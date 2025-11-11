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
from Screens.VirtualKeyBoard import VirtualKeyBoard
from .Query import getSeriesEpisode
from .Debug import logger
from .__init__ import _


class Search():
    def __init__(self):
        self.postdata = {
            "sortOrder": "desc",
            "sortBy": "timestamp",
            "offset": 0,
            "size": config.plugins.mediathekcockpit.size.value,
            "future": config.plugins.mediathekcockpit.future.value
        }

    def openKeyboard(self, query):
        logger.info("query: %s", query)
        series_episode = getSeriesEpisode(query)
        if series_episode:
            query = query.replace(series_episode, "").strip()
        self.session.openWithCallback(self.openKeyboardCallback, VirtualKeyBoard, title=_(
            "Enter search text"), text=query)

    def openKeyboardCallback(self, result):
        logger.info("result: %s", result)
        if result is None:
            result = ""
        fields = ["topic", "title"]
        self.postdata["offset"] = 0
        self.postdata["future"] = config.plugins.mediathekcockpit.future.value
        self.postdata["queries"] = [{"fields": fields, "query": result}]
        self.downloadMovieList()
