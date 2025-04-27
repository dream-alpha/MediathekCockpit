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
from urlparse import urljoin
from Components.Task import Task
from .Downloader import MyDownloadWithProgress, MyGetPage, _headers, headers_ts
from .Debug import logger
from .ParserMetaFile import ParserMetaFile
from .FileUtils import writeFile, deleteFile, touchFile
try:
    from Plugins.SystemPlugins.CacheCockpit.FileManager import FileManager
except Exception:
    logger.error("CacheCockpit import error")
    FileManager = None


def loadDatabaseFile(target_path, event_name, short_description, description, rec_time, service_ref):
    logger.info("target_path: %s, event_name: %s, short_description: %s, service_ref: %s", target_path, event_name, short_description, service_ref)
    file_name = os.path.splitext(target_path)[0]
    writeFile(file_name + ".txt", description)
    ParserMetaFile(target_path).updateMeta(
        {
            "service_reference": service_ref,
            "name": event_name,
            "description": short_description,
            "rec_time": rec_time
        }
    )
    if FileManager:
        FileManager.getInstance("MVC").loadDatabaseFile(target_path)


class DownloadTaskFile(Task):
    totalbytes = recvbytes = 0
    hls_segments = False

    def __init__(self, job, url, target_path, event_name, short_description, description, rec_time, service_ref):
        logger.info("job: %s, url: %s, target_path: %s, description: %s", job, url, target_path, description)
        self.url = url
        self.target_path = target_path
        self.event_name = event_name
        self.short_description = short_description
        self.description = description
        self.rec_time = rec_time
        self.service_ref = service_ref
        Task.__init__(self, job, "download task")

    def abort(self, *_args):
        logger.info("...")
        if self.download:
            self.download.stop()

    def run(self, callback):
        logger.info("...")
        self.callback = callback
        touchFile(self.target_path)
        loadDatabaseFile(self.target_path, self.event_name, self.short_description, self.description, self.rec_time, self.service_ref)
        self.download = MyDownloadWithProgress(url=self.url, fileOrName=self.target_path, headers=headers_ts)
        self.download.addProgress(self.http_progress)
        self.download.start().addCallback(self.http_finished).addErrback(self.http_failed)

    def http_progress(self, recvbytes, totalbytes):
        logger.info("...")
        self.progress = int(self.end * recvbytes / float(totalbytes))
        self.recvbytes, self.totalbytes = recvbytes, totalbytes

    def http_finished(self, _result):
        # logger.info("result: %s", _result)
        loadDatabaseFile(self.target_path, self.event_name, self.short_description, self.description, self.rec_time, self.service_ref)
        Task.processFinished(self, 0)

    def http_failed(self, failure_instance=None, error_message=""):
        logger.info("...")
        if error_message == "" and failure_instance is not None:
            error_message = failure_instance.getErrorMessage()
        logger.error("[DownloadTask].http_failed: %s", error_message)
        deleteFile(self.target_path)
        Task.processFinished(self, 1)


class DownloadTaskHLS(Task):
    totalbytes = recvbytes = 0
    hls_segments = True

    def __init__(self, job, url, segments, target_path, event_name, short_description, description, rec_time, service_ref):
        logger.info("job: %s, url: %s, target_path: %s, description: %s", job, url, target_path, description)
        self.url = url
        self.segments = segments
        self.target_path = target_path
        self.event_name = event_name
        self.short_description = short_description
        self.description = description
        self.rec_time = rec_time
        self.service_ref = service_ref
        Task.__init__(self, job, "download task")
        self.totalbytes = len(segments)
        self.current_deferred = None
        self.file_handle = None

    def abort(self, *_args):
        logger.info("...")
        self.segments = []
        if self.current_deferred and not self.current_deferred.called:
            self.current_deferred.cancel()
        if self.file_handle and not self.file_handle.closed:
            self.file_handle.close()
        self.finish()

    def run(self, callback):
        logger.info("...")
        self.callback = callback
        touchFile(self.target_path)
        loadDatabaseFile(self.target_path, self.event_name, self.short_description, self.description, self.rec_time, self.service_ref)
        self.file_handle = open(self.target_path, "wb")
        self.downloadSegment(str(urljoin(self.url, self.segments.pop(0)["uri"])))

    def downloadSegment(self, url):
        logger.info("url: %s", url)
        self.current_deferred = MyGetPage(url=url, headers=_headers, location=True)
        self.current_deferred.addCallback(self.http_finished).addErrback(self.http_failed)

    def http_finished(self, result):
        # logger.info("...")
        # logger.debug("segments: %s", self.segments)
        if result:
            self.file_handle.write(result[0])
        else:
            self.segments = []
        self.recvbytes += 1
        self.progress = int(round(self.end * self.recvbytes / float(self.totalbytes)))
        if self.segments:
            segment = self.segments.pop(0)
            logger.debug("segment: %s", segment)
            self.downloadSegment(str(urljoin(self.url, segment["uri"])))
        else:
            self.file_handle.close()
            loadDatabaseFile(self.target_path, self.event_name, self.short_description, self.description, self.rec_time, self.service_ref)
            Task.processFinished(self, 0)

    def http_failed(self, failure_instance=None, error_message=""):
        logger.info("...")
        if error_message == "" and failure_instance is not None:
            error_message = failure_instance.getErrorMessage()
        logger.error("[DownloadTask].http_failed: %s", error_message)
        deleteFile(self.target_path)
        Task.processFinished(self, 1)

    def finish(self):
        if self.file_handle and not self.file_handle.closed:
            self.file_handle.close()
