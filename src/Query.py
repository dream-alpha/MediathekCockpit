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
from time import localtime, strftime
from datetime import datetime
from Components.config import config
from Tools.LoadPixmap import LoadPixmap
from .WebRequests import WebRequests
from .UnicodeUtils import convertUni2Str
from .Constants import (
    plugindir, LIST_URL_VIDEO_LOW, LIST_URL_VIDEO, LIST_URL_VIDEO_HD, LIST_DATE, LIST_EVENT_NAME, LIST_SHORT_DESCRIPTION, LIST_TIME, LIST_DURATION, LIST_CHANNEL, LIST_CHANNEL_PIXMAP, LIST_TOPIC, LIST_TITLE, LIST_DESCRIPTION, LIST_SIZE, LIST_ID, LIST_URL_WEBSITE, LIST_TIMESTAMP, LIST_END
)
from .Debug import logger


def getSeriesEpisode(text):
    """
    Extracts the episode number from a given text.
    Handles format: "foo (Snn/Enn) bar"
    """

    logger.info("text: %s", text)
    text = text.strip()
    if "(" in text and ")" in text:
        start_idx = text.rfind("(")
        end_idx = text.find(")", start_idx)
        if 0 <= start_idx < end_idx:
            inside_parens = text[start_idx + 1:end_idx]
            if inside_parens.startswith("S") and "/E" in inside_parens:
                s_e_parts = inside_parens.split("/E")
                if len(s_e_parts) == 2:
                    season_part = s_e_parts[0]
                    episode_part = s_e_parts[1]
                    if season_part.startswith("S"):
                        season_num = season_part[1:].strip()
                        episode_num = episode_part.strip()
                        return "(S%s/E%s)" % (season_num, episode_num)
    return ""


class Query:
    def __init__(self):
        return

    def download(self, postdata, channel=None):
        logger.info("postdata: %s", postdata)
        # result_count = 0
        total_results = 0
        alist = []
        url = "https://mediathekviewweb.de/api/query"
        result = WebRequests().postContent(url, postdata)
        if result.text:
            data = convertUni2Str(json.loads(result.text))
            # logger.debug("data: %s", data)
            results = data["result"]["results"]
            logger.debug("results: %s", results)
            for x in results:
                row = self.getMovieRow(x)
                title = row[LIST_TITLE]
                topic = row[LIST_TOPIC]
                title_topic = title + topic
                skip = False
                if channel and channel.lower() != row[LIST_CHANNEL].lower():
                    continue
                if row[LIST_DURATION] < int(config.plugins.mediathekcockpit.skip_short_duration.value) * 60:
                    continue
                if config.plugins.mediathekcockpit.skip_audiodeskription.value:
                    skip |= "Audiodeskription" in title_topic
                if config.plugins.mediathekcockpit.skip_trailer.value:
                    skip |= "Trailer" in title_topic
                if config.plugins.mediathekcockpit.skip_gebaerdensprache.value:
                    skip |= "Gebärdensprache" in title_topic
                if not skip:
                    alist.append(row)
                else:
                    logger.debug("Skipping movie: %s", title_topic)

            query_info = data["result"]["queryInfo"]
            query_info["filmlisteTimestamp"] = strftime(
                "%d.%m.%Y %H:%M:%S", localtime(int(query_info["filmlisteTimestamp"])))
            # logger.debug("query_info: %s", query_info)
            total_results = query_info["totalResults"]
            # result_count = query_info["resultCount"]

        logger.info("alist: %s", alist)
        return alist, total_results

    def getMovieRow(self, x):
        logger.debug("x: %s", x)
        row = [""] * LIST_END
        row[LIST_TIMESTAMP] = timestamp = int(x.get("timestamp", "0"))
        row_datetime = datetime.fromtimestamp(
            timestamp).strftime("%d.%m.%Y %H:%M:%S")
        row[LIST_DATE] = row_datetime[0:10]
        row[LIST_TIME] = row_datetime[11:16]
        row[LIST_DURATION] = int(x.get("duration", 0))
        row[LIST_CHANNEL] = channel = x.get("channel", "")
        row[LIST_CHANNEL_PIXMAP] = LoadPixmap(
            "%slogos/%s.png" % (plugindir, channel.replace(" ", "").upper())) if channel else None
        topic = x.get("topic", "")
        title = x.get("title", "")
        logger.debug("topic: %s, title: %s", topic, title)
        if title.startswith(topic):
            title = title.replace(topic, "").strip()
        series_episode = getSeriesEpisode(title)
        logger.debug("series_episode: %s", series_episode)
        if series_episode:
            title = title.replace(series_episode, "").strip()
            topic = topic + " " + series_episode
        if title.startswith(": "):
            title = title[2:].strip()
        if title.startswith("| "):
            title = title[2:].strip()
        if title.startswith("- "):
            title = title[2:].strip()
        row[LIST_TOPIC] = topic
        row[LIST_TITLE] = title
        # row[LIST_EVENT_NAME] = topic + " - " + title if title else topic
        row[LIST_EVENT_NAME] = topic if topic else title
        row[LIST_SHORT_DESCRIPTION] = title if row[LIST_EVENT_NAME] != title else ""
        description = x.get("description", "")
        if description.endswith("....."):
            description = description.replace(".....", "")
            fullstop_idx = description.rfind(".")
            question_idx = description.rfind("?")
            exclamation_idx = description.rfind("!")
            idx = max(fullstop_idx, question_idx, exclamation_idx)
            if 0 < idx < len(description) - 1:
                description = description[:idx + 1]
        row[LIST_DESCRIPTION] = description
        size = x.get("size", 0)
        row[LIST_SIZE] = int(size) if size is not None else 0
        row[LIST_ID] = x.get("id", "")
        row[LIST_URL_VIDEO_LOW] = x.get("url_video_low", "")
        row[LIST_URL_VIDEO] = x.get("url_video", "")
        row[LIST_URL_VIDEO_HD] = x.get("url_video_hd", "")
        row[LIST_URL_WEBSITE] = x.get("url_website", "")
        logger.debug("row: %s", row)
        return row
