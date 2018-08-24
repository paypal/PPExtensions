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

# -*- coding: UTF-8 -*-

"""Code for all the magics and pp extensions present in the main file"""

import concurrent.futures

from enum import Enum

import ipywidgets as widgets
import nbformat

from IPython.core.display import display, HTML
from IPython.core.magic import Magics, magics_class, cell_magic, line_magic, needs_local_scope
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
from IPython.display import display_javascript


from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors import CellExecutionError
from jupyter_client.manager import start_new_kernel

from ppextensions.ppsql import HiveConnection, TeradataConnection, PrestoConnection, CSVConnection
from ppextensions.pputils import ParameterArgs, wrap_exceptions, publish
from ppextensions.pputils.utils import utils
from ppextensions.pputils.widgets.widgets import QGridCustomWidget, HorizontalBox, VerticalBox, TabView
from ppextensions.pputils.widgets.messages import UserMessages

try:
    from traitlets.config.configurable import Configurable
    from traitlets import Bool, Int

except ImportError:
    from IPython.config.configurable import Configurable
    from IPython.utils.traitlets import Bool, Int


class ConnectionType(Enum):
    """Define ENUMS for connection types.
    """
    TERADATA = "teradata"
    HIVE = "hive"
    STS = "sts"
    PRESTO = "presto"
    CSV = "csv"


