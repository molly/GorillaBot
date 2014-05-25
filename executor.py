# Copyright (c) 2013-2014 Molly White
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import logging
import queue
import threading
from time import sleep


class Executor(object):
    """Waits for messages to appear in the queue, then executes commands as needed."""

    def __init__(self, bot, message_q, shutdown):
        self.bot = bot
        self.message_q = message_q
        self.logger = logging.getLogger("GorillaBot")
        self.shutdown = shutdown

    def loop(self):
        self.logger.debug("Thread created.")
        while not self.shutdown.is_set():
            # Block until a message exists in the queue
            try:
                if self.bot.response_lock.locked():
                    raise threading.ThreadError
                else:
                    message = self.message_q.get(timeout=5)
            except queue.Empty:
                # No messages in the queue, continue loop
                pass
            except threading.ThreadError:
                # Wait for other process to release the lock
                sleep(5)
            else:
                print(message)
                print(message.trigger)
                # If this message has a trigger, execute the function
                if message.trigger:
                    if message.needs_own_thread:
                        # Begin a new thread if necessary
                        threading.Thread(name=message.trigger.__name__, target=message.trigger,
                                         args=message.args).start()
                    else:
                        if message.args:
                            message.trigger(*message.args)
                        else:
                            message.trigger()
                    self.message_q.task_done()