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

import logging
import re
from queue import Empty
from plugins.util import admin


def _get_admin(bot, *users):
	"""Add a user's ident and host to the list of bot admins. Note that this
	doesn't work if the user is offline."""
	bot.response_lock.acquire()
	logger = logging.getLogger('GorillaBot')
	initializing = False
	if not users:
		initializing = True
		if bot.settings['botop'] == ['']:
			bot.response_lock.release()
			return
		else:
			users = bot.settings['botop']
	for user in users:
		bot.waiting_for_response = True
		bot.whois(user)
		while True:
			try:
				response = bot.response_q.get(True, 120)
			except Empty:
				logger.error("No whois response.")
			nick = None
			if response[1] == '311':
				nick = response[3]
				ident = response[4]
				host = response[5]
				break
			if response[1] == '401':
				if initializing:
					bot.settings['botop'].remove(user)
				break
		bot.waiting_for_response = False
		if nick:
			userinfo = [ident, host]
			if userinfo not in bot.admins.values():
				bot.admins[user] = userinfo
				logger.info('User {0} added to admin list (*!{1}@{2}).'
					.format(nick, ident, host))
			if nick not in bot.settings['botop']:
				bot.settings['botop'].append(nick)
	bot.response_lock.release()


def _is_admin(bot, user):
	"""Returns true if the user is a bot admin, false otherwise. If the user's ident
	and host are not in the list, but the user's nick is, we assume that user is
	indeed an admin, and add theirident and host to the list."""
	match = re.search(':(?P<nick>.+?)!(?P<ident>.+?)@(?P<host>.+?)\Z', user)
	if match:
		sender_nick = match.group('nick')
		sender_ident = match.group('ident')
		sender_host = match.group('host')
	else:
		return False
	userinfo = [sender_ident, sender_host]
	if userinfo in bot.admins.values():
		return True
	else:
		if sender_nick in bot.settings['botop']:
			_get_admin(bot, sender_nick)
			return True
	return False

@admin()
def addadmin(bot, *args):
	"""Add a bot operator."""
	if not args[2]:
		bot.say(args[1], "Please specify a user to add as a bot operator.")
	else:
		_get_admin(bot, args[2][0])
		if args[2][0] in bot.settings['botop']:
			bot.say(args[1], "{} has been added as a bot operator."
				.format(args[2][0]))
		else:
			bot.say(args[1], "{} is not online, and has not been added as a bot"
				" operator.".format(args[2][0]))

@admin()
def join(bot, *args):
	"""Join a channel."""
	if not args[2] or args[2][0][0] != '#':
		bot.say(args[1], "Please specify which channel to join by typing "
			"!join #channel")
	else:
		channel = [args[2][0]]
		bot.join(channel)


@admin('leave')
def part(bot, *args):
	"""Part from a channel with an optional message."""
	if not args[2] or args[2][0][0] != '#':
		bot.say(args[1],
				"Please specify which channel to leave by typing "
				"!part #channel")
	else:
		channel = args[2][0]
		if channel not in bot.channels:
			bot.say(args[1], "I'm not in {}".format(channel))
		else:
			bot.channels.remove(channel)
			if len(args[2]) == 1:
				bot.send('PART {} Leaving'.format(args[2][0]))
			else:
				bot.send('PART {0} {1}'
							.format(args[2][0], ' '.join(args[2][1:])))


def _pong(bot, server):
	"""Respond to a ping from a server with a pong to that same server."""
	bot.send('PONG {}'.format(server))

@admin()
def removeadmin(bot, *args):
	"""Remove a bot operator."""
	if not args[2]:
		bot.say(args[1], "Please specify a user to remove from bot operators.")
	else:
		try:
			del bot.admins[args[2][0]]
		except KeyError:
			bot.say(args[1], "{} is not online, and has not been added as a bot"
				" operator.".format(args[2][0]))
		else:
			bot.say(args[1], "{} has been removed as a bot operator."
				.format(args[2][0]))
		try:
			bot.settings["botop"].remove(args[2][0])
		except ValueError:
			pass

@admin('quit')
def shutdown(bot, *args):
	"""Quit from the server and shut down the bot."""
	if args[2]:
		message = ' '.join(args[2])
	else:
		message = 'Shutting down'
	bot.send('QUIT {}'.format(message))
	bot.shutdown.set()
