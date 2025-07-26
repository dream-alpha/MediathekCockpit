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
from Tools.BoundFunction import boundFunction
from .Debug import logger
from .__init__ import _
from .Version import PLUGIN, ID
from .EventView import EventView
from .Menu import Menu
from .ChannelSelection import ChannelSelection
from .Constants import LIST_EVENT_NAME, LIST_DURATION, LIST_TOPIC, LIST_DESCRIPTION
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


class MediathekCockpit(Screen, Menu, ChannelSelection, Search):
    def __init__(self, session, query):
        self.query = query
        Screen.__init__(self, session)
        self.skinName = "MediathekCockpit"
        Menu.__init__(self)
        ChannelSelection.__init__(self)
        Search.__init__(self)
        self.movie_file = MovieFile()
        self.movie_list = MovieList(self)
        self.service_center = ServiceCenter(self["list"])
        self.last_service = self.session.nav.getCurrentlyPlayingServiceReference()
        self.title_base = PLUGIN + " - " + _("Movies") + " - " + _("Search results")
        self.title = self.title_base + " - " + _("Downloading movies...")

        self["key_red"] = StaticText(_("Exit"))
        self["key_green"] = StaticText(_("Channels"))
        self["key_yellow"] = StaticText(_("Download"))
        self["key_blue"] = StaticText(_("Search"))

        self["description"] = Label("")
        self["duration"] = Label("")

        self["actions"] = ActionMap(
            ["CockpitActions"],
            {
                "OK": self.pressOk,
                "EXIT": self.pressClose,
                "RED": self.pressRed,
                "GREEN": self.pressGreen,
                "YELLOW": self.pressYellow,
                "BLUE": self.pressBlue,
                "MENU": self.openMenu,
                "INFO": self.pressInfo,
                "UP": self.movie_list.up,
                "DOWN": self.movie_list.down,
                "LEFTR": self.movie_list.left,
                "RIGHTR": self.movie_list.right,
                "5": self.showMovieInfo
            }
        )

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

    def __onSelectionChanged(self):
        logger.info("...")
        self["description"].setText("")
        self["duration"].setText("")
        curr = self.movie_list.getCurrentSelection()
        logger.debug("curr: %s", curr)
        if curr:
            self["description"].setText(curr[LIST_DESCRIPTION])
            self["duration"].setText("%s: %s %s" % (_("Duration"), curr[LIST_DURATION] / 60, _("Minutes")))

    def downloadMovieList(self, channel=None):
        logger.info("postdata: %s", self.postdata)
        self.movie_list.getList(self.postdata, channel)

    def playMovie(self, curr, url, path):
        logger.info("url: %s, path: %s", url, path)
        stream = not self.movie_file.checkMP4Structure(path)
        logger.debug("Stream mode: %s", stream)
        uri = url if stream else path
        if uri:
            logger.debug("Playing movie from URI: %s", uri)
            service = getService(uri, curr[LIST_EVENT_NAME])
            self.session.openWithCallback(boundFunction(self.playMovieCallback, path), CockpitPlayer, service,
                                          config.plugins.mediathekcockpit, self.pressInfo, service_center=self.service_center, stream=stream)
        else:
            self.session.open(MessageBox, _("Unsupported video format or no valid stream detected."), type=MessageBox.TYPE_ERROR, timeout=4)

    def playMovieCallback(self, path):
        jobs = getPendingJobs("TMP")
        if jobs:
            for job in jobs:
                JobCockpit.abortJob(job, "TMP", True)
            callLater(0, self.session.nav.playService, self.last_service)
        else:
            deleteFile(path)

    def pressOk(self):
        curr = self.movie_list.getCurrentSelection()
        if curr:
            url, recording_path = self.movie_file.download(curr, self.tmp_job_manager)
            if recording_path and url:
                callLater(3, self.playMovie, curr, url, recording_path)
            else:
                self.session.open(MessageBox, _("No valid stream detected."), type=MessageBox.TYPE_ERROR, timeout=4)

    def pressRed(self):
        logger.info("...")
        self.pressClose()

    def pressGreen(self):
        logger.info("...")
        self.openChannelSelection()

    def pressYellow(self):
        logger.info("...")
        curr = self.movie_list.getCurrentSelection()
        if curr:
            if self.movie_file.download(curr, self.job_manager):
                self.session.open(
                    MessageBox,
                    "%s:\n\n%s" % (_("Download added"), curr[LIST_EVENT_NAME]),
                    type=MessageBox.TYPE_INFO,
                    timeout=4
                )
            else:
                self.session.open(
                    MessageBox,
                    "%s:\n\n%s" % (_("Download failed"), _("Please check movie directory in plugin settings.")),
                    type=MessageBox.TYPE_ERROR,
                    timeout=4
                )

    def pressBlue(self):
        logger.info("...")
        query = ""
        curr = self.movie_list.getCurrentSelection()
        if curr:
            query = curr[LIST_TOPIC]
            self.openKeyboard(query)

    def pressInfo(self):
        curr = self.movie_list.getCurrentSelection()
        if curr:
            self.session.open(EventView, curr)

    def pressClose(self):
        logger.info("...")
        self.close()

    def showMovieInfo(self):
        logger.info("...")
        curr = self.movie_list.getCurrentSelection()
        self.session.open(MovieInfo, curr)
