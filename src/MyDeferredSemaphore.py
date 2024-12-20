#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2025 by dream-alpha
#
# In case of reuse of this source code please do not remove this copyright.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For more information on the GNU General Public License see:
# <http://www.gnu.org/licenses/>.


from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredSemaphore
from .Debug import logger


def MyCallLater(acallable, *args, **kwargs):
	logger.info("...")
	return reactor.callLater(0, acallable, *args, **kwargs)


def MyDeferLater(acallable, *args, **kw):
	logger.info("...")

	def deferLaterCancel(_deferred):
		logger.info("...")
		if delayedCall.active():
			delayedCall.cancel()

	def cb(_result):
		logger.info("...")
		deferLaterCancel(None)
		if acallable:
			return acallable(*args, **kw)
		return None

	d = Deferred(canceller=deferLaterCancel)
	d.addCallback(cb)
	delayedCall = reactor.callLater(0, d.callback, None)
	d.deferLaterCancel = deferLaterCancel
	return d


class MyDeferredSemaphore:

	def __init__(self, tokens=1):
		logger.info("...")
		self._ds = DeferredSemaphore(tokens=tokens)
		self._deferreds = []
		self._dict = {}

	def run(self, *args, **kwargs):
		logger.info("...")
		return self._ds.run(*args, **kwargs)

	def rundeferLater(self, _ltime, *args, **kwargs):
		logger.info("...")
		return MyDeferLater(self._ds.run, *args, **kwargs)

	def start(self, *args, **kwargs):
		logger.info("...")
		return self.rundeferLater(0, *args, **kwargs)

	def deferCanceler(self, _cancel=""):
		logger.info("...")
		for items in self._ds.waiting:
			items._suppressAlreadyCalled = True
			items._runningCallbacks = True
			items.pause()
			items._canceller = None
			items.cancel()
			self._ds.waiting.remove(items)

		del self._ds.waiting[:]

	def settokens(self, tokens=10):
		logger.info("...")
		self._ds.tokens = tokens
		self._ds.limit = tokens

	def finished(self):
		logger.info("...")
		return self._ds.tokens >= self._ds.limit

	def __del__(self):
		logger.info("...")
		self.deferCanceler()
		self._dict.clear()
