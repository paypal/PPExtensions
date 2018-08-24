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

"""This class enables connecting to Hive2Servers. Implements BaseConnection."""

import csv
import getpass
import os
import re
import time
from collections import OrderedDict

import sqlparse
from hdfs3 import HDFileSystem
from impala.dbapi import connect

from ppextensions.ppsql.connection.basesql import BaseConnection
from ppextensions.pputils import UserMessages, ResultSet
from ppextensions.pputils.utils.configuration import conf_info
from ppextensions.pputils.utils.yarnapi import ResourceManager
from ppextensions.pputils.widgets.widgets import StatusBar


class HiveConnection(BaseConnection):
    """
    Enables connecting to Hive2Servers. Implements BaseConnection.
    """

    def __init__(self, cluster, host, port, auth, rm_url, sts=False):
        self.sts = sts
        self.application_id = None
        self.resource_manager = None
        self.host = host
        self.port = port
        self.auth = auth
        self.cursor = None
        if self.sts:
            self.cluster_details = conf_info('sts')
        else:
            self.cluster_details = conf_info('hive')
        if cluster in self.cluster_details:
            self.cluster_details = self.cluster_details[cluster]
            self.host = self.cluster_details['host']
            self.port = self.cluster_details['port']
            self.auth = self.cluster_details['auth']
            if 'resource_manager_url' in self.cluster_details:
                rm_url = self.cluster_details['resource_manager_url']

        if rm_url:
            self.resource_manager = ResourceManager(rm_url)

        super(HiveConnection, self).__init__(self._init_connection_())

    def _init_connection_(self):

        if hasattr(self, 'connection') and self.connection:
            return

        if self.auth.upper() == 'GSSAPI':
            HiveConnection._authecticate_()
            connection = connect(host=self.host,
                                 port=self.port,
                                 auth_mechanism='GSSAPI',
                                 kerberos_service_name='hive')
            self.cursor = connection.cursor()
            return connection
        else:
            connection = connect(host=self.host,
                                 port=self.port,
                                 auth_mechanism=self.auth.upper())
            self.cursor = connection.cursor()
            return connection

    def execute(self, sql, limit, displaylimit, progress_bar=False):
        """
            Query Hive2Server and return results.
        """

        if not hasattr(self, 'connection') or not self.connection:
            self.connection = self._init_connection_()
        log = UserMessages()
        try:
            for statement in sqlparse.split(sql):
                statement = statement.strip(";")
                log.info("Executing %s" % statement)
                if progress_bar and self.resource_manager and not self.sts:
                    self.cursor.execute_async("%s" % statement)
                    self._progress_bar_()
                else:
                    self.cursor.execute("%s" % statement)
        except KeyboardInterrupt:
            log.info("Cancelling the sql execution.")
            self.cursor.cancel_operation()
            log.info("Reconnecting to hive.")
            self.connection.reconnect()
            self.cursor = self.connection.cursor()
            if not self.sts:
                self.cursor.execute("SET hive.execution.engine=tez")
            log.info("Connected to hive.")
            return
        keys = []
        if self.cursor.description is not None and isinstance(
                self.cursor.description, list):
            for column in self.cursor.description:
                keys.append(column[0])
        data = []
        if self.cursor.description:
            if limit:
                data = self.cursor.fetchmany(size=limit)
            else:
                data = self.cursor.fetchall()
            log.info("Fetched %d results" % len(data))

        return ResultSet(keys, data, displaylimit)

    def insert_csv(self, table_name, name_node_url, name_node_options, csv_file, df_flag, autolimit, displaylimit=100):
        """
        Enables insertion of CSVs or DataFrames to Hive.
        """
        if self.cluster_details:
            if 'name_node_url' in self.cluster_details:
                name_node_url = self.cluster_details['name_node_url']
            if 'name_node_opts' in self.cluster_details:
                name_node_options = self.cluster_details['name_node_opts']
        csv_file_name = csv_file.split('/')[-1]
        folder_name = csv_file_name.split('.')[0]
        hdfs_location = '/user/{}/notebooks/{}'.format(getpass.getuser(),
                                                       folder_name)
        hdfs = HDFileSystem(host=name_node_url, pars=name_node_options)
        if not hdfs.exists(hdfs_location):
            hdfs.mkdir(hdfs_location)
        hdfs_file_location = '{}/{}'.format(hdfs_location, csv_file_name)
        hdfs.put(csv_file, hdfs_file_location)
        data_type = HiveConnection.csv_datatypes(csv_file)
        data_type_list = ',\n'.join(
            ['%s %s' % (key, value) for (key, value) in data_type.items()])
        create_table_command = "CREATE EXTERNAL TABLE {} ({})" \
                               "\nROW FORMAT DELIMITED\nFIELDS TERMINATED BY " \
                               "','\nSTORED AS TEXTFILE\nLOCATION '{}'\n" \
                               "tblproperties(" \
                               "\"skip.header.line.count\"=\"1\");"\
            .format(table_name, data_type_list, hdfs_location)
        drop_table_command = 'DROP TABLE IF EXISTS {};'.format(table_name)
        command = drop_table_command + '\n' + create_table_command
        if df_flag:
            os.system("rm %s" % csv_file)
        return self.execute(command, autolimit, displaylimit)

    @staticmethod
    def get_fieldnames(csv_file):
        """
        Read the first row and store values in a tuple
        """
        with open(csv_file) as csvfile:
            first_row = csvfile.readlines(1)
            fieldnames = tuple(first_row[0].strip('\n').split(","))
        return fieldnames

    @staticmethod
    def column_type(column):
        """
        Map column to CSV data type.
        """
        for val in column:
            if val != '?':
                try:
                    float(val)
                    if '.' in val:
                        ret_val = 'float'
                    else:
                        ret_val = 'int'
                    return ret_val
                except ValueError:
                    return 'string'
        return 'undetermined'

    @staticmethod
    def csv_datatypes(csv_file):
        """
            Map columns to CSV data types.
        """
        dtype = []
        fieldnames = HiveConnection.get_fieldnames(csv_file)
        with open(csv_file, "r") as infile:
            reader = csv.reader(infile)
            next(reader, None)  # skip the headers
            for row in reader:

                for i in row:
                    dtype.append(HiveConnection.column_type(i))
                break
            data_dict = OrderedDict(zip(fieldnames, dtype))
            return data_dict

    def _get_status_(self):
        """
            Get connection status.
        """
        status = self.cursor.status()
        return status

    def _get_progress_(self):
        """
        Gives progress of application id.
        :return:
        """
        if self.application_id:
            # Ignoring the errors and marching. Error in getting progress shouldn't fail the sql execution.
            app_info = self.resource_manager.cluster_application(
                self.application_id, ignore_errors=True)
            if app_info and 'app' in app_info and 'progress' in app_info['app']:
                return app_info['app']['progress']
        return 0

    def _progress_bar_(self):
        """
        Creates progress bar and updates status.
        :return:
        """
        if self._get_status_() == 'RUNNING_STATE':
            status_bar = StatusBar()
        elif self._get_status_() == "FINISHED_STATE":
            return
        progress = self._get_progress_()
        while self._get_status_() == 'RUNNING_STATE':
            status_bar.update_status(progress)
            if progress > 0:
                status_bar.update_info_message("{:0.2f}% - {} ".format(progress, self.application_id))
            logs = self.cursor.get_log()
            log_lines = logs.split("\n")
            log_info = log_lines[len(log_lines) - 1]
            if log_info:
                status_bar.update_info_message(log_info)
            if logs:
                self._update_app_id_(logs)
            time.sleep(1)
            progress = self._get_progress_()
        if self._get_status_() == "ERROR_STATE":
            raise Exception(self.cursor.get_log())
        elif self._get_status_() == "FINISHED_STATE":
            status_bar.update_status_success("Execution completed.")

    def _update_app_id_(self, logs):
        """
        Updates application id from logs.
        :param logs: Resource Manager logs of the application.
        :return:
        """
        app_ids = re.findall(r"application_\d+_\d+", logs)
        if app_ids:
            self.application_id = app_ids[0]

    @staticmethod
    def _authecticate_():
        """
            Enables Kerberos authentication of connection.
        """
        if os.system('klist -s') != 0:
            inp = 0
            while inp not in ("1", "2"):
                inp = input("Do you have keytab or password? If keytab Enter "
                            "1 else 2: ")
                if inp != "1" and inp != "2":
                    print("You must type 1 or 2")
            if inp == "1":
                connection = False
                location = input("Enter keytab Location ")
                principal = input("Enter keytab Principal ")
                if os.system("kinit -kt %s %s" % (location, principal)) == 0:
                    print("Successfully renewed kerberos ticket.")
                    connection = True
                if not connection:
                    print(
                        "Error: Some problem with your keytab principal and "
                        "location , please check your password and "
                        "restart the kernel with correct password.")
            if inp == "2":
                connection = False
                for _ in range(0, 4):
                    print("Enter Kerberos password to renew Kerberos ticket: ")
                    password = getpass.getpass()
                    user = getpass.getuser()
                    cmd = "export password='%s'; echo $password|kinit %s" \
                          % (password, user)
                    if os.system(cmd) == 0:
                        print("Successfully renewed kerberos ticket.")
                        connection = True
                        break
                    else:
                        print("Invalid password, please try again")
                if not connection:
                    print(
                        "Error:Some problem with your LDAP password, please "
                        "check your password and restart the "
                        "kernel with correct password.")

    def _close_connection_(self):
        """
            Closes hiveserver2 connection.
        """
        try:
            if self.cursor:
                self.cursor.close()
            del self.cursor
        except BaseException:
            pass
        try:
            if self.connection:
                self.connection.close()
            del self.connection
        except BaseException:
            pass

    def __del__(self):
        self._close_connection_()
        return super(HiveConnection, self).__del__()
