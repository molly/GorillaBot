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

import glob
import os
import logging
import sys

__all__ = ["PluginManager"]

class PluginManager(object):
    def __init__(self):
        self.logger = logging.getLogger("GorillaBot")
        self.plugin_list = dict()
        self.plugin_files = set(glob.glob(os.path.join('plugins', '*.py')))
        print(self.plugin_files)
        
    def format_plugin(self):
        pass
        
    def load_plugins(self):
        for filename in self.plugin_files:
            self.logger.info("Attempting to load {}.".format(filename))
            try:
                file = open(filename, 'U').read()
                plugin = compile(file, filename, 'exec')
                namespace = dict()
                eval(plugin, namespace)
            except Exception:
                self.logger.exception("Exception raised while trying to evaluate"
                                      "{}.".format(filename))
                continue
            
            for object in namespace.itervalues():
                if hasattr(object, "_hook"):
                    for type, data in object._hook:
                        self.plugins[type] += data
                        self.logger.info("Plugin (type {0}) loaded:"
                                         "{1}.".format(type, self.format_plugin(data)))