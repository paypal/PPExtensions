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

"""Enables Logging for PPExtensions."""

import logging
import getpass
import os

from pathlib import Path


class Log:
    """
    Custom Logging for PPExtensions.
    """

    def __init__(self, logger_name, module='',
                 filename='{}/logs/ppextensions.log'.format(str(Path.home())),
                 level=logging.INFO):
        self.logger_name = logger_name
        self._module = module
        if not os.path.isdir("{}/logs/".format(str(Path.home()))):
            os.mkdir("{}/logs/".format(str(Path.home())))
        logging.basicConfig(
            filename=filename,
            level=level,
            format='%(asctime)-4s %(levelname)-4s %(name)-4s {} %(message)s'.format(getpass.getuser()),
            datefmt='%m-%d %H:%M:%S'
        )
        self._init_logger_()

    def _init_logger_(self):
        """
        Initialize logger.
        """
        self.logger = logging.getLogger(self.logger_name)

    def debug(self, message):
        """
        Logging debug messages.
        """
        self.logger.debug(self._format_message_(message))

    def error(self, message):
        """
        Logging error messages.
        """
        self.logger.error(self._format_message_(message))

    def info(self, message):
        """
        Logging info.
        """
        self.logger.info(self._format_message_(message))

    def exception(self, message):
        """
        Logging exceptions.
        """
        self.logger.exception(self._format_message_(message))

    def _format_message_(self, message):
        """
        Formatting log messages.
        """
        if self._module is None or len(self._module) is 0:
            return message
        return '{} {}'.format(self._module, message)
