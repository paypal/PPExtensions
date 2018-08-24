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

"""Manging Queuing system for Spark Thrift Server."""

import requests
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from ppextensions.pputils.utils.exceptions import ResourceManagerException


class ResourceManager:
    """
    Manging Queuing system for Spark Thrift Server.
    """

    def __init__(self, url):
        self._url = url

    def _request_(self, api_path, ignore_errors, **query_args):
        """Base request handler for all HTTP requests"""
        params = urlencode(query_args)
        if params:
            response = requests.get(url=self._url + api_path, params=params, allow_redirects=True)
        else:
            response = requests.get(url=self._url + api_path, allow_redirects=True)

        if response.ok:
            response_json = response.json()
        elif not ignore_errors:
            raise ResourceManagerException(response.text)
        return response_json

    def cluster_application(self, application_id, ignore_errors=False):
        """
        Gives status of an application from Resource Manager
        :param application_id: The application id
        :param ignore_errors: Set to True will ignore the errors
        :return: API response object with JSON data
        """
        path = '/ws/v1/cluster/apps/{appid}'.format(appid=application_id)
        return self._request_(path, ignore_errors)

    def cluster_metrics(self, ignore_errors=False):
        """
        The cluster metrics resource provides some overall metrics about the
        cluster. More detailed metrics should be retrieved from the jmx
        interface.
        :param ignore_errors: Set to True will ignore the errors
        :returns: API response object with JSON data
        """
        path = '/ws/v1/cluster/metrics'
        return self._request_(path, ignore_errors)
