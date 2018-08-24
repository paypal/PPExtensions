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

"""Manage Tableau Publish."""

import datetime
import decimal
import getpass
import glob
import os
import re
import subprocess

import pandas as pd
from IPython.core.display import display, HTML
from paramiko.ssh_exception import SSHException
from pysftp.exceptions import ConnectionException
from tableausdk import *
from tableausdk.Extract import *

from ppextensions.pputils.utils.configuration import conf_info
from .resultset import ResultSet


def tableau_extract(resultset, data_file):
    """
    Create TDE extract.
    """
    if isinstance(resultset, ResultSet):
        df_name = resultset.DataFrame()
    else:
        df_name = resultset
    data_type = []
    fieldnames = []
    data_type_map = {int: Type.INTEGER,
                     str: Type.UNICODE_STRING,
                     bool: Type.BOOLEAN,
                     bytearray: Type.CHAR_STRING,
                     list: Type.CHAR_STRING,
                     dict: Type.CHAR_STRING,
                     float: Type.DOUBLE,
                     decimal.Decimal: Type.DOUBLE,
                     datetime.date: Type.DATE,
                     datetime.time: Type.DURATION,
                     datetime.datetime: Type.DATETIME,
                     pd._libs.tslib.Timestamp: Type.DATETIME
                     }

    for col in df_name:
        fieldnames.append(col)
        data_type.append(df_name[col].apply(type).iat[0])
    data_dict = dict(zip(fieldnames, data_type))

    for col_name in data_dict:
        if data_dict[col_name] in data_type_map:
            data_dict[col_name] = data_type_map[data_dict[col_name]]
        else:
            data_dict[col_name] = Type.UNICODE_STRING
    # Initialize a new extract
    try:
        os.remove(data_file)
    except OSError:
        pass
    new_extract = Extract(data_file)
    table_definition = TableDefinition()
    for col_name in data_dict:
        table_definition.addColumn(col_name, data_dict[col_name])
    new_table = new_extract.addTable('Extract', table_definition)
    new_row = Row(table_definition)
    tde_types = {'INTEGER': 7, 'DOUBLE': 10, 'BOOLEAN': 11, 'DATE': 12,
                 'DATETIME': 13, 'DURATION': 14,
                 'CHAR_STRING': 15, 'UNICODE_STRING': 16}
    for i in range(0, len(df_name)):
        for col in range(0, table_definition.getColumnCount()):
            col_name = table_definition.getColumnName(col)
            try:
                if data_dict[col_name] == tde_types['INTEGER']:
                    new_row.setInteger(col, int(df_name[col_name][i]))
                elif data_dict[col_name] == tde_types['DOUBLE']:
                    new_row.setDouble(col, float(df_name[col_name][i]))
                elif data_dict[col_name] == tde_types['BOOLEAN']:
                    new_row.setBoolean(col, bool(df_name[col_name][i]))
                elif data_dict[col_name] == tde_types['DATE']:
                    data = df_name[col_name][i]
                    new_row.setDate(col, data.year, data.month, data.day)
                elif data_dict[col_name] == tde_types['DATETIME']:
                    data = df_name[col_name][i]
                    new_row.setDateTime(col, data.year, data.month, data.day,
                                        data.hour, data.minute, data.second, 0)
                elif data_dict[col_name] == tde_types['DURATION']:
                    data = df_name[col_name][i]
                    new_row.setDuration(col, data.hour, data.minute, data.second, 0)
                elif data_dict[col_name] == tde_types['CHAR_STRING']:
                    new_row.setCharString(col, str(df_name[col_name][i]))
                elif data_dict[col_name] == tde_types['UNICODE_STRING']:
                    new_row.setString(col, str(df_name[col_name][i]))
                else:
                    print('Error')
                    new_row.setNull(col)
            except TypeError:
                new_row.setNull(col)
        new_table.insert(new_row)

    new_extract.close()
    ExtractAPI.cleanup()
    for file_name in glob.glob("DataExtract*.log"):
        os.remove(file_name)


def publish(data, data_file=None, project_name=None):
    """
    Publish to Tableau.
    """
    overwrite = False
    if not data_file:
        data_file = ("data-%s.tde" % (str(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')))).strip()

    else:
        data_file = re.sub(r"\.tde$", "", data_file)
        data_file = getpass.getuser() + '-' + data_file + '.tde'

    tableau_details = conf_info('tableau')

    if tableau_details:
        site_name = tableau_details['site_name']
        username = tableau_details['user_name']
        password = tableau_details['password']
    else:
        site_name = input("Enter the site name to publish ")
        username = input("Enter tableau user name ")
        password = getpass.getpass("Please enter your password ")

    try:
        if project_name:
            project_name = project_name.strip('\'"')

        else:
            project_name = 'default'

        tableau_extract(data, data_file)
        data_file_name = str(data_file).rsplit('.tde', 1)[0]

        subprocess.run(["tabcmd", "--accepteula"], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)

        result = subprocess.run(["tabcmd", "login", "-s",
                                 "{}".format(site_name), "-u", "{}".format(username),
                                 "-p", "{}".format(password)], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        if result.returncode != 0:
            raise ConnectionException("Unable to connect to tableau server")

        result = subprocess.run(["tabcmd", "publish",
                                 "{}".format(data_file),
                                 "-r", "{}".format(project_name)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            if ("A data source named '{}' already exists in project".format(
                    data_file_name) in str(result.stderr)):
                result = subprocess.run(
                    ["tabcmd", "publish", "{}".format(data_file),
                     "-r", "{}".format(project_name), "--overwrite"], stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
                overwrite = True
            if "Unexpected response from the server:" not in str(result.stderr):
                print(result.stderr)
                raise SSHException("Unable to get response from tableau server")

    finally:
        os.system("rm %s" % data_file)

    if overwrite:
        link_t = "<a href='{href}' target='_blank'>Click here to access " \
                 "Tableau published data</a>"
        result_file = "{}/datasources/{}".format(site_name, data_file_name)
    else:
        link_t = "<a href='{href}' target='_blank'>Click here to access " \
                 "Tableau published data</a>"
        result_file = "{}/authoringNewWorkbook/{}".format(site_name,
                                                          data_file_name)

    html = HTML(link_t.format(href=result_file))
    display(html)
