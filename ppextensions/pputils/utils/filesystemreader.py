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

"""Reading and Managing PPExtensions Configuration."""

import os


class FileSystemReaderWriter:
    """
    Credits: Thanks to 'SPARKMAGIC' for FileSystemReader.
    """

    def __init__(self, path):
        assert path is not None
        self.path = os.path.expanduser(path)

    def ensure_path_exists(self):
        """
        Ensure PPExtensions path exists in user's home.
        """
        FileSystemReaderWriter._ensure_path_exists(self.path)

    def ensure_file_exists(self):
        """
        Ensure PPExtensions configuration file exists.
        """
        self._ensure_path_exists(os.path.dirname(self.path))
        if not os.path.exists(self.path):
            open(self.path, 'w').close()

    def read_lines(self):
        """
        Read PPExtensions Configuration.
        """
        if os.path.isfile(self.path):
            with open(self.path, "r+") as config_file:
                return config_file.readlines()
        else:
            return ""

    def overwrite_with_line(self, line):
        """
        Write additional configuration to PPExtensions.
        """
        with open(self.path, "w+") as f:
            f.writelines(line)

    @staticmethod
    def _ensure_path_exists(path):
        """
        Creates a path to PPExtensions configuration.
        """
        try:
            os.makedirs(path)
        except OSError:
            if not os.path.isdir(path):
                raise
