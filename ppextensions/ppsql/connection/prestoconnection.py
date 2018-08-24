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

"""This class enables connecting to Presto. Implements BaseConnection."""

import getpass
import os

import sqlalchemy

from ppextensions.ppsql.connection.basesql import BaseConnection
from ppextensions.pputils import PrestoStatusBar, ResultSet
from ppextensions.pputils.utils.configuration import conf_info


class PrestoConnection(BaseConnection):
    def __init__(self, cluster, host, port, auth):

        self.cluster_details = conf_info('presto')
        if cluster in self.cluster_details:
            self.cluster_details = self.cluster_details[cluster]
            host = self.cluster_details['host']
            port = self.cluster_details['port']
            auth = self.cluster_details['auth']

        if auth.upper() == 'GSSAPI':
            PrestoConnection._authecticate_()
        engine = sqlalchemy.create_engine("presto://%s:%d/" % (host, port))
        self.session = None
        super(PrestoConnection, self).__init__(engine)

    def execute(self, sql, limit, displaylimit, progress_bar):
        if progress_bar is False:
            return self._execute_without_progress_bar_(sql, limit, displaylimit)

        cursor = self.connection.execute("%s" % sql).cursor
        PrestoStatusBar(cursor)

        keys = []
        if cursor.description is not None and isinstance(cursor.description, list):
            for column in cursor.description:
                keys.append(column[0])
        if limit:
            data = cursor.fetchmany(size=limit)
        else:
            data = cursor.fetchall()

        return ResultSet(keys, data, displaylimit)

    def _execute_without_progress_bar_(self, sql, limit, displaylimit):
        if self.session is None:
            self.session = self.connection.connect()

        result = self.session.execute("%s" % sql)
        keys = result.keys()
        if limit:
            data = result.fetchmany(size=limit)
        else:
            data = result.fetchall()
        result.close()
        return ResultSet(keys, data, displaylimit)

    @staticmethod
    def _authecticate_():
        """
            Enables Kerberos authentication of connection.
        """
        if os.system('klist -s') != 0:
            inp = 0
            while inp not in ("1", "2"):
                inp = input("Do you have keytab or password? If keytab Enter 1 else 2: ")
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
                        "Error:Some problem with your keytab principal and location , please check your password and "
                        "restart the kernel with correct password.")
            if inp == "2":
                connection = False
                for _ in range(0, 4):
                    print("Enter Kerberos password to renew Kerberos ticket: ")
                    password = getpass.getpass()
                    user = getpass.getuser()
                    cmd = "export password='%s'; echo $password|kinit %s" % (password, user)
                    if os.system(cmd) == 0:
                        print("Successfully renewed kerberos ticket.")
                        connection = True
                        break
                    else:
                        print("Invalid password, please try again")
                if not connection:
                    print(
                        "Error: Some problem with your LDAP password, please check your password and restart the "
                        "kernel with correct password.")
