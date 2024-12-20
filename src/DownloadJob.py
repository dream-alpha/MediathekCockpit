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


from Components.Task import Job
from .Debug import logger
from .DownloadTask import DownloadTaskFile, DownloadTaskHLS


class DownloadJob(Job):

	def __init__(self, url, segments, file_name, event_name, short_description, description, rec_time, service_ref):
		logger.info("file_name: %s, event_name: %s, short_description: %s", file_name, event_name, short_description)
		logger.debug("segments: %s", segments)
		Job.__init__(self, "Download: " + event_name)
		self.file_name = file_name
		self.keep = True
		if segments:
			DownloadTaskHLS(self, url, segments, file_name, event_name, short_description, description, rec_time, service_ref)
		else:
			DownloadTaskFile(self, url, file_name, event_name, short_description, description, rec_time, service_ref)

	def gettotalbytes(self):
		t = self.tasks[self.current_task]
		return int(t.totalbytes)

	totalbytes = property(gettotalbytes)

	def getrecvbytes(self):
		t = self.tasks[self.current_task]
		return int(t.recvbytes)

	recvbytes = property(getrecvbytes)

	def gethls_segments(self):
		t = self.tasks[self.current_task]
		return t.hls_segments

	hls_segments = property(gethls_segments)
