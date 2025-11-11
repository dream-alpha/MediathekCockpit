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
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from .Debug import logger
from .__init__ import _
from .Constants import LIST_EVENT_NAME, LIST_SHORT_DESCRIPTION, LIST_DESCRIPTION, LIST_DATE, LIST_DURATION, LIST_CHANNEL, LIST_TIME


class EventView(Screen):

    def __init__(self, session, curr):
        logger.info("...")
        Screen.__init__(self, session, windowTitle=curr[LIST_EVENT_NAME])
        self.skinName = "EventView"
        self["actions"] = ActionMap(
            ["MTC_Actions", "OkCancelActions", "ChannelSelectEPGActions"],
            {
                "red": self.close,
                "ok": self.close,
                "cancel": self.close,
                "showEPGList": self.close
            }
        )
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button()
        self["key_yellow"] = Button()
        self["key_blue"] = Button()
        epg_description = curr[LIST_EVENT_NAME]
        if curr[LIST_SHORT_DESCRIPTION]:
            epg_description += "\n\n" + curr[LIST_SHORT_DESCRIPTION]
        epg_description += "\n\n" + curr[LIST_DESCRIPTION]
        self["epg_description"] = ScrollLabel(epg_description)
        self["datetime"] = Label(curr[LIST_DATE] + " " + curr[LIST_TIME])
        self["duration"] = Label(
            str(curr[LIST_DURATION] / 60) + " " + _("min"))
        self["channel"] = Label(curr[LIST_CHANNEL])
