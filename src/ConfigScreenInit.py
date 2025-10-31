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
from .Debug import logger
from .__init__ import _


class ConfigScreenInit():
    def __init__(self, _parent, session):
        self.session = session
        self.section = 400 * "¯"
        self.config_list = [
            # text, config, on save, on ok, e2 usage level, depends on rel parent, description
            (self.section, _("COCKPIT"), None, None, 0, [], ""),
            (_("Entries in list"), config.plugins.mediathekcockpit.size, None, None, 0, [], _("Select the number of movies by download.")),
            (_("Show future movies"), config.plugins.mediathekcockpit.future, None, None, 0, [], _("Include future movies in list")),
            (_("Movie resolution"), config.plugins.mediathekcockpit.movie_resolution, None, None, 0, [], _("Select the resolution for movie download.")),
            (_("Download directory"), config.plugins.mediathekcockpit.movie_dir, self.validatePath, self.openLocationBox, 0, [], _("Select the directory the downloads are stored in.")),
            (self.section, _("FILTER"), None, None, 0, [], ""),
            (_("Skip 'Audio description'"), config.plugins.mediathekcockpit.skip_audiodeskription, None, None, 0, [], _("Skip movies with titles that contain 'Audio description'")),
            (_("Skip 'Trailer'"), config.plugins.mediathekcockpit.skip_trailer, None, None, 0, [], _("Skip movies with titles that contain 'Trailer'")),
            (_("Skip 'Sign language'"), config.plugins.mediathekcockpit.skip_gebaerdensprache, None, None, 0, [], _("Skip movies with titles that contain 'Sign language'")),
            (_("Skip short duration"), config.plugins.mediathekcockpit.skip_short_duration, None, None, 0, [], _("Skip movies with duration shorter than value specified in settings.")),
            (self.section, _("DEBUG"), None, None, 2, [], ""),
            (_("Log level"), config.plugins.mediathekcockpit.debug_log_level, self.setLogLevel, None, 2, [], _("Select the debug log level."))
        ]

    @staticmethod
    def save(_conf):
        logger.debug("...")

    def openLocationBox(self, element):
        logger.debug("element: %s", element.value)
        return True

    def setLogLevel(self, element):
        logger.debug("element: %s", element.value)
        return True

    def validatePath(self, element):
        logger.debug("element: %s", element.value)
        return True
