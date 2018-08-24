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

"""Exceptions for PPExtensions."""

import functools

from IPython import get_ipython

from .log import Log


class ParameterNotDefined(Exception):
    """
    Exception for parameter not defined cases.
    """

    def __init__(self, parameter_name):
        Exception.__init__(self, "Parameter %s not defined." % parameter_name)


class UnsupportedCluster(Exception):
    """
    Exception when a cluster is not supported.
    """

    def __init__(self, cluster):
        Exception.__init__(self, "Cluster %s is not supported." % cluster)


class InvalidParameterType(Exception):
    """
    Exception for parameter type mismatch.
    """

    def __init__(self, message):
        Exception.__init__(self, message)


class MissingArgument(Exception):
    """
    Exception when dealing with missing arguments.
    """

    def __init__(self, param):
        Exception.__init__(self, "Missing required argument %s" % param)


class TableauException(Exception):
    """
    Exception for Tableau related errors.
    """

    def __init__(self, message):
        Exception.__init__(self, message)


class ResourceManagerException(Exception):
    """
    Exception to describe resource allocation errors.
    """

    def __init__(self, message):
        Exception.__init__(self, message)


class DownloadException(Exception):
    """
    Exception to describe download errors.
    """

    def __init__(self, message):
        Exception.__init__(self, message)


def wrap_exceptions(function_name):
    """
    A decorator that wraps the passed in function and logs
    exceptions should one occur
    """

    @functools.wraps(function_name)
    def wrapper(*args, **kwargs):
        try:
            return function_name(*args, **kwargs)
        except Exception as error_msg:
            # log the exception
            log = Log(function_name.__name__, 'wrap_exception')
            error_formatted_message = '{}: {}'.format(error_msg.__class__.__name__, error_msg)
            log.exception(error_formatted_message)
            get_ipython().write_err(error_formatted_message)
            raise error_msg
    return wrapper
