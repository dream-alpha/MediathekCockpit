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


import os
import json
from time import localtime, strftime
from enigma import eServiceReference
from Plugins.SystemPlugins.JobCockpit.JobSupervisor import JobSupervisor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.config import config
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Components.Sources.List import List
from .Debug import logger
from .__init__ import _
from .Version import PLUGIN, ID
from .MoviePlayer import MoviePlayer
from .EventView import EventView
from .DownloadJob import DownloadJob
from .Menu import Menu
from .ChannelSelection import ChannelSelection
from .Constants import (
	LIST_DATE, LIST_EVENT_NAME, LIST_SHORT_DESCRIPTION, LIST_TIME, LIST_DURATION, LIST_CHANNEL, LIST_TITLE, LIST_TOPIC, LIST_DESCRIPTION, LIST_TIMESTAMP
)
from .ChannelUtils import getServiceReference
from .UnicodeUtils import convertUni2Str
from .WebRequests import WebRequests
from .RecordingUtils import calcRecordingFilename
from .CallLater import callLater
from .MovieUtils import getVideoUrl, getVideoResolutions, getPlaylistSegments, getMovieRow, getNextRow
from .Search import Search
from .MovieInfo import MovieInfo


class MediathekCockpit(Screen, Menu, ChannelSelection, Search):
	def __init__(self, session, query):
		self.query = query
		Screen.__init__(self, session)
		self.skinName = "MediathekCockpit"
		Menu.__init__(self)
		ChannelSelection.__init__(self)
		Search.__init__(self)
		self.last_service = self.session.nav.getCurrentlyPlayingServiceReference()
		self.title_base = PLUGIN + " - " + _("Movies") + " - " + _("Search results")
		self.title = self.title_base + " - " + _("Downloading movies...")

		self["key_red"] = StaticText(_("Exit"))
		self["key_green"] = StaticText(_("Channels"))
		self["key_yellow"] = StaticText(_("Download"))
		self["key_blue"] = StaticText(_("Search"))

		self["description"] = Label("")
		self["date"] = Label("")

		self["list"] = List()
		self.list = []
		self.curr_index = 0
		self.query_info = {}

		self["actions"] = ActionMap(
			["MTC_Actions"],
			{
				"ok": self.pressOk,
				"cancel": self.pressClose,
				"red": self.pressRed,
				"green": self.pressGreen,
				"yellow": self.pressYellow,
				"blue": self.pressBlue,
				"menu": self.openMenu,
				"info": self.pressInfo,
				"5": self.showMovieInfo
			}
		)
		self["list"].onSelectionChanged.append(self.__onSelectionChanged)
		self.onLayoutFinish.append(self.__onLayoutFinish)
		self.job_manager = JobSupervisor.getInstance().getJobManager(ID)

	def __onLayoutFinish(self):
		logger.info("...")
		if self.query:
			query = self.query
			self.query = ""
			callLater(0, self.openKeyboard, query)
		else:
			self.postdata["offset"] = 0
			callLater(0, self.downloadMovieList)

	def downloadMovieList(self, channel=None):
		logger.info("postdata: %s", self.postdata)
		result_count = 0
		if self.postdata["offset"] == 0:
			self.list = []
		url = "https://mediathekviewweb.de/api/query"
		result = WebRequests().postContent(url, self.postdata)
		if result.text:
			data = convertUni2Str(json.loads(result.text))
			# logger.debug("data: %s", data)
			results = data["result"]["results"]
			# logger.debug("results: %s", results)
			for x in results:
				row = getMovieRow(x)
				title = row[LIST_TITLE]
				topic = row[LIST_TOPIC]
				title_topic = title + topic
				skip = False
				if channel and channel != row[LIST_CHANNEL]:
					continue
				if row[LIST_DURATION] < int(config.plugins.mediathekcockpit.skip_short_duration.value):
					continue
				if config.plugins.mediathekcockpit.skip_audiodeskription.value:
					skip |= "Audiodeskription" in title_topic
				if config.plugins.mediathekcockpit.skip_trailer.value:
					skip |= "Trailer" in title_topic
				if config.plugins.mediathekcockpit.skip_gebaerdensprache.value:
					skip |= "Gebärdensprache" in title_topic
				if not skip:
					self.list.append(row)
				else:
					logger.debug("Skipping movie: %s", title_topic)

			self.query_info = data["result"]["queryInfo"]
			result_count = min(self.postdata["offset"] + self.query_info["resultCount"], self.query_info["totalResults"])
			self.query_info["filmlisteTimestamp"] = strftime("%d.%m.%Y %H:%M:%S", localtime(int(self.query_info["filmlisteTimestamp"])))
			# logger.debug("query_info: %s", self.query_info)
			if self.query_info["totalResults"] != result_count:
				self.list.append(getNextRow())

		logger.info("list: %s", self.list)
		self["list"].setList(self.list)
		self["list"].setIndex(self.curr_index)
		if len(self.list) == 0:
			self.title = self.title_base + " - " + _("No movies available")
		else:
			self.title = self.title_base

	def __onSelectionChanged(self):
		logger.info("...")
		self["description"].setText("")
		self["date"].setText("")
		self.curr = self["list"].getCurrent()
		logger.debug("curr: %s", self.curr)
		if self.curr and self.curr[LIST_CHANNEL] != ">>>":
			self["description"].setText(self.curr[LIST_DESCRIPTION])
			self["date"].setText("%s: %s %s" % (_("Duration"), self.curr[LIST_DURATION], _("Minutes")))

	def pressOk(self):
		self.curr = self["list"].getCurrent()
		if self.curr:
			if self.curr[LIST_CHANNEL] == ">>>":
				self.curr_index = self["list"].getIndex()
				logger.debug("curr_index: %s", self.curr_index)
				self.postdata["offset"] += int(config.plugins.mediathekcockpit.size.value)
				del self.list[len(self.list) - 1]
				self.downloadMovieList()
			else:
				val = int(config.plugins.mediathekcockpit.movie_resolution.value)
				url, _resolution = getVideoUrl(self.curr, val)
				if url:
					self.playMovie(url)

	def playMovie(self, url):
		logger.info("url: %s", url)
		sref = eServiceReference(eServiceReference.idGST, 0, url.encode("utf-8"))
		sref.setName(self.curr[LIST_EVENT_NAME])
		self.session.openWithCallback(self.playMovieCallback, MoviePlayer, sref, menuval=None, infoval=(EventView, self.curr))

	def playMovieCallback(self):
		self.session.nav.playService(self.last_service)

	def pressRed(self):
		self.pressClose()

	def pressGreen(self):
		self.openChannelSelection()

	def pressYellow(self):
		logger.info("...")
		self.curr = self["list"].getCurrent()
		movie_dir = config.plugins.mediathekcockpit.movie_dir.value
		if self.curr and self.curr[LIST_CHANNEL] != ">>>":
			if os.path.exists(movie_dir):
				url, resolution = getVideoUrl(self.curr, int(config.plugins.mediathekcockpit.movie_resolution.value))
				ext = url[url.rfind("."):] if url.rfind(".") != -1 else ".mp4"
				service_ref = getServiceReference(self.curr[LIST_CHANNEL])
				segments = []
				if url.endswith(".m3u8"):
					segments = getPlaylistSegments(url)
					ext = os.path.splitext(os.path.dirname(url))[1]
				recording_file = calcRecordingFilename(self.curr[LIST_TIMESTAMP], self.curr[LIST_CHANNEL], self.curr[LIST_EVENT_NAME], movie_dir) + ext
				self.job_manager.AddJob(
					DownloadJob(
						url,
						segments,
						recording_file,
						self.curr[LIST_EVENT_NAME],
						self.curr[LIST_SHORT_DESCRIPTION],
						self.curr[LIST_DESCRIPTION],
						self.curr[LIST_TIMESTAMP],
						service_ref
					)
				)
				self.session.open(
					MessageBox, "%s:\n\n%s\n\n%s: %s" % (
						_("Download added"),
						self.curr[LIST_EVENT_NAME],
						_("Video resolution"), resolution,
					),
					type=MessageBox.TYPE_INFO,
					timeout=4
				)
			else:
				self.session.open(MessageBox, _("Movie directory does not exist") + ":\n\n" + movie_dir, type=MessageBox.TYPE_ERROR)

		else:
			self.session.open(MessageBox, _("No movie to download"), type=MessageBox.TYPE_INFO, timeout=4)

	def pressBlue(self):
		query = ""
		self.curr = self["list"].getCurrent()
		if self.curr:
			query = self.curr[LIST_TOPIC]
			self.openKeyboard(query)

	def pressInfo(self):
		self.curr = self["list"].getCurrent()
		if self.curr and self.curr[LIST_CHANNEL] != ">>>":
			self.session.open(EventView, self.curr)

	def pressClose(self):
		logger.info("...")
		self.close()

	def showMovieInfo(self):
		curr = self["list"].getCurrent()
		self.session.open(MovieInfo, curr)
