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


import re
from collections import namedtuple
import urlparse

# Define data structures using namedtuple for Python 2.7 compatibility
HLSSegment = namedtuple('HLSSegment', [
    'url', 'duration', 'sequence', 'discontinuity', 'byterange', 'key'
])

HLSVariant = namedtuple('HLSVariant', [
    'url', 'bandwidth', 'resolution', 'codecs', 'frame_rate'
])

# Helper functions to create objects with default values


def create_hls_segment(url, duration, sequence, discontinuity=False, byterange=None, key=None):
    """Create HLSSegment with default values"""
    return HLSSegment(url, duration, sequence, discontinuity, byterange, key)


def create_hls_variant(url, bandwidth, resolution=None, codecs=None, frame_rate=None):
    """Create HLSVariant with default values"""
    return HLSVariant(url, bandwidth, resolution, codecs, frame_rate)


class HLSParser(object):
    """Parser for HLS M3U8 files that extracts all variants and segments"""

    def __init__(self, base_url=""):
        self.base_url = base_url

    def parse_m3u8(self, content):
        """
        Parse M3U8 content and return variants and segments

        Args:
            content: Raw M3U8 file content

        Returns:
            Dictionary with 'variants' and 'segments' keys
        """
        lines = [line.strip() for line in content.splitlines() if line.strip()]

        if not lines or not lines[0].startswith('#EXTM3U'):
            raise ValueError("Invalid M3U8 file format")

        # Check if this is a master playlist or media playlist
        is_master = any(line.startswith('#EXT-X-STREAM-INF') for line in lines)

        if is_master:
            variants = self._parse_master_playlist(lines)
            return {'variants': variants, 'segments': []}
        segments = self._parse_media_playlist(lines)
        return {'variants': [], 'segments': segments}

    def _parse_master_playlist(self, lines):
        """Parse master playlist and extract variant streams"""
        variants = []
        i = 0

        while i < len(lines):
            line = lines[i]

            if line.startswith('#EXT-X-STREAM-INF'):
                # Parse stream info attributes
                attrs = self._parse_attributes(line)

                # Get the URL from next line
                i += 1
                if i < len(lines) and not lines[i].startswith('#'):
                    url = self._resolve_url(lines[i])

                    # Convert bandwidth to int, default to 0 if not present
                    bandwidth = int(attrs.get('BANDWIDTH', 0))

                    # Get frame rate as float if present
                    frame_rate = None
                    if 'FRAME-RATE' in attrs:
                        try:
                            frame_rate = float(attrs['FRAME-RATE'])
                        except (ValueError, TypeError):
                            frame_rate = None

                    # Remove quotes from codecs if present
                    codecs = attrs.get('CODECS', '').strip('"')

                    variant = create_hls_variant(
                        url=url,
                        bandwidth=bandwidth,
                        resolution=attrs.get('RESOLUTION'),
                        codecs=codecs if codecs else None,
                        frame_rate=frame_rate
                    )
                    variants.append(variant)

            i += 1

        return variants

    def _parse_media_playlist(self, lines):
        """Parse media playlist and extract segments"""
        segments = []
        sequence = 0
        current_key = None
        i = 0

        while i < len(lines):
            line = lines[i]

            if line.startswith('#EXT-X-MEDIA-SEQUENCE'):
                sequence = int(line.split(':')[1])

            elif line.startswith('#EXT-X-KEY'):
                current_key = self._parse_attributes(line)

            elif line.startswith('#EXTINF'):
                # Parse segment duration
                duration_match = re.search(r':([\d.]+)', line)
                duration = float(duration_match.group(
                    1)) if duration_match else 0.0

                # Get segment URL from next line
                i += 1
                if i < len(lines) and not lines[i].startswith('#'):
                    url = self._resolve_url(lines[i])

                    # Copy current_key dictionary if it exists
                    key_copy = None
                    if current_key:
                        key_copy = dict(current_key)

                    segment = create_hls_segment(
                        url=url,
                        duration=duration,
                        sequence=sequence,
                        discontinuity=False,
                        byterange=None,
                        key=key_copy
                    )
                    segments.append(segment)
                    sequence += 1

            elif line.startswith('#EXT-X-BYTERANGE'):
                # Handle byte range for last segment
                if segments:
                    # Replace the last segment with updated byterange
                    last_segment = segments[-1]
                    updated_segment = create_hls_segment(
                        url=last_segment.url,
                        duration=last_segment.duration,
                        sequence=last_segment.sequence,
                        discontinuity=last_segment.discontinuity,
                        byterange=line.split(':')[1],
                        key=last_segment.key
                    )
                    segments[-1] = updated_segment

            elif line.startswith('#EXT-X-DISCONTINUITY'):
                # Mark next segment as discontinuity
                # We'll handle this when we encounter the next EXTINF
                pass

            i += 1

        return segments

    def _parse_attributes(self, line):
        """Parse attribute string from M3U8 line"""
        attrs = {}
        if ':' not in line:
            return attrs

        attr_part = line.split(':', 1)[1]

        # Regular expression to match key=value pairs
        pattern = r'([A-Z-]+)=([^,]*(?:"[^"]*"[^,]*)*)'
        matches = re.findall(pattern, attr_part)

        for key, value in matches:
            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            attrs[key] = value

        return attrs

    def _resolve_url(self, url):
        """Resolve relative URLs against base URL"""
        if url.startswith(('http://', 'https://')):
            return url

        if self.base_url:
            return urlparse.urljoin(self.base_url, url)

        return url


def decode_hls_m3u8(m3u8_content, base_url=""):
    """
    Decode HLS M3U8 file and return all variants and segments

    Args:
        m3u8_content: Raw M3U8 file content as string
        base_url: Base URL for resolving relative URLs

    Returns:
        Dictionary containing:
        - 'variants': List of HLSVariant objects (for master playlists)
        - 'segments': List of HLSSegment objects (for media playlists)

    Example:
        with open('playlist.m3u8', 'r') as f:
            content = f.read()

        result = decode_hls_m3u8(content, 'https://example.com/hls/')

        # Access variants
        for variant in result['variants']:
            print("Bandwidth: {}, URL: {}".format(variant.bandwidth, variant.url))

        # Access segments
        for segment in result['segments']:
            print("Duration: {}s, URL: {}".format(segment.duration, segment.url))
    """
    parser = HLSParser(base_url)
    return parser.parse_m3u8(m3u8_content)

# Example usage and test function


def example_usage():
    """Example of how to use the HLS decoder"""

    # Example master playlist
    master_playlist = """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=1280000,RESOLUTION=720x480,CODECS="avc1.42e01e,mp4a.40.2"
low/playlist.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=2560000,RESOLUTION=1280x720,CODECS="avc1.42e01e,mp4a.40.2"
high/playlist.m3u8
"""

    # Example media playlist
    media_playlist = """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:9.009,
segment0.ts
#EXTINF:9.009,
segment1.ts
#EXTINF:3.003,
segment2.ts
#EXT-X-ENDLIST
"""

    # Parse master playlist
    print("Master playlist variants:")
    result = decode_hls_m3u8(master_playlist, "https://example.com/hls/")
    for variant in result['variants']:
        print("  Bandwidth: {}, Resolution: {}".format(
            variant.bandwidth, variant.resolution))

    # Parse media playlist
    print("\nMedia playlist segments:")
    result = decode_hls_m3u8(media_playlist, "https://example.com/hls/")
    for segment in result['segments']:
        print("  Duration: {}s, Sequence: {}".format(
            segment.duration, segment.sequence))


if __name__ == "__main__":
    example_usage()
