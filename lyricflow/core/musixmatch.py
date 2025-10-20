"""
Musixmatch lyrics fetcher implementation.

This module provides functionality to search and fetch lyrics from Musixmatch,
including synced lyrics (LRC format), translations, and romanization.
"""

import time
import logging
from typing import Dict, Any, List, Optional, Literal
from pathlib import Path

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class MusixmatchAPI:
    """Musixmatch API client for fetching lyrics."""
    
    BASE_URL = "https://apic-desktop.musixmatch.com/ws/1.1"
    APP_ID = "web-desktop-app-v1.0"
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize Musixmatch API client.
        
        Args:
            token: Optional user token. If not provided, will be fetched automatically.
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library is required for Musixmatch API")
        
        self.token = token
        self.headers = {
            'authority': 'apic-desktop.musixmatch.com',
            'cookie': 'x-mxm-token-guid=',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Musixmatch/4.10.55 Chrome/120.0.6099.291 Electron/28.2.3 Safari/537.36'
        }
        self._last_request_time = 0
        self._min_request_interval = 0.5  # Minimum 500ms between requests
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make a request to the Musixmatch API."""
        # Rate limiting
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Add common parameters
        params.update({
            'user_language': 'en',
            'app_id': self.APP_ID,
        })
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            self._last_request_time = time.time()
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {endpoint}: {e}")
            return None
        except ValueError as e:
            logger.error(f"JSON parsing error: {e}")
            return None
    
    def get_token(self) -> Optional[str]:
        """Get or refresh user token."""
        if self.token:
            return self.token
        
        logger.info("Fetching new Musixmatch token...")
        
        params = {'t': int(time.time() * 1000)}
        data = self._make_request('token.get', params)
        
        if data:
            logger.debug(f"Token response: {data}")
            message = data.get('message', {})
            body = message.get('body', {})
            
            # Handle list/dict body like in get_lyrics
            if isinstance(body, list):
                if not body:
                    logger.error("Token response body is empty list")
                    return None
                body = body[0] if len(body) > 0 else {}
            
            if not isinstance(body, dict):
                logger.error(f"Unexpected token body type: {type(body)}")
                return None
            
            token = body.get('user_token', '')
            if token and token != 'UpgradeOnlyUpgradeOnlyUpgradeOnlyUpgradeOnly':
                self.token = token
                logger.info("Successfully acquired token")
                return token
            else:
                logger.error(f"Invalid token received: {token[:50] if token else 'empty'}")
        else:
            logger.error("No data received from token.get endpoint")
        
        logger.error("Failed to get valid token")
        return None
    
    def search_tracks(
        self,
        title: str,
        artist: Optional[str] = None,
        album: Optional[str] = None,
        has_lyrics: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for tracks on Musixmatch.
        
        Args:
            title: Track title
            artist: Artist name (optional)
            album: Album name (optional)
            has_lyrics: Only return tracks with lyrics
        
        Returns:
            List of track dictionaries with metadata
        """
        if not self.get_token():
            return []
        
        logger.info(f"Searching for: {title} by {artist or 'Unknown'}")
        
        params = {
            'format': 'json',
            'subtitle_format': 'lrc',
            'q_track': title,
            'f_has_lyrics': 1 if has_lyrics else 0,
            'usertoken': self.token,
            't': int(time.time() * 1000)
        }
        
        if artist:
            params['q_artist'] = artist
        if album:
            params['q_album'] = album
        
        data = self._make_request('track.search', params)
        
        if not data:
            return []
        
        track_list = data.get('message', {}).get('body', {}).get('track_list', [])
        results = []
        
        for track_obj in track_list:
            track = track_obj.get('track', {})
            if not track:
                continue
            
            track_id = track.get('commontrack_id')
            has_lyrics_flag = track.get('has_lyrics')
            has_subtitles = track.get('has_subtitles')
            
            if not track_id or (not has_lyrics_flag and not has_subtitles):
                continue
            
            results.append({
                'id': track_id,
                'track_id': track.get('track_id'),
                'title': track.get('track_name', ''),
                'artist': track.get('artist_name', ''),
                'album': track.get('album_name', ''),
                'duration': track.get('track_length', 0),
                'has_lyrics': bool(has_lyrics_flag),
                'has_subtitles': bool(has_subtitles),
                'instrumental': track.get('instrumental', 0) == 1,
                'rating': track.get('track_rating', 0),
            })
        
        logger.info(f"Found {len(results)} tracks")
        return results
    
    def get_lyrics(
        self,
        track_id: int,
        synced: bool = False
    ) -> Optional[str]:
        """
        Get lyrics for a specific track.
        
        Args:
            track_id: Musixmatch common track ID
            synced: If True, get synced lyrics (LRC format)
        
        Returns:
            Lyrics text or None if not found
        """
        if not self.get_token():
            return None
        
        endpoint = 'track.subtitle.get' if synced else 'track.lyrics.get'
        params = {
            'commontrack_id': track_id,
            'usertoken': self.token
        }
        
        data = self._make_request(endpoint, params)
        
        if not data:
            return None
        
        body_key = 'subtitle' if synced else 'lyrics'
        lyric_key = 'subtitle_body' if synced else 'lyrics_body'
        
        # Handle both dict and list responses from API
        message = data.get('message', {})
        body = message.get('body', {})
        
        # Sometimes the body is a list instead of dict
        if isinstance(body, list):
            if not body:
                return None
            body = body[0] if len(body) > 0 else {}
        
        if not isinstance(body, dict):
            logger.warning(f"Unexpected body type: {type(body)}")
            return None
        
        lyrics_data = body.get(body_key, {})
        if not isinstance(lyrics_data, dict):
            logger.warning(f"Unexpected {body_key} type: {type(lyrics_data)}")
            return None
        
        lyrics = lyrics_data.get(lyric_key)
        return lyrics
    
    def get_translation(
        self,
        track_id: int,
        target_language: str = 'en'
    ) -> Optional[str]:
        """
        Get translated lyrics for a track.
        
        Args:
            track_id: Musixmatch track ID (not commontrack_id)
            target_language: Target language code (e.g., 'en', 'ja')
        
        Returns:
            Translated lyrics or None
        """
        if not self.get_token():
            return None
        
        params = {
            'track_id': track_id,
            'selected_language': target_language,
            'usertoken': self.token
        }
        
        data = self._make_request('crowd.track.translations.get', params)
        
        if not data:
            return None
        
        translations = data.get('message', {}).get('body', {}).get('translations_list', [])
        if translations:
            return translations[0].get('translation', {}).get('description')
        
        return None


