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


import json
from Screens.ChoiceBox import ChoiceBox
from .WebRequests import WebRequests
from .Debug import logger
from .__init__ import _


class ChannelSelection():
    def __init__(self):
        return

    def openChannelSelection(self):
        logger.info("...")
        url = "https://mediathekviewweb.de/api/channels"
        channel_list = json.loads(
            WebRequests().getContent(url)).get("channels", [])
        choices = [(_("All channels"),)]
        for channel in channel_list:
            choices.append((str(channel),))
        self.session.openWithCallback(
            self.openChannelSelectionCallback,
            ChoiceBox,
            title=_("Channel selection"),
            list=choices,
            titlebartext="MediathekCockpit" + " - " + _("Channel selection"),
            keys=[]
        )

    def openChannelSelectionCallback(self, selection):
        logger.info("selection: %s", selection)
        if selection:
            channel = selection[0]
            if channel == _("All channels"):
                if "queries" in self.postdata:
                    del self.postdata["queries"]
                channel = None
            else:
                self.postdata["queries"] = [
                    {"fields": ["channel"], "query": channel}]
            self.postdata["offset"] = 0
            self.downloadMovieList(channel)
