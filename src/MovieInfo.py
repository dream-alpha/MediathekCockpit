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


from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Components.Button import Button
from Components.Sources.List import List
from Components.ActionMap import HelpableActionMap
from .__init__ import _
from .SkinUtils import getSkinName
from .Constants import (
    LIST_DATE, LIST_EVENT_NAME, LIST_SHORT_DESCRIPTION, LIST_TIME, LIST_DURATION,
    LIST_CHANNEL, LIST_TITLE, LIST_TOPIC, LIST_DESCRIPTION, LIST_TIMESTAMP, LIST_SIZE,
    LIST_ID, LIST_URL_VIDEO_LOW, LIST_URL_VIDEO, LIST_URL_VIDEO_HD, LIST_URL_WEBSITE,
    LIST_CHANNEL_PIXMAP
)
from .Debug import logger


class MovieInfo(Screen, HelpableScreen):

    def __init__(self, session, row):
        self.row = row
        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        self.skinName = getSkinName("MovieInfo")

        self["actions"] = HelpableActionMap(
            self,
            "MTC_Actions",
            {
                "ok": (self.exit, _("Exit")),
                "cancel": (self.exit, _("Exit")),
                "red": (self.exit, _("Exit")),
                "green": (self.exit, _("Exit")),
            },
            prio=-1
        )

        self.setTitle(_("Movie Info"))
        self["list"] = List()
        self["key_green"] = Button(_("Exit"))
        self["key_red"] = Button(_("Cancel"))
        self["key_yellow"] = Button()
        self["key_blue"] = Button()
        self.onLayoutFinish.append(self.fillList)

    def exit(self):
        self.close()

    def fillList(self):
        logger.info("row: %s", self.row)
        alist = [
            ("0: CHANNEL", self.row[LIST_CHANNEL]),
            ("1: TOPIC", self.row[LIST_TOPIC]),
            ("2: TITLE", self.row[LIST_TITLE]),
            ("3: DESCRIPTION", self.row[LIST_DESCRIPTION]),
            ("4: TIME", self.row[LIST_TIME]),
            ("5: DATE", self.row[LIST_DATE]),
            ("6: DURATION", str(self.row[LIST_DURATION])),
            ("7: SIZE", str(self.row[LIST_SIZE])),
            ("8: CHANNEL_PIXMAP", self.row[LIST_CHANNEL_PIXMAP]),
            ("9: ID", self.row[LIST_ID]),
            ("10: URL_VIDEO_LOW", self.row[LIST_URL_VIDEO_LOW]),
            ("11: URL_VIDEO", self.row[LIST_URL_VIDEO]),
            ("12: URL_VIDEO_HD", self.row[LIST_URL_VIDEO_HD]),
            ("13: URL_WEBSITE", self.row[LIST_URL_WEBSITE]),
            ("14: TIMESTAMP", str(self.row[LIST_TIMESTAMP])),
            ("15: EVENT_NAME", self.row[LIST_EVENT_NAME]),
            ("16: SHORT_DESCRIPTION", self.row[LIST_SHORT_DESCRIPTION])
        ]
        self["list"].setList(alist)
        self["list"].master.downstream_elements.setSelectionEnabled(0)
