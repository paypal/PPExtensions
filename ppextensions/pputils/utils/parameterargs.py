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

"""Manage Line and Cell magic parameters."""

from enum import Enum

from ppextensions.pputils.utils.exceptions import InvalidParameterType, MissingArgument


class WidgetType(Enum):
    """
    Widget Types.
    """
    TEXTBOX = "textbox"
    DROPDOWN = "dropdown"
    READ = "read"


class ParameterArgs:
    """
    Manage Line and Cell magic parameters.
    """

    def __init__(self, args):
        self.args = args

    def widget_type(self):
        """
            Get Widget type.
        """
        try:
            return WidgetType(getattr(self.args, 'type'))
        except ValueError:
            raise InvalidParameterType("Invalid parameter type. Only textbox or dropdown are supported.")

    def get(self, key):
        """
            Get parameter value.
        """
        if hasattr(self.args, key):
            param_value = getattr(self.args, key)
        else:
            raise MissingArgument(key)

        return param_value

    def hasattr(self, key):
        """
            Checks if paramter is present.
        """
        return hasattr(self.args, key)

    def get_list(self, key):
        """
            Get list of parameters.
        """
        return self.get(key).split(":::")
