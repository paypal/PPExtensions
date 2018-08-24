"""Copyright (c) 2018, PayPal Inc.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the <organization> nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

"""Utils supporting PPMagics."""

import ast
import datetime
import getpass
import os
import re
import pandas as pd
import astor

from autovizwidget.widget.utils import display_dataframe


def renew_kerberos_ticket(principal, keytab):
    """
        Check for existing Kerberos ticket.
    """
    return os.system("kinit -kt %s %s" % (keytab, principal)) == 0


def parse_run_str(run_str):
    """
        Parser to support run and run pipeline magics.
        :return Run notebook filename, Save notebook filename and key value parameters.
    """
    notebook_filename = None
    notebook_save_filename = None
    params = None

    def append_notebook_ext(file_name):
        _, ext = os.path.splitext(file_name)
        if ext == '':
            file_name = file_name + '.ipynb'
        return file_name

    save_nb_idx = run_str.find(':')
    param_start_idx = run_str.find('=')

    if (save_nb_idx != -1 and save_nb_idx < param_start_idx) or (save_nb_idx != -1 and param_start_idx == -1):
        notebook_filename = run_str[:save_nb_idx]
        notebook_filename = append_notebook_ext(notebook_filename)
        rest = run_str[save_nb_idx + 1:]
    else:
        rest = run_str

    args = list(re.finditer(" [\w]+=", rest))
    num_total_args = len(args)

    if num_total_args == 0:
        if not notebook_filename:
            notebook_filename = rest
            notebook_filename = append_notebook_ext(notebook_filename)
        else:
            notebook_save_filename = rest
            notebook_save_filename = append_notebook_ext(notebook_save_filename)
        return notebook_filename, notebook_save_filename, params

    params = dict()

    if notebook_filename:
        notebook_save_filename = rest[:args[0].start()]
        notebook_save_filename = append_notebook_ext(notebook_save_filename)
    else:
        notebook_filename = rest[:args[0].start()]
        notebook_filename = append_notebook_ext(notebook_filename)

    for arg_idx in range(num_total_args - 1):
        this_arg = args[arg_idx]
        next_arg = args[arg_idx + 1]
        arg = rest[this_arg.start() + 1: this_arg.end() - 1]
        value = rest[this_arg.end(): next_arg.start()]
        params[arg] = arg + '=' + value

    last_arg = rest[args[-1].start() + 1:args[-1].end() - 1]
    last_value = rest[args[-1].end():]
    params[last_arg] = last_arg + '=' + last_value

    return notebook_filename, notebook_save_filename, params


def substitute_params(param_cell_src, params):
    """
        Updates parameters of parameterized notebooks. Supports run and run pipeline magics.
        :return updated code cell.
    """
    param_cell_ast = ast.parse(param_cell_src)
    param_cell_ast_nodes = param_cell_ast.body
    original_params_dict = dict()
    updated_param_cell_src = ''

    def check_ast_node(ast_node):
        ret_val = False
        if isinstance(ast_node, ast.NameConstant) and ast_node.value in (True, False):
            ret_val = True
        elif isinstance(ast_node, (ast.Dict, ast.List, ast.Str, ast.Num)):
            ret_val = True
        elif isinstance(ast_node, ast.Dict):
            ret_val = True
        return ret_val

    for node in param_cell_ast_nodes:

        if not isinstance(node, ast.Assign):
            raise AttributeError("Parameters cell should only contain assignments.")

        node_value = node.value
        if not check_ast_node(node_value):
            raise AttributeError("Parameters cell can contain Strings, Numbers, Bools, Lists and Dicts.")

        param_name = node.targets[0].id
        original_params_dict[param_name] = node

    for param, value in params.items():
        if param in original_params_dict:
            new_param_node = ast.parse(value)
            new_param_node = new_param_node.body[0]

            if not isinstance(new_param_node, ast.Assign):
                raise AttributeError("Parameters should be assignments.")

            new_param_node_value = new_param_node.value
            if not check_ast_node(new_param_node_value):
                raise AttributeError("Parameters cell can contain Strings, Numbers, Bools, Lists and Dicts.")

            if isinstance(new_param_node_value, type(original_params_dict[param].value)):
                original_params_dict[param] = new_param_node
            else:
                raise AttributeError("Parameter Type Mismatch.")

    for _, value in original_params_dict.items():
        updated_param_cell_src = updated_param_cell_src + astor.to_source(value)

    return updated_param_cell_src


def csv_to_df(user_ns, args):
    """
        Converts CSCV to DataFrame.
        :return DataFrame
    """
    if args.get("csv"):
        csv_args = args.get("csv")
        df_name = pd.read_csv(csv_args, index_col=0)
    if args.get("dataframe"):
        df_name = user_ns[args.get('dataframe')]
    return df_name


def df_to_csv(user_ns, args):
    """
        Converts DataFrame to CSV.
        :return CSV
    """
    if args.get("csv"):
        data_file = args.get("csv")
    if args.get("dataframe"):
        data_file = "/home/%s/data-%s.csv" % (getpass.getuser(),
                                              str(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')))
        df_name = user_ns[args.get('dataframe')]
        df_name.to_csv(data_file, index=False)
    return data_file


def register_autoviz_code(result):
    """
        Enables AutoViz.
    """
    ip = get_ipython()
    ip.display_formatter.ipython_display_formatter.for_type_by_name(
        'pandas.core.frame', 'DataFrame', display_dataframe)
    return result.DataFrame()
