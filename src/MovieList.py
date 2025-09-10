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


from Components.Sources.List import List
from .Query import Query
from .Debug import logger
from .__init__ import _


ROWS = 12


class MovieList(Query):
    def __init__(self, parent):
        self.parent = parent
        Query.__init__(self)
        self.parent["list"] = List()
        self.list = []
        self.index = 0
        self.total_results = 0
        self.pages = 0

    def getList(self, postdata, channel=None):
        logger.info("postdata: %s", postdata)
        self.postdata = postdata
        self.channel = channel
        offset = postdata.get("offset", 0)
        if offset == 0:
            self.list = []
            self.index = 0
        alist, self.total_results = self.download(postdata, channel)
        self.list += alist
        logger.debug("list: %s", self.list)
        self.parent["list"].setList(self.list)
        self.parent["list"].index = self.index
        self.pages = (self.total_results + ROWS - 1) // ROWS
        self.updateTitle()

    def getCurrentSelection(self):
        if self.parent["list"].getCurrent() is not None:
            return self.parent["list"].getCurrent()
        return None

    def up(self):
        if self.index > 0:
            self.index -= 1
            self.parent["list"].index = self.index
        else:
            logger.warning("Already at the first item in the list.")
        self.updateTitle()

    def down(self):
        self.index += 1
        if self.index < len(self.list):
            self.parent["list"].index = self.index
        else:
            self.postdata["offset"] = self.index
            self.getList(self.postdata, self.channel)
        self.updateTitle()

    def left(self):
        self.index = max(0, self.index - ROWS)
        self.parent["list"].index = self.index
        self.updateTitle()

    def right(self):
        self.index += ROWS
        if self.index + ROWS < len(self.list):
            logger.debug("index is still within the list bounds.")
            self.parent["list"].index = self.index
        else:
            self.postdata["offset"] = len(self.list)
            self.getList(self.postdata, self.channel)
        self.updateTitle()

    def updateTitle(self):
        page = self.index // ROWS
        if self.list:
            self.parent.title = self.parent.title_base + " - " + _("Page") + ": " + "%d/%d" % (page + 1, self.pages)
        else:
            self.parent.title = self.parent.title_base + " - " + _("No movies available")
        logger.info("Updated title: %s", self.parent.title)
