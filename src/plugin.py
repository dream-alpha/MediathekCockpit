# coding=utf-8

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


from Plugins.Plugin import PluginDescriptor
from .ConfigInit import ConfigInit
from .SkinUtils import loadPluginSkin
from .Debug import logger
from .Version import VERSION
from .MediathekCockpit import MediathekCockpit
from .PluginUtils import WHERE_MEDIATHEK_SEARCH
from . import _


def main(session, query="", **__kwargs):
    logger.info("...")
    session.open(MediathekCockpit, query)


def showDownloads(session, event="", service="", **_kwargs):
    logger.info("...")
    if not service:
        service = session.nav.getCurrentService()
    info = service.info()
    if not event:
        event = info.getEvent(0)  # 0 = now, 1 = next
    event_name = event and event.getEventName() or info.getName() or ""
    logger.info("event_name: %s", event_name)
    session.open(MediathekCockpit, event_name)


def autoStart(reason, **kwargs):
    if reason == 0:  # startup
        if "session" in kwargs:
            logger.info("+++ Version: %s starts...", VERSION)
            loadPluginSkin("skin.xml")
    elif reason == 1:  # shutdown
        logger.info("--- shutdown")


def Plugins(**__kwargs):
    ConfigInit()
    return [
        PluginDescriptor(
            where=[
                PluginDescriptor.WHERE_AUTOSTART,
                PluginDescriptor.WHERE_SESSIONSTART
            ],
            fnc=autoStart
        ),
        PluginDescriptor(
            name="MediathekCockpit",
            where=PluginDescriptor.WHERE_PLUGINMENU,
            icon="MediathekCockpit.png",
            description=_("Browse Mediathek libraries"),
            fnc=main
        ),
        PluginDescriptor(
            name=_("Mediathek Downloads"),
            description=_("Mediathek Downloads"),
            where=[
                PluginDescriptor.WHERE_EPG_SELECTION_SINGLE_BLUE,
                PluginDescriptor.WHERE_EVENTINFO,
                PluginDescriptor.WHERE_EVENTVIEW,
            ],
            fnc=showDownloads
        ),
        PluginDescriptor(
            name=_("MediathekCockpit"),
            description=_("Mediathek Downloads"),
            where=WHERE_MEDIATHEK_SEARCH,
            fnc=main
        ),
    ]
