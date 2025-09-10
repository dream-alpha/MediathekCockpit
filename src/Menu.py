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
from Screens.ChoiceBox import ChoiceBox
from .ConfigScreen import ConfigScreen
from .About import about
from .Debug import logger
from .PluginUtils import WHERE_JOBCOCKPIT, getPlugin
from .Version import ID
from .__init__ import _


class Menu():
    def __init__(self):
        self.menu = [
            (_("Download Manager"), self.showDownloadManager),
            (_("Settings"), self.showSettings),
            (_("About"), self.showAbout)
        ]

    def openMenu(self):
        self.session.openWithCallback(
            self.openMenuCallback,
            ChoiceBox,
            title=_("Functions"),
            list=self.menu,
            titlebartext="MediathekCockpit" + " - " + _("Menu")
        )

    def openMenuCallback(self, selection):
        logger.info("...")
        if selection:
            selection[1]()

    def showDownloadManager(self):
        logger.info("...")
        plugin = getPlugin(WHERE_JOBCOCKPIT)
        if plugin:
            logger.debug("plugin.name: %s", plugin.name)
            plugin(self.session, ID)

    def showSettings(self):
        logger.info("...")
        self.session.openWithCallback(
            self.showSettingsCallback, ConfigScreen, config.plugins.mediathekcockpit)

    def showSettingsCallback(self, changed=None):
        logger.info("...")
        if changed:
            self.postdata["size"] = int(
                config.plugins.mediathekcockpit.size.value)
            self.postdata["future"] = config.plugins.mediathekcockpit.future.value
            self.postdata["offset"] = 0

    def showAbout(self):
        logger.info("...")
        about(self.session)
