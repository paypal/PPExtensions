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

"""This class enables working with CSV files. Implements BaseConnection."""

import re
import pandas as pd

from IPython import get_ipython

from ppextensions.ppsql.connection.basesql import BaseConnection
from ppextensions.pputils.utils.exceptions import InvalidParameterType


class CSVConnection(BaseConnection):
    first_run = True
    dflist = []

    def __init__(self):
        super(CSVConnection, self).__init__('')

    def execute(self, sql):
        return self._execute_csv_data_(str(sql))

    def _execute_csv_data_(self, query):
        """ Parse the sql query csv fields Returns the required csv results for persisted dataframe.
        """
        ipython = get_ipython()
        if self.first_run:
            ipython.magic("reload_ext sql")
        self.first_run = False
        try:
            filename = re.split("from", query, 1, flags=re.IGNORECASE)[1].split()[0]
            df_name = filename.replace("/", "_").replace(" ", "_").replace(".", "_").replace(":", "_").replace("-", "")
        except BaseException:
            raise InvalidParameterType("Problem in select query. Type the correct query and try again")
        if df_name in self.dflist:
            query = query.replace(filename, df_name)
            result = ipython.magic("sql {}".format(query))
        else:
            query = query.replace(filename, df_name)
            try:
                if filename.endswith('.tsv'):
                    exec('{}= pd.read_csv(\'{}\',sep=\'\\t\')'.format(df_name, filename))
                else:
                    exec('{}= pd.read_csv(\'{}\')'.format(df_name, filename))
            except IOError:
                raise IOError('File %s does not exist. Please type correct file name and try again' % (filename))
            ipython.magic("sql sqlite://")
            ipython.magic("sql persist {}".format(df_name))
            self.dflist.append(df_name)
            result = ipython.magic("sql {}".format(query))
        return result
