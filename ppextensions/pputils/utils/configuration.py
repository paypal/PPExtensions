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

"""Configuration management for PPExtensions."""

import json
import os

from ppextensions.pputils.utils import FileSystemReaderWriter
from ppextensions.pputils.utils.constants import HOME_PATH, CONFIG_FILE

PATH = os.path.join(HOME_PATH, CONFIG_FILE)


def load_conf(path, fsrw_class=None):
    """
    Creates a dictionary of configuration by reading from the configuration file.
    """
    if fsrw_class is None:
        fsrw_class = FileSystemReaderWriter

    config_file = fsrw_class(path)
    config_file.ensure_file_exists()
    config_text = config_file.read_lines()
    line = u"".join(config_text).strip()

    if line == u"":
        conf_details = {}
    else:
        conf_details = json.loads(line)
    return conf_details


def conf_info(engine):
    """
    Returns a dictionary of configuration by reading from the configuration file.
    """
    conf_details = load_conf(PATH)
    config_dict = {}

    if engine in conf_details:
        config_dict = conf_details[engine]

    return config_dict
