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

from IPython.core.magic import Magics, magics_class, line_magic, needs_local_scope
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring

from ppextensions.pputils import ParameterWidgets, ParameterArgs, WidgetType
from ppextensions.pputils.utils.exceptions import InvalidParameterType

try:
    from traitlets.config.configurable import Configurable

except ImportError:
    from IPython.config.configurable import Configurable


@magics_class
class Parameters(Magics, Configurable):
    """Parameterization magics.."""

    def __init__(self, shell):
        Configurable.__init__(self, config=shell.config)
        Magics.__init__(self, shell=shell)
        self.widgets = ParameterWidgets(shell)
        self.shell.user_ns['ppwidgets'] = self.widgets
        # Add ourself to the list of module configurable via %config
        self.shell.configurables.append(self)

    @needs_local_scope
    @magic_arguments()
    @line_magic('parameter')
    @argument("-n", "--name", type=str, help="Name of the widget.")
    @argument("-t", "--type", type=str, default="read",
              help="Type of parameter. textbox/dropdown are currently supported.")
    @argument("-d", "--defaultValue", type=str, default="textbox",
              help="Type of parameter. textbox/dropzone are currently supported.")
    @argument("-v", "--values", type=str, default='',
              help="List of values separated by ':::', if type is dropdown. Ex: first:::last")
    def parameter(self, arg, local_ns={}):
        """
            Magic to parameterize your notebooks.

            This magic allows you to parameterize notebooks. You can create two kinds of parameterization - textbox and dropdown.

            Create a parameter widget:
            ==========================

                %parameter -t textbox -n myTextbox -d text

                %parameter -t dropdown -n myDropdown -d dropdown1 -v dropdown1:::dropdown2


            Reading from widget:
            ====================

                %parameter -n myTextbox

            The same can be done using ppwidgets python API.

        """
        user_ns = self.shell.user_ns.copy()
        user_ns.update(local_ns)
        args = ParameterArgs(parse_argstring(self.parameter, arg))
        if args.widget_type() is WidgetType.READ:
            return self.widgets.get(args.get('name'))
        elif args.widget_type() is WidgetType.TEXTBOX:
            self.widgets.text(args.get('name'), args.get('defaultValue'))
        elif args.widget_type() is WidgetType.DROPDOWN:
            if args.get('defaultValue') not in args.get_list('values'):
                raise InvalidParameterType("defaultValue should be present in dropdown values specified.")
            self.widgets.dropdown(args.get('name'), args.get('defaultValue'), args.get_list('values'))
        else:
            raise InvalidParameterType("%s is not supported" % args.widget_type())


def load_ipython_extension(ip):
    """Load the extension in IPython."""
    ip.register_magics(Parameters)