@magics_class
class PPMagics(Magics, Configurable):
    """Has All magics to connect to different storage engines and clusters.
    """
    autolimit = Int(10000, config=True, help="Automatically limit the size "
                                             "of the returned result sets")
    displaylimit = Int(1000, config=True,
                       help="Automatically limit the number of rows "
                            "displayed (full result set is still stored)")
    progress_bar = Bool(True, config=True, help="Shows sql execution status "
                                                "with progress bar if "
                                                "available.")
    enable_download = Bool(False, config=True, help="Enables download option")
    qgrid = Bool(False, config=True, help="Enables QGrid formatted output")
    autoviz = Bool(False, config=True, help="Enable AutoViz formatted output")

    def __init__(self, shell):
        Configurable.__init__(self, config=shell.config)
        Magics.__init__(self, shell=shell)
        # Add ourself to the list of module configurable via %config
        self.shell.configurables.append(self)
        self.connections = {}

    def _get_connection_(self, conn_type, cluster=None, host=None, port=None, auth=None, resource_manager=None):
        if conn_type is ConnectionType.HIVE or conn_type is ConnectionType.STS:
            if conn_type not in self.connections:
                self.connections[conn_type] = HiveConnection(cluster, host, port, auth, resource_manager, conn_type is ConnectionType.STS)
        elif conn_type is ConnectionType.TERADATA:
            if conn_type not in self.connections:
                self.connections[conn_type] = TeradataConnection(cluster, host)
        elif conn_type is ConnectionType.PRESTO:
            if conn_type not in self.connections:
                self.connections[conn_type] = PrestoConnection(cluster, host, port, auth)
        elif conn_type is ConnectionType.CSV:
            if conn_type not in self.connections:
                self.connections[conn_type] = CSVConnection()
        return self.connections[conn_type]

    @needs_local_scope
    @magic_arguments()
    @cell_magic
    @line_magic
    @argument("-c", "--cluster_name", type=str, help="Cluster Name to connect to ")
    @argument("-hs", "--hive_server", type=str, help="Hive server2 host name or ip address.")
    @argument("-p", "--port", type=int, help="Hive Server2 port")
    @argument("-nn", "--name_node_url", type=str, help="Name node host name")
    @argument("-np", "--name_node_options", type=dict, help="Parameters for host")
    @argument("-rm", "--resource_manager_url", type=str, help="Resource Manager web ui url")
    @argument("-a", "--auth", type=str, default="plain", help="Authentication type")
    @argument("-f", "--csv", type=str, help="Local CSV file name to be loaded "
                                            "to hive table. Use this option "
                                            "along with --table")
    @argument("-t", "--table", type=str, help="Hive table name for data to "
                                              "be inserted to. Use this "
                                              "option along with --csv")
    @argument("-df", "--dataframe", type=str, help="DataFrame to be uploaded "
              "to a table. Use this option with --table")
    @argument("-tab", "--tableau", type=bool, default=False,
              help="True to download tableau data")
    @argument("-pub", "--publish", type=bool, default=False,
              help="Publish Data to Tableau Server")
    @argument("-tde", "--tde_name", type=str, help="tde Name to be published")
    @argument("-pname", "--project_name", type=str, help="project name to be "
              "published")
    @wrap_exceptions
    def hive(self, arg, line='', cell='', local_ns=None):
        """Connects to hive execution engine and executes the query.

        Example2:
            %%hive --hive_server hive.server.com --port 10000 --auth gssapi
            select * from database.table_name limit 10

            # To query data from hive
            %%hive
            select * from database.table_name limit 10

            # To insert csv data to a table
            %hive -f file.csv -t database.table_name

        """
        # save globals and locals so they can be referenced in bind vars
        if not (line or cell):
            if not arg.startswith("-"):
                line = arg
                arg = ''
        args = ParameterArgs(parse_argstring(self.hive, arg))
        user_ns = self.shell.user_ns.copy()
        if local_ns:
            user_ns.update(local_ns)

        if not cell:
            cell = line

        if args.get("table") and (args.get("csv") or args.get("dataframe")):
            csv = utils.df_to_csv(user_ns, args)
            df_flag = False
            if args.get("dataframe"):
                df_flag = True

            return self._get_connection_(ConnectionType.HIVE, cluster=args.get("cluster_name"),
                                         host=args.get("hive_server"), port=args.get("port"),
                                         auth=args.get("auth")).insert_csv(args.get("table"),
                                                                           args.get("name_node_url"),
                                                                           args.get("name_node_options"),
                                                                           csv, df_flag, self.autolimit, self.displaylimit)

        result_set = self._get_connection_(ConnectionType.HIVE, cluster=args.get("cluster_name"),
                                           host=args.get("hive_server"), port=args.get("port"),
                                           auth=args.get("auth"),
                                           resource_manager=args.get("resource_manager_url")).\
            execute(cell, self.autolimit, self.displaylimit, self.progress_bar)

        return self._process_results_(result_set, args.get('tableau'), args.get('publish'), args.get('tde_name'), args.get('project_name'))

    @needs_local_scope
    @magic_arguments()
    @line_magic
    @cell_magic
    @argument("-c", "--cluster_name", type=str, help="Cluster Name to connect to ")
    @argument("-f", "--csv", type=str, help="Local CSV file name to be loaded "
                                            "to hive table. Use this option "
                                            "along with --table")
    @argument("-t", "--table", type=str, help="Teradata table name for data to "
                                              "be inserted to. Use this "
                                              "option along with --csv")
    @argument("-df", "--dataframe", type=str, help="DataFrame to be uploaded "
              "to a table. Use this option with --table")
    @argument("-h", "--host", type=str, help="Teradata host name to connect to")
    @argument("-tab", "--tableau", type=bool, default=False,
              help="True to download tableau data")
    @argument("-pub", "--publish", type=bool, default=False,
              help="Publish Data to Tableau Server")
    @argument("-tde", "--tde_name", type=str, help="tde Name to be published")
    @argument("-pname", "--project_name", type=str, help="project name to be "
              "published")
    @wrap_exceptions
    def teradata(self, arg, line='', cell='', local_ns=None):
        """Connects to teradata system and executes the query.

        Example2:

            # To download data
            %%teradata --host
            select * from database.table_name sample 10

            # To insert csv data to a table
            %teradata -f dim_cust.csv -t pp_scratch.dim_cust

        """
        # save globals and locals so they can be referenced in bind vars
        if not (line or cell):
            if not arg.startswith("-"):
                line = arg
                arg = ''
        args = ParameterArgs(parse_argstring(self.teradata, arg))
        user_ns = self.shell.user_ns.copy()
        if local_ns:
            user_ns.update(local_ns)

        if not cell:
            cell = line

        if args.get("table") and (args.get("csv") or args.get("dataframe")):
            data_frame = utils.csv_to_df(user_ns, args)

            return self._get_connection_(ConnectionType.TERADATA, args.get("cluster_name"), args.get("host")).insert_csv(
                args.get("table"), data_frame, self.autolimit, self.displaylimit)

        result_set = self._get_connection_(ConnectionType.TERADATA, args.get("cluster_name"), args.get("host")).execute(
            cell, self.autolimit, self.displaylimit, self.progress_bar)

        return self._process_results_(result_set, args.get('tableau'), args.get('publish'), args.get('tde_name'), args.get('project_name'))

    @needs_local_scope
    @magic_arguments()
    @line_magic
    @cell_magic
    @argument("-c", "--cluster_name", type=str, help="Cluster Name to connect to ")
    @argument("-h", "--host", type=str, help="Host name or ip address of presto server")
    @argument("-p", "--port", type=str, help="Port of presto server")
    @argument("-a", "--auth", type=str, default="plain", help="Authentication type")
    @argument("-tab", "--tableau", type=bool, default=False,
              help="True to download tableau data")
    @argument("-pub", "--publish", type=bool, default=False,
              help="Publish Data to Tableau Server")
    @argument("-tde", "--tde_name", type=str, help="tde Name to be published")
    @argument("-pname", "--project_name", type=str, help="project name to be "
              "published")
    @wrap_exceptions
    def presto(self, arg, line='', cell='', local_ns=None):
        """Connects to presto execution engine for query execution.

        Example2:
            %presto select * from cluster.default.dim_cust limit 10

            # To download data
            %%presto -d True
            select * from cluster.default.dim_cust limit 10

        """
        # save globals and locals so they can be referenced in bind vars
        if not (line or cell):
            if not arg.startswith("-"):
                line = arg
                arg = ''
        args = ParameterArgs(parse_argstring(self.presto, arg))
        user_ns = self.shell.user_ns.copy()
        if local_ns:
            user_ns.update(local_ns)
        if not cell:
            cell = line

        result_set = self._get_connection_(ConnectionType.PRESTO, args.get("cluster_name"), args.get("host"), args.get("port"), args.get("auth")).execute(
            cell, self.autolimit, self.displaylimit, self.progress_bar)

        return self._process_results_(result_set, args.get('tableau'), args.get('publish'), args.get('tde_name'), args.get('project_name'))

    @line_magic('help')
    def help(self, arg, line='', cell='', local_ns=None):
        return display(HTML(PPMagics._help_html_str_()))

    @staticmethod
    def _help_html_str_():
        help_html = u"""
        <table>
          <tr>
            <th>Magic</th>
            <th>Usage</th>
            <th>Explanation</th>
          </tr>
          <tr>
            <td>hive</td>
            <td>%hive?</td>
            <td>Connects to hive engine. Hive magic also gives options to insert csv/dataframe to teradata and publishing data to tableau.</td>
          </tr>
          <tr>
            <td>teradata</td>
            <td>%teradata?</td>
            <td>Connects to teradata engine. Teradata magic also gives has to insert csv/dataframe to teradata and publishing data to tableau.</td>
          </tr>
          <tr>
            <td>presto</td>
            <td>%presto?</td>
            <td>Connects to presto engine. Presto magic also has options to publishing data to tableau.</td>
          </tr>
          <tr>
            <td>Spark Thrift Server</td>
            <td>%sts?</td>
            <td>Connects to Spark Thrift Server. Sts magic also has options to publishing data to tableau.</td>
          </tr>
          <tr>
            <td>CSV</td>
            <td>%csv?</td>
            <td>Runs sqls on top of csv files. CSV magic also has options to publishing data to tableau.</td>
          </tr>
          <tr>
            <td>run</td>
            <td>%run?</td>
            <td>Runs a notebook from another notebook. Allows for running parameterized notebooks.</td>
          </tr>
          <tr>
            <td>run_pipeline</td>
            <td>%run_pipeline?</td>
            <td>Run notebooks sequentially in a pipeline</td>
          </tr>
        </table>
        """
        return help_html

    @needs_local_scope
    @magic_arguments()
    @line_magic
    @cell_magic
    @argument("-tab", "--tableau", type=bool, default=False,
              help="True to download tableau data")
    @argument("-pub", "--publish", type=bool, default=False,
              help="Publish Data to Tableau Server")
    @argument("-tde", "--tde_name", type=str, help="tde Name to be published")
    @argument("-pname", "--project_name", type=str, help="project name to be "
              "published")
    @wrap_exceptions
    def csv(self, arg, line='', cell='', local_ns=None):
        # save globals and locals so they can be referenced in bind vars
        """CSV Magic
        Accepted Query formats: All select sql statements: select * from filename.csv/tsv
        return: Dataframe

        Example Queries:
        1. select * from test.csv
        2. select col1 from test.csv where col1=1
        3.select * from test.tsv

        Note: Currently csv magic supports only select sqls
        """
        if not (line or cell):
            if not arg.startswith("-"):
                line = arg
                arg = ''
        args = ParameterArgs(parse_argstring(self.csv, arg))
        user_ns = self.shell.user_ns.copy()
        if local_ns:
            user_ns.update(local_ns)
        if not cell:
            cell = line

        result_set = self._get_connection_(ConnectionType.CSV, '').execute(cell)
        return self._process_results_(result_set, args.get('tableau'), args.get('publish'), args.get('tde_name'), args.get('project_name'))

    @needs_local_scope
    @magic_arguments()
    @line_magic
    @cell_magic
    @argument("-c", "--cluster_name", type=str, help="Cluster Name to connect to ")
    @argument("-h", "--host", type=str, default="plain", help="Host name or ip address of spark thrift server")
    @argument("-p", "--port", type=int, help="Port address of spark thrift server")
    @argument("-a", "--auth", type=str, help="Authentication type")
    @argument("-tab", "--tableau", type=bool, default=False,
              help="True to download tableau data")
    @argument("-pub", "--publish", type=bool, default=False,
              help="Publish Data to Tableau Server")
    @argument("-tde", "--tde_name", type=str, help="tde Name to be published")
    @argument("-pname", "--project_name", type=str, help="project name to be "
              "published")
    @wrap_exceptions
    def sts(self, arg, line='', cell='', local_ns=None):
        """Connects to spark thrift server and executes the query

        Example2:
            # To initialize spark thrift server connection.
            %%sts -h 127.0.0.1 -p 1000
            select * form dim_cust limit 10

        """
        # save globals and locals so they can be referenced in bind vars
        if not (line or cell):
            if not arg.startswith("-"):
                line = arg
                arg = ''
        args = ParameterArgs(parse_argstring(self.sts, arg))
        user_ns = self.shell.user_ns.copy()
        if local_ns:
            user_ns.update(local_ns)

        if not cell:
            cell = line

        result_set = self._get_connection_(ConnectionType.STS, cluster=args.get("cluster_name"), host=args.get("host"), port=args.get("port"), auth=args.get("auth")).execute(
            cell, self.autolimit, self.displaylimit, self.progress_bar)

        return self._process_results_(result_set, args.get('tableau'), args.get('publish'), args.get('tde_name'), args.get('project_name'))

    @needs_local_scope
    @magic_arguments()
    @line_magic
    @argument("-p", "--principal", type=str, default=False, help="Principal to renew kerberos ticket")
    @argument("-k", "--keytab", type=str, help="Keytab path to renew kerberos ticket")
    @wrap_exceptions
    def keytab(self, arg):
        """
        Look for Kerberos Ticket.
        """
        args = ParameterArgs(parse_argstring(self.url, arg))
        if not utils.renew_kerberos_ticket(args.get("principal"), args.get("keytab")):
            raise Exception("Unable to renew kerberos ticket")

    @needs_local_scope
    @magic_arguments()
    @line_magic
    @cell_magic
    @argument("-tde", "--tde_name", type=str, help="tde Name to be published")
    @argument("-p_name", "--project_name", type=str, help="tde Name to be published")
    @wrap_exceptions
    def publish(self, arg, line='', cell='', local_ns=None):
        """
            Publish to Tableau.
        """
        if not (line or cell):
            if not arg.startswith("-"):
                line = arg
                arg = ''
        args = ParameterArgs(parse_argstring(self.publish, arg))
        user_ns = self.shell.user_ns.copy()
        if local_ns:
            user_ns.update(local_ns)

        if not cell:
            cell = line
            if cell.startswith('%%'):
                magic = cell.split(" ", 1)[0].lstrip('%')
                arg = cell.split(" ", 1)[1].split("\n", 1)[0]
                query = cell.split(" ", 1)[1].split("\n", 1)[1]
                result = get_ipython().run_cell_magic(magic, arg, query)
                return publish(result, args.get('tde_name'), args.get('project_name'))
            elif cell.startswith('%'):
                magic = cell.split(" ", 1)[0].lstrip('%')
                query = cell.split(" ", 1)[1]
                result = get_ipython().run_line_magic(magic, query)
                return publish(result, args.get('tde_name'), args.get('project_name'))
        df_name = user_ns[cell]
        return publish(df_name, args.get('tde_name'), args.get('project_name'))

    @needs_local_scope
    @magic_arguments()
    @line_magic
    @cell_magic
    @argument("-p", "--parallel", type=bool, default=False, help="Run Notebooks in Parallel")
    @argument("-e", "--allow_errors", type=bool, default=False, help="Ignore errors and execute whole notebook")
    @argument("-pbar", "--enable_progress_bar", type=bool, default=False, help="Show Progress Bar")
    @argument("-t", "--cell_timeout", type=int, default=300, help="Cell Execution Timeout. -1 to Disable.")
    @wrap_exceptions
    def run(self, arg, line='', cell='', local_ns=None):
        """Runs a notebook from another notebook. Allows for running parameterized notebooks. If using parameters
           the first codecell will be treated to contain only parameter assignments. Parameters can be strings, numbers,
           lists or dictionaries. The magic can enable sequential or parallel execution of notebooks.

           To save a notebook's execution, the save name should be specified along with the execution notebook
           separated with a colon.

           Run parameters will only change their equivalent parameters from the first code cell. Unknown parameters will
           be ignored. Adding parameters on an execution is optional.

                # simple run
                Example1:
                    %run your notebook

                # simple sequential run
                Example1:
                    %%run
                    your notebook 01;
                    your notebook 02

                # simple run allow errors
                Example1:
                    %%run -e True
                    your notebook

                # simple run show progress bar
                Example1:
                    %%run -pbar True
                    your notebook

                # simple run show progress bar and save execution
                Example1:
                    %%run -pbar True
                    your notebook:your save notebook

                # simple run in parallel with progressbar
                Example1:
                    %%run -pbar True -p True
                    your notebook 01;
                    your notebook 02

                # simple run in parallel with progressbar and disabling cell timeout
                Example1:
                    %%run -pbar True -t -1
                    your notebook 01;
                    your notebook 02

                # parameterized run in parallel with progressbar
                Example1:
                    %%run -pbar True -p True
                    your notebook 01  key01=int key01=string key02={'key01': param01};
                    your notebook 02:your save name key01=int key02=string key03=[param01, param02]

        """
        # save globals and locals so they can be referenced in bind vars
        if not (line or cell):
            if not arg.startswith("-"):
                line = arg
                arg = ''

        args = ParameterArgs(parse_argstring(self.run, arg))
        user_ns = self.shell.user_ns.copy()
        if local_ns:
            user_ns.update(local_ns)

        if not cell:
            cell = line

        notebook_run_cmds = cell.split(';')
        notebook_run_cmds = [notebook_run_cmd.strip() for notebook_run_cmd in notebook_run_cmds]

        def execute_notebook(notebook_filename, notebook_save_filename, params):
            log = UserMessages()

            with open(notebook_filename) as file_handler:
                notebook = nbformat.read(file_handler, as_version=4)
                b_errors = False
                execute_preprocessor = ExecutePreprocessor(timeout=args.get('cell_timeout'), allow_errors=args.get('allow_errors'))
                kernel_manager = None
                kernel_comm = None
                progress_bar = args.get('enable_progress_bar')

                if params:
                    for nb_cell in notebook.cells:
                        if nb_cell.cell_type == 'code':
                            new_cell_source = utils.substitute_params(nb_cell.source, params)
                            nb_cell.source = new_cell_source
                            break

                try:
                    if progress_bar:

                        progress_bar = widgets.IntProgress(
                            value=0,
                            min=0,
                            max=len(notebook.cells),
                            step=1,
                            bar_style='info',  # 'success', 'info', 'warning', 'danger' or ''
                            orientation='horizontal'
                        )

                        kernel_manager, kernel_comm = start_new_kernel(kernel_name=notebook['metadata']['kernelspec']['name'])
                        execute_preprocessor.km = kernel_manager
                        execute_preprocessor.kc = kernel_comm
                        execute_preprocessor.nb = notebook

                        display_label = notebook_filename
                        if notebook_save_filename:
                            display_label = display_label + ' : ' + notebook_save_filename
                        display(widgets.HBox([widgets.Label(display_label), progress_bar]))

                        for idx, nb_cell in enumerate(notebook.cells):
                            execute_preprocessor.preprocess_cell(nb_cell, resources={'metadata': {}}, cell_index=idx)
                            progress_bar.value = idx + 1
                    else:
                        log.info("Running Notebook: " + notebook_filename)
                        execute_preprocessor.preprocess(notebook, {'metadata': {}})
                except CellExecutionError:
                    b_errors = True
                    if progress_bar:
                        progress_bar.bar_style = 'danger'
                    raise
                except AttributeError:
                    b_errors = True
                    if progress_bar:
                        progress_bar.bar_style = 'danger'
                    raise
                finally:
                    if notebook_save_filename:
                        with open(notebook_save_filename, mode='wt') as file_handler:
                            nbformat.write(notebook, file_handler)

                    if kernel_manager or kernel_comm:
                        kernel_comm.stop_channels()
                        kernel_manager.shutdown_kernel()

                    if not b_errors:
                        if progress_bar:
                            progress_bar.bar_style = 'success'
                        else:
                            log.info(notebook_filename + " was executed successfully.")
                    elif b_errors and not progress_bar:
                        log.error(notebook_filename + " execution failed.")

        if args.get('parallel'):
            futures = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:

                for notebook_run_cmd in notebook_run_cmds:
                    run_notebook_name, notebook_save_name, nb_params = utils.parse_run_str(notebook_run_cmd)
                    futures.append(executor.submit(execute_notebook, run_notebook_name, notebook_save_name, nb_params))

                # Handle other notebook runs if one or more fails intermittently
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except CellExecutionError:
                        raise
        else:
            for notebook_run_cmd in notebook_run_cmds:
                run_notebook_name, notebook_save_name, nb_params = utils.parse_run_str(notebook_run_cmd)
                execute_notebook(run_notebook_name, notebook_save_name, nb_params)

    @needs_local_scope
    @magic_arguments()
    @line_magic
    @cell_magic
    @argument("-t", "--cell_timeout", type=int, default=300, help="Cell Execution Timeout. -1 to Disable.")
    @wrap_exceptions
    def run_pipeline(self, arg, line='', cell='', local_ns=None):
        """Run notebooks sequentially in a pipeline.
           A dictionary called _pipeline_workspace is created by the magic that will be shared by all the notebooks in
           the pipeline. The state can contain DataFrames, Lists, Dictionaries and objects. Notebook parameterization
           can be used to load and read from the shared state.

           The pipeline supports execution of parameterized notebooks. If parameters are used, the first code cell will
           be treated to contain only parameter assignments. Parameters can be a string, number, list or dictionary.

           To save a notebook's execution in the pipeline, the save name should be specified along with the
           execution notebook separated with a colon.

           Run parameters will only change their equivalent parameters from the first code cell. Unknown parameters will
           be ignored. Adding parameters on an execution is optional.

                # simple pipeline
                Example1:
                    %%run_pipeline
                    first notebook in pipeline;
                    second notebook in pipeline;
                    third notebook in pipeline

                # pipleine with parameterized notebooks
                Example2:
                    %%run_pipeline
                    first notebook in pipeline  key01=int key01=string key02={'key01': param01};
                    second notebook in pipeline;
                    third notebook in pipeline:your save name key01=int key02=string key03=[param01, param02]

        """
        # save globals and locals so they can be referenced in bind vars

        clear_namespace_cell = nbformat.v4.new_code_cell(
            source="from IPython import get_ipython\n" +
            "_ip = get_ipython()\n" +
            "_user_vars = %who_ls\n" +
            "for _var in _user_vars:\n" +
            "    if _var != '_pipeline_workspace':\n" +
            "        del _ip.user_ns[_var]\n" +
            "import gc\n" +
            "gc.collect()"
        )
        pipeline_state_cell = nbformat.v4.new_code_cell(source="_pipeline_workspace = {'frames': list()}")

        if not (line or cell):
            if not arg.startswith("-"):
                line = arg
                arg = ''

        args = ParameterArgs(parse_argstring(self.run, arg))

        user_ns = self.shell.user_ns.copy()
        if local_ns:
            user_ns.update(local_ns)

        if not cell:
            cell = line

        notebook_run_cmds = cell.split(';')
        notebook_run_cmds = [notebook_run_cmd.strip() for notebook_run_cmd in notebook_run_cmds]

        execute_preprocessor = ExecutePreprocessor(kernel_name='python3', timeout=args.get('cell_timeout'))

        kernel_manager, kernel_comm = start_new_kernel(kernel_name='python3')

        execute_preprocessor.km = kernel_manager
        execute_preprocessor.kc = kernel_comm

        def execute_cell(nb4_cell):
            try:
                execute_preprocessor.run_cell(nb4_cell)
            except BaseException:
                if kernel_manager or kernel_comm:
                    kernel_comm.stop_channels()
                    kernel_manager.shutdown_kernel()

        def execute_notebook(notebook_filename, notebook_save_filename, params):

            with open(notebook_filename) as file_handler:
                notebook = nbformat.read(file_handler, as_version=4)
                b_errors = False

                if params:
                    for nb_cell in notebook.cells:
                        if nb_cell.cell_type == 'code':
                            new_cell_source = utils.substitute_params(nb_cell.source, params)
                            nb_cell.source = new_cell_source
                            break

                try:

                    execute_preprocessor.nb = notebook

                    progress_bar = widgets.IntProgress(
                        value=0,
                        min=0,
                        max=len(notebook.cells),
                        step=1,
                        bar_style='info',  # 'success', 'info', 'warning', 'danger' or ''
                        orientation='horizontal'
                    )

                    display_label = notebook_filename
                    if notebook_save_filename:
                        display_label = display_label + ' : ' + notebook_save_filename
                    display(widgets.HBox([widgets.Label(display_label), progress_bar]))

                    for idx, nb_cell in enumerate(notebook.cells):
                        execute_preprocessor.preprocess_cell(nb_cell, resources={'metadata': {}}, cell_index=idx)
                        progress_bar.value = idx + 1

                except CellExecutionError:
                    b_errors = True

                    progress_bar.bar_style = 'danger'

                    if kernel_manager or kernel_comm:
                        kernel_comm.stop_channels()
                        kernel_manager.shutdown_kernel()

                    raise
                finally:
                    if notebook_save_filename:
                        with open(notebook_save_filename, mode='wt') as file_handler:
                            nbformat.write(notebook, file_handler)

                    if not b_errors:
                        progress_bar.bar_style = 'success'

        execute_cell(pipeline_state_cell)
        for notebook_run_cmd in notebook_run_cmds:

            run_notebook_name, notebook_save_name, nb_params = utils.parse_run_str(notebook_run_cmd)

            execute_notebook(run_notebook_name, notebook_save_name, nb_params)
            execute_cell(clear_namespace_cell)

        if kernel_manager or kernel_comm:
            kernel_comm.stop_channels()
            kernel_manager.shutdown_kernel()

    def _process_results_(self, results, tableau=False, publish_tab=False, tde_name=None, project_name=None):
        """
        Processes the results based on configs and returns the output to user.
        :param results:
        :return:
        """

        def create_tab(result, b_multiple):
            result_df = result.DataFrame()
            horizontal_widgets = []
            vertical_widgets = []

            if tableau and publish_tab and not b_multiple:
                publish(result, tde_name, project_name)

            # Add optional button and forms for input.
            if len(horizontal_widgets) != 0:
                vertical_widgets.append(HorizontalBox(horizontal_widgets))

            if self.qgrid or b_multiple:
                # QGrid Render
                vertical_widgets.append(QGridCustomWidget(result_df, self.displaylimit))
            elif self.autoviz:
                # AutoViz
                return utils.register_autoviz_code(result), None
            else:
                # HTML Render
                # vertical_widgets.append(widgets.HTML(result._repr_html_()))
                return result, None

            return VerticalBox(vertical_widgets, result_df), result_df

        if isinstance(results, list):
            tabs = []
            data = []
            for this_result in results:
                this_tab, this_data = create_tab(this_result, b_multiple=True)
                tabs.append(this_tab)
                data.append(this_data)
            ret_val = TabView(tabs, data)
        elif isinstance(results, list):
            tab, _ = create_tab(results, b_multiple=False)
            ret_val = tab
        else:
            if self.autoviz:
                # AutoViz
                return self._register_autoviz_code(results), None
            ret_val = results

        return ret_val


def load_ipython_extension(ip):
    """Load the PPMagics extension in IPython."""
    js = "IPython.CodeCell.options_default.highlight_modes[""'magic_text/x-sql'] = {'reg':[/^.*%%?.*/""]};"
    display_javascript(js, raw=True)
    ip.register_magics(PPMagics)
