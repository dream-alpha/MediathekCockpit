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
import random
import requests
from .Debug import logger


class Content():
    def __init__(self):
        self.text = ""
        self.status_code = "999"


class WebRequests():

    def __init__(self):
        return

    def getUserAgent(self):
        user_agents = [
            'Mozilla/5.0 (compatible; Konqueror/4.5; FreeBSD) KHTML/4.5.4 (like Gecko)',
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 7.1; Trident/5.0)',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20120101 Firefox/29.0',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20120101 Firefox/35.0',
            'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
            'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; de) Presto/2.9.168 Version/11.52',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
        ]
        user_agent = random.choice(user_agents)
        return user_agent

    def getSession(self):
        session = requests.Session()
        session.headers.update({"user-agent": self.getUserAgent()})
        return session

    def postContent(self, url, data=None):
        logger.info("url: %s", url)
        headers = {"user-agent": self.getUserAgent(), "Content-Type": "text/plain"}
        if data is None:
            data = {}
        try:
            content = requests.post(url, headers=headers, data=json.dumps(data), allow_redirects=True, verify=False)
            logger.debug("content.url: %s", content.url)
            logger.debug("content.status_code: %s", content.status_code)
            content.raise_for_status()
        except Exception:
            # logger.error("exception: %s", e)
            content = Content()
        logger.debug("content.text: %s", content.text)
        return content

    def getContent(self, url, params=None):
        logger.info("url: %s", url)
        headers = {"user-agent": self.getUserAgent()}
        if params is None:
            params = {}
        try:
            response = requests.get(url, headers=headers, params=params, allow_redirects=True, verify=False)
            logger.debug("response.url: %s", response.url)
            logger.debug("response.status_code: %s", response.status_code)
            content = response.content
            response.raise_for_status()
        except Exception as e:
            logger.error("exception: %s", e)
            content = ""
        return content

    def downloadFile(self, url, path):
        """Stream download large files to avoid memory issues"""
        logger.info("url: %s, path: %s", url, path)
        headers = {"user-agent": self.getUserAgent()}
        response = requests.get(url, headers=headers, stream=True, allow_redirects=True, verify=False)
        logger.debug("response.url: %s", response.url)
        logger.debug("response.status_code: %s", response.status_code)
        response.raise_for_status()

        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if hasattr(self, '_cancelled') and self._cancelled:
                    logger.debug("Download cancelled during chunk processing")
                    f.close()
                    response.close()
                    return False
                if chunk:  # filter out keep-alive chunks
                    f.write(chunk)

        response.close()
        return True
