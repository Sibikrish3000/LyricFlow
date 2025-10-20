"""
LRCLIB lyrics fetcher implementation.

LRCLIB is a free, open-source lyrics database that provides synced and unsynced lyrics.
API documentation: https://lrclib.net/docs
"""

import re
import json
import html
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class LRCLIBApi:
    """LRCLIB API client for fetching lyrics."""
    
    BASE_URL = "https://lrclib.net/api"
    
    def __init__(self):
        """Initialize LRCLIB API client."""
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library is required for LRCLIB API")
    
    @staticmethod
    def clean_meta_text(text: str) -> str:
        """
        Clean metadata text for use in the API URL.
        
        Args:
            text: Raw metadata text
        
        Returns:
            Cleaned text suitable for API queries
        """
        if not isinstance(text, str):
            return ''
        
        # Remove content in brackets (), {}, [], 【】
        text = re.sub(r'\(.*?\)|{.*?}|\[.*?\]|【.*?】', '', text)
        
        # Normalize and trim (but don't lowercase or remove unicode)
        text = text.strip()
        
        # Replace special characters but keep unicode (Japanese, Korean, etc.)
        text = text.replace('@', 'at')
        text = text.replace('&', 'and')
        
        return text.strip()
    
    @staticmethod
    def parse_lyrics(lyric_text: str) -> str:
        """
        Decode HTML entities and clean up special characters in lyrics.
        
        Args:
            lyric_text: Raw lyric text with potential HTML entities
        
        Returns:
            Cleaned lyric text
        """
        if not isinstance(lyric_text, str):
            return ''
        
        # Use Python's standard library to decode HTML entities
        cleaned_text = html.unescape(lyric_text)
        
        # Specific character replacements
        replacements = {
            '<br>': '',
            '\uFF1A': ':',   # Full-width colon
            '\uFF08': '(',   # Full-width parenthesis
            '\uFF09': ')',   # Full-width parenthesis
        }
        
        for old, new in replacements.items():
            cleaned_text = cleaned_text.replace(old, new)
        
        # Normalize various apostrophe and quote characters to standard single quote
        cleaned_text = re.sub(r"[\u2018\u2019\uFF07`´]", "'", cleaned_text)
        
        # Normalize various whitespace characters to standard space
        cleaned_text = re.sub(r'[\u2000-\u200F\u2028-\u202F\u205F-\u206F\u3000\uFEFF]+', ' ', cleaned_text)
        
        return cleaned_text.strip()
    
    def get_lyrics(
        self,
        title: str,
        artist: str,
        album: Optional[str] = None,
        duration: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get lyrics from LRCLIB.
        
        Args:
            title: Track title
            artist: Artist name
            album: Album name (optional)
            duration: Track duration in seconds (optional, improves accuracy)
        
        Returns:
            Dictionary with lyrics data or None if not found
        """
        # Clean metadata
        clean_artist = self.clean_meta_text(artist)
        clean_title = self.clean_meta_text(title)
        clean_album = self.clean_meta_text(album) if album else ''
        
        if not clean_artist or not clean_title:
            logger.error("Artist or title metadata is missing")
            return None
        
        # Construct API URL
        url = f"{self.BASE_URL}/get"
        params = {
            'artist_name': clean_artist,
            'track_name': clean_title,
        }
        
        if clean_album:
            params['album_name'] = clean_album
        
        if duration:
            params['duration'] = int(duration)
        
        logger.info(f"Requesting LRCLIB: {clean_title} by {clean_artist}")
        
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract lyrics (prefer synced over plain)
            synced_lyrics = data.get('syncedLyrics')
            plain_lyrics = data.get('plainLyrics')
            
            # Use synced if available and not empty
            if synced_lyrics and isinstance(synced_lyrics, str) and synced_lyrics.strip():
                lyrics = synced_lyrics
                is_synced = True
            elif plain_lyrics:
                lyrics = plain_lyrics
                is_synced = False
            else:
                logger.warning("No lyrics found in LRCLIB response")
                return None
            
            # Parse and clean lyrics
            parsed_lyrics = self.parse_lyrics(lyrics)
            
            return {
                'id': data.get('id'),
                'title': data.get('trackName', title),
                'artist': data.get('artistName', artist),
                'album': data.get('albumName', album or ''),
                'duration': data.get('duration', duration or 0),
                'synced_lyrics': parsed_lyrics if is_synced else None,
                'plain_lyrics': parsed_lyrics if not is_synced else None,
                'instrumental': data.get('instrumental', False),
                'source_url': response.url
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch from LRCLIB: {e}")
            return None
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse LRCLIB response: {e}")
            return None
    
    def search(
        self,
        query: str,
        artist: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for tracks on LRCLIB.
        
        Args:
            query: Search query (track name)
            artist: Artist name filter (optional)
        
        Returns:
            List of search results
        """
        url = f"{self.BASE_URL}/search"
        params = {'q': query}
        
        if artist:
            params['artist_name'] = artist
        
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            results = response.json()
            
            # Transform to our format
            formatted_results = []
            for item in results:
                formatted_results.append({
                    'id': item.get('id'),
                    'title': item.get('trackName', ''),
                    'artist': item.get('artistName', ''),
                    'album': item.get('albumName', ''),
                    'duration': item.get('duration', 0),
                    'has_synced': bool(item.get('syncedLyrics')),
                    'has_plain': bool(item.get('plainLyrics')),
                    'instrumental': item.get('instrumental', False)
                })
            
            logger.info(f"Found {len(formatted_results)} results from LRCLIB")
            return formatted_results
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Search failed: {e}")
            return []


class LRCLIBFetcher:
    """High-level LRCLIB lyrics fetcher compatible with Musixmatch fetcher."""
    
    def __init__(self):
        """Initialize LRCLIB fetcher."""
        self.api = LRCLIBApi()
    
    def search(
        self,
        title: str,
        artist: Optional[str] = None,
        album: Optional[str] = None,
        duration: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Search for lyrics (simplified interface).
        
        Args:
            title: Track title
            artist: Artist name
            album: Album name (optional)
            duration: Track duration in seconds (optional)
        
        Returns:
            Lyrics data or None
        """
        return self.api.get_lyrics(title, artist or "", album, duration)
    
    def get_best_match(
        self,
        title: str,
        artist: str,
        album: Optional[str] = None,
        duration: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get the best matching lyric result automatically.
        
        Args:
            title: Track title
            artist: Artist name
            album: Album name (optional)
            duration: Track duration in seconds (optional)
        
        Returns:
            Best matching result or None
        """
        result = self.search(title, artist, album, duration)
        
        if result:
            logger.info(f"Found match: {result['title']} by {result['artist']}")
        
        return result
    
    def save_lrc(self, result: Dict[str, Any], output_path: Path) -> bool:
        """
        Save lyrics to LRC file.
        
        Args:
            result: Lyrics data dictionary
            output_path: Output file path
        
        Returns:
            True if successful
        """
        lyrics = result.get('synced_lyrics') or result.get('plain_lyrics')
        
        if not lyrics:
            logger.error("No lyrics to save")
            return False
        
        try:
            # Add metadata if we have synced lyrics
            if result.get('synced_lyrics'):
                lrc_content = f"[ti:{result['title']}]\n"
                lrc_content += f"[ar:{result['artist']}]\n"
                if result.get('album'):
                    lrc_content += f"[al:{result['album']}]\n"
                if result.get('duration'):
                    minutes = result['duration'] // 60
                    seconds = result['duration'] % 60
                    lrc_content += f"[length:{minutes:02d}:{seconds:02d}]\n"
                lrc_content += "\n"
                lrc_content += lyrics
            else:
                lrc_content = lyrics
            
            output_path.write_text(lrc_content, encoding='utf-8')
            logger.info(f"Saved lyrics to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving LRC: {e}")
            return False
