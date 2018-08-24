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

"""IPyWidgets for PPExtensions."""

from ppextensions.pputils.utils.exceptions import ParameterNotDefined

from .widgets import ParameterBox
from .widgetsfactory import WidgetsFactory


class ParameterWidgets:
    """
        Widget to drive user driven parameters.
    """

    def __init__(self, shell):
        super(ParameterWidgets, self).__init__()
        self._shell = shell
        # exec (shell, "from pputils.widgets.widgets import ParameterBox", shell.user_ns)
        # exec (shell, "_para_box = ParameterBox()", shell.user_ns)
        self._para_box = ParameterBox()
        self._enabled = False
        self._child = {}
        self._data = {}
        self._enable_()

    def _enable_(self):
        self._enabled = True
        self._para_box.display()

    def text(self, name, default_value, label='', observer=None):
        """
        Gives a text box for a parameter to be used in notebook.
        :param name: name of the parameter
        :param default_value: default value for the parameter.
        :param label: Is a placeholder to be used later.
        :return:
        """
        if not self._enabled:
            self._enable_()

        child = WidgetsFactory.get_text(
            value=default_value,
            description=name,
        )
        self._child[name] = child
        self._para_box.add_child(child)
        self._register_observer_(child, observer)
        self._set_values_(name, default_value)

    def dropdown(self, name, default_value, sequence, label='', observer=None):
        """
        Gives a dropdown for a parameter to be used in notebook.
        :param name: name of the parameter
        :param default_value: default value for the parameter.
        :param sequence: sequence of values for dropdown.
        :param label: is a placeholder to be used later.
        :return:
        """
        if not self._enabled:
            self._enable_()

        child = WidgetsFactory.get_dropdown(
            value=default_value,
            description=name,
            options=sequence,
        )
        self._child[name] = child
        self._para_box.add_child(child)
        self._register_observer_(child, observer)
        self._set_values_(name, default_value)

    def _register_observer_(self, child, observer=None):
        child.observe(self._update_shell_value_, names='value')
        if observer:
            child.observe(observer, names='value')

    def _update_shell_value_(self, event):
        # print("Changing value")
        # print(event)
        self._set_values_(event['owner'].description, event['new'])

    def disable_widgets(self):
        """
        Disables all widgets so user won't be able to change any values.
        :return:
        """
        for name in self._child:
            self._child[name].disabled = True

    def enable_widgets(self):
        """
        Enables all widgets so user will be able to change values.
        :return:
        """
        for name in self._child:
            self._child[name].disabled = False

    def _set_values_(self, name, value):
        self._data[name] = value
        self._shell.user_ns[name] = value

    def get(self, name):
        """
        Gives the value of the parameter set/changed.
        :param name: parameter name.
        :return: parameter value
        """
        if name in self._data:
            return self._data[name]
        else:
            raise ParameterNotDefined(name)
