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
VIDEO_RESOLUTIONS_DICT = {LIST_URL_VIDEO_HD: _(
    "High"), LIST_URL_VIDEO: _("Medium"), LIST_URL_VIDEO_LOW: _("Low")}

choices_date = [
    ("%d.%m.%Y", _("DD.MM.YYYY")),
    ("%a %d.%m.%Y", _("WD DD.MM.YYYY")),

    ("%d.%m.%Y %H:%M", _("DD.MM.YYYY HH:MM")),
    ("%a %d.%m.%Y %H:%M", _("WD DD.MM.YYYY HH:MM")),

    ("%d.%m. %H:%M", _("DD.MM. HH:MM")),
    ("%a %d.%m. %H:%M",	_("WD DD.MM. HH:MM")),

    ("%Y/%m/%d", _("YYYY/MM/DD")),
    ("%a %Y/%m/%d", _("WD YYYY/MM/DD")),

    ("%Y/%m/%d %H:%M", _("YYYY/MM/DD HH:MM")),
    ("%a %Y/%m/%d %H:%M", _("WD YYYY/MM/DD HH:MM")),

    ("%m/%d %H:%M", _("MM/DD HH:MM")),
    ("%a %m/%d %H:%M", _("WD MM/DD HH:MM"))
]


class ConfigInit():

    def __init__(self):
        logger.info("...")
        config.plugins.mediathekcockpit = ConfigSubsection()
        config.plugins.mediathekcockpit.fake_entry = NoSave(ConfigNothing())
        config.plugins.mediathekcockpit.debug_log_level = ConfigSelection(
            default="INFO", choices=list(log_levels.keys()))
        config.plugins.mediathekcockpit.size = ConfigSelectionNumber(
            min=12, max=1200, stepwidth=12, default=120)
        config.plugins.mediathekcockpit.future = ConfigYesNo(default=False)
        config.plugins.mediathekcockpit.askstopmovie = ConfigSelection(
            default="quit", choices=[("quit", _("Do nothing")), ("ask", _("Ask user"))])
        config.plugins.mediathekcockpit.movie_resolution = ConfigSelection(default=str(LIST_URL_VIDEO_HD), choices=[(
            str(LIST_URL_VIDEO_LOW), _("Low")), (str(LIST_URL_VIDEO), _("Medium")), (str(LIST_URL_VIDEO_HD), _("High"))])
        config.plugins.mediathekcockpit.skip_audiodeskription = ConfigYesNo(
            default=True)
        config.plugins.mediathekcockpit.skip_trailer = ConfigYesNo(
            default=True)
        config.plugins.mediathekcockpit.skip_gebaerdensprache = ConfigYesNo(
            default=True)
        config.plugins.mediathekcockpit.skip_short_duration = ConfigSelectionNumber(
            0, 60, 1, default=5)
        config.plugins.mediathekcockpit.movie_dir = ConfigDirectory(
            default="/media/hdd/movie")
        config.plugins.mediathekcockpit.movie_date_format = ConfigSelection(
            default="%d.%m.%Y %H:%M", choices=choices_date)
        config.plugins.mediathekcockpit.movie_resume_at_last_pos = ConfigYesNo(
            default=False)
        config.plugins.mediathekcockpit.movie_start_position = ConfigSelection(default="beginning", choices=[(
            "beginning", _("beginning")), ("first_mark", _("first mark")), ("event_start", _("event start"))])

        initLogging()
