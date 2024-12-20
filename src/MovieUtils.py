# !/usr/bin/python
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


import os
from datetime import datetime
from urlparse import urljoin
from . import m3u8
from .Debug import logger
from .ConfigInit import VIDEO_RESOLUTIONS, VIDEO_RESOLUTIONS_DICT
from .Constants import (
	plugindir, LIST_URL_VIDEO_LOW, LIST_URL_VIDEO, LIST_URL_VIDEO_HD, LIST_DATE, LIST_EVENT_NAME, LIST_SHORT_DESCRIPTION, LIST_TIME, LIST_DURATION, LIST_CHANNEL, LIST_CHANNEL_PIXMAP, LIST_TOPIC, LIST_TITLE, LIST_DESCRIPTION, LIST_SIZE, LIST_ID, LIST_URL_WEBSITE, LIST_TIMESTAMP, LIST_END
)
from .__init__ import _
from Tools.LoadPixmap import LoadPixmap


def getMovieRow(x):
	logger.debug("x: %s", x)
	row = [""] * LIST_END
	row[LIST_TIMESTAMP] = timestamp = int(x.get("timestamp", "0"))
	row_datetime = datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y %H:%M:%S")
	row[LIST_DATE] = row_datetime[0:10]
	row[LIST_TIME] = row_datetime[11:16]
	row[LIST_DURATION] = "%s" % str(int(x.get("duration", 0)) / 60) + " " + _("Minutes")
	row[LIST_CHANNEL] = channel = x.get("channel", "")
	row[LIST_CHANNEL_PIXMAP] = LoadPixmap("%slogos/%s.png" % (plugindir, channel.replace(" ", "").upper())) if channel else None
	topic = x.get("topic", "")
	title = x.get("title", "")
	if title.startswith(topic):
		title = title.replace(topic, "").strip()
		if title.startswith("-"):
			title = title[1:].strip()
	row[LIST_TOPIC] = topic
	row[LIST_TITLE] = title
	row[LIST_EVENT_NAME] = topic + " - " + title if title else topic
	row[LIST_SHORT_DESCRIPTION] = title
	row[LIST_DESCRIPTION] = x.get("description", "")
	size = x.get("size", 0)
	row[LIST_SIZE] = int(size) / (1024 * 1024) if size is not None else 0
	row[LIST_ID] = x.get("id", "")
	row[LIST_URL_VIDEO_LOW] = x.get("url_video_low", "")
	row[LIST_URL_VIDEO] = x.get("url_video", "")
	row[LIST_URL_VIDEO_HD] = x.get("url_video_hd", "")
	row[LIST_URL_WEBSITE] = x.get("url_website", "")
	logger.debug("row: %s", row)
	return row


def getNextRow():
	row = [""] * LIST_END
	row[LIST_CHANNEL] = ">>>"
	row[LIST_EVENT_NAME] = _("Next page")
	row[LIST_SHORT_DESCRIPTION] = _("Select")
	row[LIST_DATE] = ">>>"
	row[LIST_CHANNEL_PIXMAP] = None
	logger.debug("row: %s", row)
	return row


def getVideoResolutions(curr):
	def checkVideoUrl(was, curr):
		return curr[was] and curr[was].startswith("http")

	resolutions = []
	if checkVideoUrl(LIST_URL_VIDEO_LOW, curr):
		resolutions.append(_("Low"))
	if checkVideoUrl(LIST_URL_VIDEO, curr):
		resolutions.append(_("Medium"))
	if checkVideoUrl(LIST_URL_VIDEO_HD, curr):
		resolutions.append(_("High"))
	return resolutions


def getVideoUrl(curr, val):
	url = ""
	resolution_text = ""
	resolutions = [val] + VIDEO_RESOLUTIONS
	for resolution in resolutions:
		if curr[resolution] and curr[resolution].startswith("http"):
			url = curr[resolution]
			resolution_text = VIDEO_RESOLUTIONS_DICT[resolution]
			break
	return url, resolution_text


def getPlaylistSegments(url):
	file_url = os.path.dirname(url)
	ext = os.path.splitext(file_url)[1]
	logger.debug("ext: %s", ext)
	playlist = m3u8.load(url)
	logger.debug("base_path: %s, base_uri: %s, data: %s", playlist.base_path, playlist.base_uri, playlist.data)
	url = playlist.base_uri
	playlist = m3u8.load(urljoin(url, playlist.data["playlists"][0]["uri"]))
	logger.debug("base_path: %s, base_uri: %s, data: %s", playlist.base_path, playlist.base_uri, playlist.data)
	segments = playlist.data["segments"]
	logger.debug("segments: %s", segments)
	return segments
