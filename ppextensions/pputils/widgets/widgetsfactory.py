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

"""Get IPyWidgets."""
from ipywidgets import VBox, Output, Button, HTML, HBox, Dropdown, Checkbox, ToggleButtons, Text, Textarea, Tab, Password


class WidgetsFactory:

    @staticmethod
    def get_vbox(**kwargs):
        """
        Get VBox Widget.
        """
        return VBox(**kwargs)

    @staticmethod
    def get_output(**kwargs):
        """
            Get Output.
        """
        return Output(**kwargs)

    @staticmethod
    def get_button(**kwargs):
        """
            Get Button.
        """
        return Button(**kwargs)

    @staticmethod
    def get_html(value, **kwargs):
        """
            Get HTML.
        """
        return HTML(value, **kwargs)

    @staticmethod
    def get_hbox(**kwargs):
        """
            Get HBox Widget.
        """
        return HBox(**kwargs)

    @staticmethod
    def get_dropdown(**kwargs):
        """
            Get Dropdown Widget.
        """
        return Dropdown(**kwargs)

    @staticmethod
    def get_checkbox(**kwargs):
        """
            Get Checkbox Widget.
        """
        return Checkbox(**kwargs)

    @staticmethod
    def get_toggle_buttons(**kwargs):
        """
            Get Toggle Buttons.
        """
        return ToggleButtons(**kwargs)

    @staticmethod
    def get_text(**kwargs):
        """
            Get Text.
        """
        return Text(**kwargs)

    @staticmethod
    def get_password(**kwargs):
        """
            Get Password Widget.
        """
        return Password(**kwargs)

    @staticmethod
    def get_text_area(**kwargs):
        """
            Get Text Area.
        """
        return Textarea(**kwargs)

    @staticmethod
    def get_tab(**kwargs):
        """
            Get Tab.
        """
        return Tab(**kwargs)
