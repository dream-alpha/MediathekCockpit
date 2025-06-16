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


from Plugins.SystemPlugins.JobCockpit.JobSupervisor import JobSupervisor
from Plugins.SystemPlugins.JobCockpit.JobCockpit import JobCockpit
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
from .EventView import EventView
from .Menu import Menu
from .ChannelSelection import ChannelSelection
from .Constants import LIST_EVENT_NAME, LIST_DURATION, LIST_CHANNEL, LIST_TOPIC, LIST_DESCRIPTION
from .CallLater import callLater
from .Search import Search
from .MovieInfo import MovieInfo
from .ServiceUtils import getService
from .MovieFile import MovieFile
from .MovieList import MovieList
from .CockpitPlayer import CockpitPlayer
from .ServiceCenter import ServiceCenter
from .JobUtils import getPendingJobs
from .DownloadTask import deleteFile
from Tools.BoundFunction import boundFunction


class MediathekCockpit(Screen, Menu, ChannelSelection, Search):
    def __init__(self, session, query):
        self.query = query
        Screen.__init__(self, session)
        self.skinName = "MediathekCockpit"
        Menu.__init__(self)
        ChannelSelection.__init__(self)
        Search.__init__(self)
        self.last_service = self.session.nav.getCurrentlyPlayingServiceReference()
        self.title_base = PLUGIN + " - " + \
            _("Movies") + " - " + _("Search results")
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
        self.service_center = ServiceCenter(self["list"])

        self.movie_file = MovieFile()
        self.movie_list = MovieList()
        self.job_manager = JobSupervisor.getInstance().getJobManager(ID)
        self.tmp_job_manager = JobSupervisor.getInstance().getJobManager("TMP")
        self["list"].onSelectionChanged.append(self.__onSelectionChanged)
        self.onLayoutFinish.append(self.__onLayoutFinish)

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
        if self.postdata["offset"] == 0:
            self.list = []

        self.list += self.movie_list.download(self.postdata, channel)

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
            self["date"].setText("%s: %s %s" % (
                _("Duration"), self.curr[LIST_DURATION] / 60, _("Minutes")))

    def pressOk(self):
        self.curr = self["list"].getCurrent()
        if self.curr:
            if self.curr[LIST_CHANNEL] == ">>>":
                self.curr_index = self["list"].getIndex()
                self.postdata["offset"] += int(
                    config.plugins.mediathekcockpit.size.value)
                del self.list[len(self.list) - 1]
                self.downloadMovieList()
            else:
                url, recording_path = self.movie_file.download(self.curr, self.tmp_job_manager)
                if recording_path:
                    callLater(3, self.playMovie, url, recording_path)
                else:
                    self.session.open(MessageBox, _(
                        "No valid stream detected."), type=MessageBox.TYPE_ERROR, timeout=4)

    def playMovie(self, url, path):
        logger.info("url: %s, path: %s", url, path)
        uri = path if self.checkMP4Structure(path) else url
        if uri:
            logger.debug("Playing movie from URI: %s", uri)
            service = getService(uri, self.curr[LIST_EVENT_NAME])
            self.session.openWithCallback(boundFunction(self.playMovieCallback, path), CockpitPlayer, service,
                                          config.plugins.mediathekcockpit, self.pressInfo, service_center=self.service_center)
        else:
            self.session.open(MessageBox, _("Unsupported video format or no valid stream detected."),
                              type=MessageBox.TYPE_ERROR, timeout=4)

    def playMovieCallback(self, path):
        jobs = getPendingJobs("TMP")
        if jobs:
            for job in jobs:
                JobCockpit.abortJob(job, "TMP", True)
            self.session.nav.playService(self.last_service)
        else:
            deleteFile(path)

    def pressRed(self):
        self.pressClose()

    def pressGreen(self):
        self.openChannelSelection()

    def pressYellow(self):
        logger.info("...")
        self.curr = self["list"].getCurrent()
        if self.curr and self.curr[LIST_CHANNEL] != ">>>":
            if self.movie_file.download(self.curr, self.job_manager):
                self.session.open(
                    MessageBox, "%s:\n\n%s\n" % (
                        _("Download added"),
                        self.curr[LIST_EVENT_NAME],
                    ),
                    type=MessageBox.TYPE_INFO,
                    timeout=4
                )
            else:
                self.session.open(
                    MessageBox, "%s:\n\n%s\n" % (
                        _("Download failed"),
                        _("Please check your movie directory in the plugin settings."),
                    ),
                    type=MessageBox.TYPE_ERROR,
                    timeout=4
                )
        else:
            self.session.open(MessageBox, _("No movie to download"),
                              type=MessageBox.TYPE_INFO, timeout=4)

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

    def checkMP4Structure(self, file_path):
        """Check if MP4 has progressive structure"""
        try:
            with open(file_path, 'rb') as f:
                # Read first 1KB to look for moov atom
                header = f.read(1024)
                if b'moov' in header[:100]:
                    logger.info("Progressive MP4 - can play during download")
                    return True
                logger.info("Standard MP4 - needs complete download for playback")
                return False
        except Exception:
            return False
