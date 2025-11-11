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


from datetime import datetime
from enigma import iServiceInformation
from Components.config import config
from .Debug import logger
from .Constants import (
    LIST_EVENT_NAME, LIST_SHORT_DESCRIPTION, LIST_DESCRIPTION, LIST_TIMESTAMP,
    LIST_DURATION, LIST_SIZE
)


class ServiceCenter():

    def __init__(self, movie_list):
        self.movie_list = movie_list
        logger.debug("...")

    def info(self, service):
        logger.debug("...")
        return ServiceInfo(service, self.movie_list)


class ServiceInfo():

    def __init__(self, service, movie_list=None):
        logger.debug("service.getPath(): %s",
                     service.getPath() if service else None)
        self.info = Info(service, movie_list)

    def getLength(self, _service=None):
        logger.debug("..")
        return self.info.getLength()

    def getInfoString(self, _service=None, info_type=None):
        logger.debug("info_type: %s", info_type)
        if info_type == iServiceInformation.sServiceref:
            return self.info.getServiceReference()
        if info_type == iServiceInformation.sDescription:
            return self.info.getShortDescription()
        if info_type == iServiceInformation.sTags:
            return self.info.getTags()
        return None

    def getInfo(self, _service=None, info_type=None):
        logger.debug("info_type: %s", info_type)
        if info_type == iServiceInformation.sTimeCreate:
            return self.info.getEventStartTime()
        return None

    def getInfoObject(self, _service=None, info_type=None):
        logger.debug("info_type: %s", info_type)
        if info_type == iServiceInformation.sFileSize:
            return self.info.getSize()
        return None

    def getName(self, _service=None):
        logger.debug("...")
        return self.info.getName()

    def getEvent(self, _service=None):
        logger.debug("...")
        return self.info

    def getCover(self):
        logger.debug("...")
        return self.info.getCover()


class Info():

    def __init__(self, service, movie_list=None):
        logger.info("...")
        self.path = service.getPath()
        self.afile = movie_list and movie_list.getCurrent()

    def getName(self):
        # EventName NAME
        name = ""
        if self.afile:
            name = self.afile[LIST_EVENT_NAME]
        logger.debug("name: %s", name)
        return name

    def getServiceReference(self):
        logger.debug("...")
        service_reference = ""
        return service_reference

    def getTags(self):
        logger.debug("...")
        tags = ""
        if self.afile:
            # tags = self.afile[FILE_IDX_TAGS]
            tags = ""
        return tags

    def getEventId(self):
        logger.debug("...")
        return 0

    def getEventName(self):
        logger.debug("...")
        return self.getName()

    def getShortDescription(self):
        logger.debug("...")
        # EventName SHORT_DESCRIPTION
        short_description = ""
        if self.afile:
            short_description = self.afile[LIST_SHORT_DESCRIPTION]
        return short_description

    def getExtendedDescription(self):
        logger.debug("...")
        # EventName EXTENDED_DESCRIPTION
        extended_description = ""
        if self.afile:
            extended_description = self.afile[LIST_DESCRIPTION]
        return extended_description

    def getBeginTimeString(self):
        logger.debug("...")
        stime = ""
        event_start_time = self.getEventStartTime()
        if event_start_time:
            movie_date_format = config.plugins.mediathekcockpit.movie_date_format.value
            stime = datetime.fromtimestamp(
                event_start_time).strftime(movie_date_format)
        return stime

    def getEventStartTime(self):
        logger.debug("...")
        event_start_time = 0
        if self.afile:
            event_start_time = self.afile[LIST_TIMESTAMP]
        return event_start_time

    def getRecordingStartTime(self):
        logger.debug("...")
        recording_start_time = 0
        if self.afile:
            recording_start_time = self.afile[LIST_TIMESTAMP]
        return recording_start_time

    def getDuration(self):
        logger.debug("...")
        duration = 0
        if self.afile:
            duration = self.afile[LIST_DURATION]
        return duration

    def getLength(self):
        return self.getDuration()

    def getSize(self):
        logger.debug("...")
        size = self.afile[LIST_SIZE]  # No null check!
        return size

    def getCover(self):
        logger.debug("...")
        cover = ""
        return cover
