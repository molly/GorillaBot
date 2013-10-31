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

import logging, threading


class Executor(object):
    """This class listens for commands to execute, then executes them."""

    def __init__(self, command_q):
        self.command_q = command_q
        self.logger = logging.getLogger('GorillaBot')

    def loop(self, bot):
        self.logger.debug('Thread created.')
        while not bot.shutdown.is_set():
            # Block until a command exists in the queue
            command = self.command_q.get()
            if not command.needs_own_thread:
                # Call the function the command triggers
                if command.args is not None:
                    command.trigger(*command.args)
                else:
                    command.trigger()
                self.command_q.task_done()
            else:
                threading.Thread(name=command.trigger.__name__,
                                    target=command.trigger,
                                    args=command.args).start()
