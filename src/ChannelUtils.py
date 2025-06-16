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


import json
from APIs.ServiceData import getServiceList
from Screens.ChannelSelection import service_types_tv
from .Debug import logger
from .FileUtils import readFile, writeFile


def getServiceReference(name):
    logger.info("name: %s", name)
    data = readFile(
        "/usr/lib/enigma2/python/Plugins/Extensions/MediathekCockpit/channels/mtc_service_refs.json")
    service_refs = json.loads(data)
    channel = service_refs.get(name, {})
    service_ref = channel.get("service", "")
    logger.debug("service_ref: %s", service_ref)
    return service_ref


def getServiceDict(bouquet=""):
    if not bouquet:
        bouquet = service_types_tv
    # bouquet = "Alle Sender (Enigma)"
    service_types = bouquet + " " + "ORDER BY name"
    service_list = getServiceList(service_types)
    logger.debug("service_list: %s", service_list)
    if service_list:
        service_dict = {}
        for service, name in service_list:
            if "::" not in service:
                service_dict[name] = service
    # service_dict = convertUnicode2Str(service_dict)
    data = json.dumps(service_dict, indent=6)
    writeFile("/etc/enigma2/mtc_service_dict.json", data)
    return service_dict