class LyricResult:
    """Container for a single lyric search result."""
    
    def __init__(
        self,
        track_id: int,
        title: str,
        artist: str,
        album: str = "",
        duration: int = 0,
        has_lyrics: bool = False,
        has_subtitles: bool = False,
        instrumental: bool = False,
        rating: int = 0
    ):
        self.track_id = track_id
        self.title = title
        self.artist = artist
        self.album = album
        self.duration = duration
        self.has_lyrics = has_lyrics
        self.has_subtitles = has_subtitles
        self.instrumental = instrumental
        self.rating = rating
        
        self.lyrics: Optional[str] = None
        self.synced_lyrics: Optional[str] = None
        self.translation: Optional[str] = None
        self.romanization: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation."""
        duration_str = f"{self.duration // 60}:{self.duration % 60:02d}" if self.duration else "Unknown"
        flags = []
        if self.has_subtitles:
            flags.append("Synced")
        if self.has_lyrics:
            flags.append("Unsynced")
        if self.instrumental:
            flags.append("Instrumental")
        
        flags_str = ", ".join(flags) if flags else "No lyrics"
        
        return f"{self.title} - {self.artist} [{duration_str}] ({flags_str}) Rating: {self.rating}"
    
    def match_score(self, title: str, artist: str) -> float:
        """
        Calculate match score for this result.
        
        Args:
            title: Search title
            artist: Search artist
        
        Returns:
            Match score (0.0 to 1.0)
        """
        score = 0.0
        
        # Title match (50% weight)
        title_lower = title.lower()
        result_title_lower = self.title.lower()
        if title_lower == result_title_lower:
            score += 0.5
        elif title_lower in result_title_lower or result_title_lower in title_lower:
            score += 0.3
        
        # Artist match (30% weight)
        artist_lower = artist.lower()
        result_artist_lower = self.artist.lower()
        if artist_lower == result_artist_lower:
            score += 0.3
        elif artist_lower in result_artist_lower or result_artist_lower in artist_lower:
            score += 0.15
        
        # Bonus for synced lyrics (10% weight)
        if self.has_subtitles:
            score += 0.1
        
        # Rating bonus (10% weight)
        score += (self.rating / 100) * 0.1
        
        return min(score, 1.0)


class MusixmatchFetcher:
    """High-level Musixmatch lyrics fetcher."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize fetcher with optional token."""
        self.api = MusixmatchAPI(token)
    
    def search(
        self,
        title: str,
        artist: Optional[str] = None,
        album: Optional[str] = None,
        fetch_lyrics: bool = True,
        fetch_translation: bool = False,
        fetch_romanization: bool = False
    ) -> List[LyricResult]:
        """
        Search for lyrics and optionally fetch them.
        
        Args:
            title: Track title
            artist: Artist name
            album: Album name
            fetch_lyrics: Automatically fetch lyrics for results
            fetch_translation: Fetch translations
            fetch_romanization: Fetch romanization (will use local romanizer)
        
        Returns:
            List of LyricResult objects
        """
        tracks = self.api.search_tracks(title, artist, album)
        results = []
        
        for track in tracks:
            result = LyricResult(
                track_id=track['id'],
                title=track['title'],
                artist=track['artist'],
                album=track['album'],
                duration=track['duration'],
                has_lyrics=track['has_lyrics'],
                has_subtitles=track['has_subtitles'],
                instrumental=track['instrumental'],
                rating=track['rating']
            )
            
            if fetch_lyrics:
                # Prefer synced lyrics
                if result.has_subtitles:
                    result.synced_lyrics = self.api.get_lyrics(result.track_id, synced=True)
                if result.has_lyrics:
                    result.lyrics = self.api.get_lyrics(result.track_id, synced=False)
                
                # Fetch translation if requested
                if fetch_translation and track.get('track_id'):
                    result.translation = self.api.get_translation(track['track_id'])
                
                # Romanization would be done locally using our romanizer
                if fetch_romanization and result.synced_lyrics:
                    try:
                        from lyricflow.core.romanizer import Romanizer
                        from lyricflow.utils.config import Config
                        config = Config.load()
                        romanizer = Romanizer(config)
                        result.romanization = romanizer.romanize(result.synced_lyrics)
                    except Exception as e:
                        logger.error(f"Romanization error: {e}")
            
            results.append(result)
        
        return results
    
    def get_best_match(
        self,
        title: str,
        artist: str,
        album: Optional[str] = None
    ) -> Optional[LyricResult]:
        """
        Get the best matching lyric result automatically.
        
        Args:
            title: Track title
            artist: Artist name
            album: Album name (optional)
        
        Returns:
            Best matching LyricResult or None
        """
        results = self.search(title, artist, album, fetch_lyrics=True)
        
        if not results:
            return None
        
        # Sort by match score
        results.sort(key=lambda r: r.match_score(title, artist), reverse=True)
        
        # Return best match
        best = results[0]
        logger.info(f"Best match: {best} (score: {best.match_score(title, artist):.2f})")
        return best
    
    def save_lrc(self, result: LyricResult, output_path: Path) -> bool:
        """
        Save lyrics to LRC file.
        
        Args:
            result: LyricResult with lyrics
            output_path: Output file path
        
        Returns:
            True if successful
        """
        lyrics = result.synced_lyrics or result.lyrics
        
        if not lyrics:
            logger.error("No lyrics to save")
            return False
        
        try:
            # Add metadata if we have synced lyrics
            if result.synced_lyrics:
                lrc_content = f"[ti:{result.title}]\n"
                lrc_content += f"[ar:{result.artist}]\n"
                if result.album:
                    lrc_content += f"[al:{result.album}]\n"
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
