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

"""This class enables connecting to Teradata. Implements BaseConnection."""

import collections
import datetime
import decimal
import getpass

import pandas
import sqlparse
import teradata
from IPython.display import Markdown, display
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import SqlLexer
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Number

from ppextensions.ppsql.connection.basesql import BaseConnection
from ppextensions.pputils import UserMessages, ResultSet, Log
from ppextensions.pputils.utils.configuration import conf_info


class TeradataConnection(BaseConnection):
    """
    Enables connecting to Teradata. Implements BaseConnection.
    """

    def __init__(self, cluster, host):
        self.cluster_details = conf_info('teradata')
        if cluster in self.cluster_details:
            self.cluster_details = self.cluster_details[cluster]
            host = self.cluster_details['host']
        uda_exec = teradata.UdaExec(appName="Jupyter Notebooks", version="1.0", logConsole=False)
        password = TeradataConnection._get_password_()
        connection = uda_exec.connect(method="odbc", system=host, username=getpass.getuser(), password=password.replace('$', '$$'))
        super(TeradataConnection, self).__init__(connection)

    def execute(self, sql, limit, displaylimit, progress_bar=False):
        """
            Query Teradata and return results.
        """

        log = UserMessages()

        def process_result(result, exec_statement=''):
            keys = []
            if result.description is not None and isinstance(result.description, list):
                for column in result.description:
                    keys.append(column[0])
            if limit:
                data = result.fetchmany(size=limit)
            else:
                data = result.fetchall()
            log.info("Fetched %d out of %d records" % (len(data), result.rowcount))
            return_result = ResultSet(keys, data, displaylimit)

            # Formats show query output
            if exec_statement.strip().startswith("show"):
                display_sql(return_result.data[0].values[0])
            else:
                return return_result

        if ';' in sql:
            results = []
            log.info("Executing multi-statement atomic request. "
                     "Estimated time unavailable.")
            result_set = self.connection.execute(sql)
            results.append(process_result(result_set))
            while result_set.nextset():
                results.append(process_result(result_set))
            return results
        else:
            estimated_time = ""
            if not sql.lower().startswith(('explain', 'show', 'help',
                                           'select session')):
                explain_result = self.connection.execute("explain %s" % sql)
                for row in explain_result:
                    if 'estimated time is' in str(row):
                        estimated_time = str(row).split("estimated time is",
                                                        1)[1].strip(".]")
            if estimated_time:
                log.info("Executing %s. Estimated time taken by query to "
                         "complete will be %s" % (sql, estimated_time))
            else:
                log.info("Executing %s" % sql)

            result_set = process_result(
                self.connection.execute("%s" % sql),
                exec_statement=sql
            )
            return result_set

    def insert_csv(self, table_name, df_name, autolimit, displaylimit):
        """
            Function to insert dataframe or csv to Teradata.
        """
        df_name = df_name.reindex_axis(sorted(df_name.columns), axis=1)
        df_name.columns = df_name.columns.astype(str)

        # Get the corresponding teradata data types for all dataframe columns
        data_dict = TeradataConnection.df_datatype(df_name)
        data_type_list = ',\n'.join(
            ['%s %s' % (key, value) for (key, value) in data_dict.items()])

        # Create Table command for creating a new table
        create_table_command = "CREATE TABLE {} ({})" \
            .format(table_name, data_type_list)

        # Insert Value  command for inserting records into table
        insert_command = TeradataConnection.create_insert_command(df_name, table_name, data_dict)

        try:
            self.execute(create_table_command, autolimit, displaylimit)
        except teradata.api.DatabaseError as err:
            table_args = table_name.split(".", 1)
            if len(table_args) > 1:
                table_name = table_args[1]
            else:
                table_name = table_args[0]
            if "Table '%s' already exists" % table_name in str(err):
                pass
            else:
                raise
        return self.execute(insert_command, autolimit, displaylimit)

    @staticmethod
    def df_datatype(df_name):
        """
            Function to get the corresponding teradata data types for all dataframe columns
        """
        log = Log('', filename='/tmp/logs/teradataconnection.log')
        data_type = []
        fieldnames = []
        data_type_map = {int: "int",
                         str: "varchar(1000)",
                         bytearray: "byte(1200)",
                         float: "float",
                         decimal.Decimal: "decimal",
                         datetime.date: "DATE",
                         datetime.time: "Time",
                         datetime.datetime: "TIMESTAMP",
                         pandas.Timestamp: "TIMESTAMP",
                         pandas.NaT: "TIMESTAMP"
                         }
        for col in df_name:
            col_name = col.split('.')
            if col_name:
                col_name = col_name[1] if len(col_name) > 1 else col_name[0]
            fieldnames.append(col_name)
            data_type.append(df_name[col].apply(type).iat[0])
        data_dict = dict(zip(fieldnames, data_type))

        for col_name in data_dict:
            if data_dict[col_name] in data_type_map:
                data_dict[col_name] = data_type_map[data_dict[col_name]]
            else:
                log.info("For %s data type is %s,  while inserting dataframe to Teradata" % (col_name, data_dict[col_name]))
                data_dict[col_name] = "varchar(1000)"

        data_dict = collections.OrderedDict(sorted(data_dict.items()))
        return data_dict

    @staticmethod
    def create_insert_command(df_name, table_name, data_dict):
        """
            Function to create insert command for all the dataframe/csv values.
        """
        value_list = []
        for _, row in df_name.iterrows():
            row_value = []
            for col in df_name:
                col_name = col.split('.')
                if col_name:
                    col_name = col_name[1] if len(col_name) > 1 else col_name[0]
                if pandas.isnull(row[col]):
                    row_value.append('Null')
                elif data_dict[col_name] == "float" or data_dict[
                        col_name] == "int" or data_dict[col_name] == "decimal":
                    row_value.append(str(row[col]))
                else:
                    row_value.append("'" + str(row[col]) + "'")
            row_value = tuple(row_value)
            value_list.append(row_value)
        value_list = tuple(value_list)
        insert_statement = '\n;insert into %s values' % table_name
        insert_value = "insert into %s values" % table_name + \
                       insert_statement.join("(%s)" % ",".join(str(i)
                                                               for i in row) for row in value_list)
        return insert_value

    @staticmethod
    def _get_password_():
        """
            Get Password user authentication.
        """
        print("Please enter your password:")
        return getpass.getpass()


class YourStyle(Style):
    """
        Styling for show queries.
    """
    default_style = ""
    styles = {
        Comment: 'italic #000000',
        Number: '#ff00ff',
        Keyword: 'bold #0000ff',
        Name: '#660000',
        Name.Function: '#0f0',
        Name.Class: '#0f0',
        String: 'bg:#f7f4f4'
    }


def display_sql(sql_code):
    """
        Formatting for show queries.
    """
    formatted_sql_code = sqlparse.format(
        sql_code,
        reindent=False,
        keyword_case='upper',
        identifier_case='upper')
    highlighted_formatted_sql_code = highlight(
        formatted_sql_code,
        SqlLexer(),
        HtmlFormatter(noclasses=True, style=YourStyle))
    display(Markdown(highlighted_formatted_sql_code))
