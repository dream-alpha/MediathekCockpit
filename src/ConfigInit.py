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


from Components.config import config, ConfigSelection, ConfigSelectionNumber, ConfigYesNo, ConfigDirectory, ConfigSubsection, ConfigNothing, NoSave
from .Debug import logger, log_levels, initLogging
from .__init__ import _

from .Constants import LIST_URL_VIDEO_LOW, LIST_URL_VIDEO, LIST_URL_VIDEO_HD


VIDEO_RESOLUTIONS = [LIST_URL_VIDEO_HD, LIST_URL_VIDEO, LIST_URL_VIDEO_LOW]
VIDEO_RESOLUTIONS_DICT = {LIST_URL_VIDEO_HD: _("High"), LIST_URL_VIDEO: _("Medium"), LIST_URL_VIDEO_LOW: _("Low")}


class ConfigInit():

	def __init__(self):
		logger.info("...")
		config.plugins.mediathekcockpit = ConfigSubsection()
		config.plugins.mediathekcockpit.fake_entry = NoSave(ConfigNothing())
		config.plugins.mediathekcockpit.debug_log_level = ConfigSelection(default="INFO", choices=list(log_levels.keys()))
		config.plugins.mediathekcockpit.size = ConfigSelectionNumber(min=50, max=1500, stepwidth=50, default=500)
		config.plugins.mediathekcockpit.future = ConfigYesNo(default=False)
		config.plugins.mediathekcockpit.askstopmovie = ConfigSelection(default="quit", choices=[("quit", _("Do nothing")), ("ask", _("Ask user"))])
		config.plugins.mediathekcockpit.movie_resolution = ConfigSelection(default=str(LIST_URL_VIDEO_HD), choices=[(str(LIST_URL_VIDEO_LOW), _("Low")), (str(LIST_URL_VIDEO), _("Medium")), (str(LIST_URL_VIDEO_HD), _("High"))])
		config.plugins.mediathekcockpit.movie_dir = ConfigDirectory(default="/media/hdd/movie")
		initLogging()
