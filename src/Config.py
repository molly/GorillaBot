# Copyright (c) 2013 Molly White
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from os import path
import configparser
import logging

__all__ = ["Configure"]

class Configure(object):
    '''Creates, modifies, or opens a configuration file.'''
    def __init__(self, config, root, logger):
        self._config = configparser.ConfigParser()
        self._config_path = path.join(self._root, "config.cfg")
        self._logger = logging.getLogger("GB")
        
    def load(self):
        file = self._config_path
        if path.isfile(file):
            try:
                self._config.read_file(open(self._config_path))
            except IOError:
                self._logger.exception("Unable to open {}".format(self._config_path))
        else:
            self.make_new()
    
    def make_new(self):
        print ("Made")
