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
from Components.config import config
from .Constants import LIST_CHANNEL, LIST_TIMESTAMP, LIST_EVENT_NAME, LIST_SHORT_DESCRIPTION, LIST_DESCRIPTION, LIST_DURATION, LIST_URL_WEBSITE
from .ChannelUtils import getServiceReference
from .RecordingUtils import calcRecordingFilename
from .DownloadJob import DownloadJob
from .HLSParser import decode_hls_m3u8  # Add import for new HLS parser
from .Debug import logger
from .ConfigInit import VIDEO_RESOLUTIONS, VIDEO_RESOLUTIONS_DICT
from .WebRequests import WebRequests


class MovieFile:
    def __init__(self):
        self.web_requests = WebRequests()

    def download(self, curr, job_manager):
        logger.info("...")
        movie_dir = config.plugins.mediathekcockpit.movie_dir.value
        if os.path.exists(movie_dir):
            download_ok = False
            segments = []
            service_ref = getServiceReference(curr[LIST_CHANNEL])
            url, _resolution = self.getVideoUrl(curr, int(config.plugins.mediathekcockpit.movie_resolution.value))
            logger.debug("Selected video URL: %s", url)
            if url.endswith(".m3u8"):
                logger.info("Downloading HLS playlist: %s", url)
                segments = self.getPlaylistSegments(url)
                url2, ext = os.path.splitext(os.path.dirname(url))
                if ext == ".csmil":
                    ext = os.path.splitext(url2)[1]
                download_ok = segments != []
            else:
                logger.info("Downloading video URL: %s", url)
                ext = url[url.rfind("."):] if url.rfind(".") != -1 else ".mp4"
                download_ok = True
            if download_ok:
                recording_path = calcRecordingFilename(
                    curr[LIST_TIMESTAMP], curr[LIST_CHANNEL], curr[LIST_EVENT_NAME], movie_dir) + ext

                job_manager.AddJob(
                    DownloadJob(
                        url,
                        segments,
                        recording_path,
                        curr[LIST_EVENT_NAME],
                        curr[LIST_SHORT_DESCRIPTION],
                        curr[LIST_DESCRIPTION],
                        curr[LIST_TIMESTAMP],
                        service_ref,
                        curr[LIST_DURATION],
                        curr[LIST_URL_WEBSITE]
                    )
                )
                return url, recording_path
        return None, None

    def getVideoResolutions(self, curr):
        """Return list of available video resolutions."""
        resolutions = []

        for resolution_id in VIDEO_RESOLUTIONS:
            if curr[resolution_id] and curr[resolution_id].startswith("http"):
                resolutions.append(VIDEO_RESOLUTIONS_DICT[resolution_id])

        return resolutions

    def getVideoUrl(self, curr, val):
        """Get the best available video URL based on preferred resolution."""
        # Try preferred resolution first, then fall back to others
        for resolution in [val] + VIDEO_RESOLUTIONS:
            url = curr[resolution]
            if url and url.startswith("http"):
                return url, VIDEO_RESOLUTIONS_DICT[resolution]
        # Return empty values if no valid URL found
        return "", ""

    def getPlaylistSegments(self, url):
        """
        Extract segments from HLS playlists, handling various formats.
        """
        logger.debug("Processing HLS playlist: %s", url)
        try:
            # Download playlist content
            playlist_content = self.web_requests.getContent(url)

            # Get base URL for resolving relative URLs
            base_url = url.rsplit('/', 1)[0] + '/'

            # Parse playlist using HLS parser
            result = decode_hls_m3u8(playlist_content, base_url)

            # Case 1: Direct media playlist with segments
            if result['segments']:
                logger.debug("Found direct media playlist with %d segments", len(result['segments']))
                return result['segments']

            # Case 2: Master playlist with variants
            if result['variants']:
                logger.debug("Found master playlist with %d variants", len(result['variants']))
                # Select the highest bandwidth variant (last in sorted order)
                variants = sorted(result['variants'], key=lambda v: v.bandwidth)
                selected_variant = variants[-1]
                variant_url = selected_variant.url

                logger.debug("Loading variant playlist: %s", variant_url)
                variant_content = self.web_requests.getContent(variant_url)

                # Get base URL for variant playlist
                variant_base_url = variant_url.rsplit('/', 1)[0] + '/'

                # Parse variant playlist
                variant_result = decode_hls_m3u8(variant_content, variant_base_url)

                if variant_result['segments']:
                    logger.debug("Found variant media playlist with %d segments", len(variant_result['segments']))
                    return variant_result['segments']

            logger.error("No segments found in playlist: %s", url)
            return []

        except Exception as e:
            logger.error("Error processing playlist %s: %s", url, str(e))
            return []

    def checkMP4Structure(self, file_path):
        """Check if MP4 has progressive structure"""
        logger.info("Checking MP4 structure for file_path: %s", file_path)
        try:
            with open(file_path, 'rb') as f:
                # Read first 1KB to look for moov atom
                header = f.read(1024)
                if b'moov' in header[:100]:
                    logger.info("Progressive MP4 - can play during download")
                    return True
                logger.info("Standard MP4 - needs complete download for playback")
                return False
        except Exception:
            return False
