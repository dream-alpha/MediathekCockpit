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


from Components.config import config
from Components.ActionMap import ActionMap
from Components.ServiceEventTracker import InfoBarBase
from Screens.Screen import Screen
from Screens.SimpleSummary import SimpleSummary
from Screens.InfoBarGenerics import PlayerBase, InfoBarNotifications, InfoBarSeek, InfoBarShowHide, InfoBarAudioSelection, InfoBarSubtitleSupport, InfoBarServiceErrorPopupSupport, InfoBarGstreamerErrorPopupSupport, InfoBarServiceNotifications, InfoBarPVRState
from Screens.ChoiceBox import ChoiceBox
from enigma import iServiceInformation, iPlayableService
from .__init__ import _
from .Debug import logger


class BasePlayer(InfoBarBase, InfoBarShowHide, InfoBarAudioSelection, InfoBarSubtitleSupport, InfoBarServiceErrorPopupSupport, InfoBarNotifications, InfoBarGstreamerErrorPopupSupport):
	InfoBarServiceErrorPopupSupport.STATE_TUNING = _(InfoBarServiceErrorPopupSupport.STATE_TUNING)
	InfoBarServiceErrorPopupSupport.STATE_CONNECTING = _(InfoBarServiceErrorPopupSupport.STATE_CONNECTING)
	InfoBarServiceErrorPopupSupport.MESSAGE_WAIT = _(InfoBarServiceErrorPopupSupport.MESSAGE_WAIT)
	InfoBarServiceErrorPopupSupport.STATE_RECONNECTING = _(InfoBarServiceErrorPopupSupport.STATE_RECONNECTING)
	ENABLE_RESUME_SUPPORT = False
	ALLOW_SUSPEND = True

	def __init__(self, session, service, infoval=None, menuval=None, lastservice=None):
		logger.info("...")
		for x in [
			InfoBarBase, InfoBarShowHide, InfoBarAudioSelection,
			InfoBarSubtitleSupport, InfoBarServiceErrorPopupSupport,
			InfoBarNotifications, InfoBarGstreamerErrorPopupSupport
		]:
			x.__init__(self)

		self.session = session
		self.service = service
		self.lastservice = lastservice
		self.infoval = infoval
		self.menuval = menuval
		self["ShowHideActions"] = ActionMap(
			["InfobarShowHideActions", "MoviePlayerActions", "MenuActions", "ChannelSelectEPGActions"],
			{
				"toggleShow": self.toggleShow,
				"leavePlayer": self.leavePlayer,
				"hide": self.leavePlayer,
				"showEPGList": self.showInfo,
				"menu": self.mainMenu
			},
			1
		)
		self.onFirstExecBegin.append(self.play)

	def play(self):
		logger.info("...")
		self.session.nav.playService(self.service)

	def handleLeave(self, _how):
		logger.info("...")
		self.close()

	def leavePlayer(self):
		logger.info("...")
		self.close()

	def playService(self, newservice):
		logger.info("...")
		self.session.nav.stopService()
		self.service = newservice
		self.play()

	def showInfo(self):
		logger.info("...")
		if self.infoval:
			self.session.open(*self.infoval)

	def mainMenu(self):
		logger.info("...")
		if self.menuval:
			self.session.open(*self.menuval)

	def __evVideoSizeChanged(self):
		logger.info("...")
		service = self.session.nav.getCurrentService()
		if service:
			info = service.info()
			if info:
				_xres = info.getInfo(iServiceInformation.sVideoWidth)
				_yres = info.getInfo(iServiceInformation.sVideoHeight)
				frame_rate = info.getInfo(iServiceInformation.sFrameRate)
				progressive = info.getInfo(iServiceInformation.sProgressive)
				if not progressive:
					frame_rate *= 2
				frame_rate = (frame_rate + 500) / 1000
				_p = "p" if progressive else "i"
				logger.debug("evVideoTypeReady: %s", iPlayableService.evVideoTypeReady)
				logger.debug("evVideoSizeChanged: %s", iPlayableService.evVideoSizeChanged)
				logger.debug("evVideoFramerateChanged: %s", iPlayableService.evVideoFramerateChanged)
				logger.debug("evVideoProgressiveChanged: %s", iPlayableService.evVideoProgressiveChanged)

	def createSummary(self):
		logger.info("...")
		return SimpleSummary


class StreamPlayer(Screen, PlayerBase, BasePlayer):

	def __init__(self, session, service, *args, **kwargs):
		logger.info("...")
		Screen.__init__(self, session)
		self.skinName = ["MTCStreamPlayer", "MTCMoviePlayer", "MoviePlayer"]
		PlayerBase.__init__(self)
		BasePlayer.__init__(self, session, service, *args, **kwargs)


class MoviePlayer(Screen, BasePlayer, InfoBarSeek, InfoBarServiceNotifications, InfoBarPVRState):

	def __init__(self, session, service, *args, **kwargs):
		logger.info("...")
		Screen.__init__(self, session)
		self.skinName = ["MTCMoviePlayer", "MoviePlayer"]
		InfoBarSeek.__init__(self)
		BasePlayer.__init__(self, session, service, *args, **kwargs)
		InfoBarServiceNotifications.__init__(self)
		InfoBarPVRState.__init__(self)

	def doEofInternal(self, playing):
		logger.info("...")
		if not self.execing:
			return
		if not playing:
			return
		self.handleLeave(config.plugins.mediathekcockpit.askstopmovie.value)

	def leavePlayer(self):
		logger.info("...")
		self.handleLeave(config.plugins.mediathekcockpit.askstopmovie.value)

	def handleLeave(self, how):
		logger.info("...")
		self.is_closing = True
		if how == "ask":
			lst = (
				(_("Quit"), "quit"),
				(_("Restart from the beginning"), "restart"),
				(_("None"), "continue")
			)
			self.session.openWithCallback(self.leavePlayerConfirmed, ChoiceBox, title=_("Action"), list=lst)
		else:
			self.leavePlayerConfirmed([True, how])

	def leavePlayerConfirmed(self, answer):
		logger.info("...")
		answer = answer and answer[1]
		if answer == "quit":
			self.close()
		elif answer == "restart":
			self.doSeek(0)
			self.setSeekState(self.SEEK_STATE_PLAY)

	def seekFwd(self):
		logger.info("...")
		self.fwdSeekTo(1)

	def seekBack(self):
		logger.info("...")
		self.rwdSeekTo(1)
