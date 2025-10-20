"""
Unified lyrics provider interface for LyricFlow.

Supports multiple providers: Musixmatch, LRCLIB, and more.
"""

from typing import Optional, Dict, Any, List, Literal
from pathlib import Path
from enum import Enum
import logging
import re

from lyricflow.core.romanizer import clean_lrc_timestamps

logger = logging.getLogger(__name__)


class LyricsProvider(str, Enum):
    """Available lyrics providers."""
    MUSIXMATCH = "musixmatch"
    LRCLIB = "lrclib"


class UnifiedLyricsFetcher:
    """
    Unified interface for fetching lyrics from multiple providers.
    
    Supports:
    - Musixmatch: Large database, synced/unsynced, translations
    - LRCLIB: Free, open-source, synced/unsynced
    
    Example:
        >>> fetcher = UnifiedLyricsFetcher(provider="lrclib")
        >>> result = fetcher.fetch("Song Title", "Artist")
        >>> if result:
        >>>     fetcher.save_lrc(result, Path("output.lrc"))
    """
    
    def __init__(
        self,
        provider: Literal["musixmatch", "lrclib"] = "lrclib",
        musixmatch_token: Optional[str] = None
    ):
        """
        Initialize unified fetcher.
        
        Args:
            provider: Which provider to use ("musixmatch" or "lrclib")
            musixmatch_token: Optional Musixmatch API token
        """
        self.provider = provider
        self._fetcher = None
        
        # Initialize the appropriate fetcher
        if provider == "musixmatch":
            try:
                from lyricflow.core.musixmatch import MusixmatchFetcher
                self._fetcher = MusixmatchFetcher(token=musixmatch_token)
                logger.info("Initialized Musixmatch provider")
            except ImportError:
                logger.error("Musixmatch provider requires 'requests' library")
                raise
        
        elif provider == "lrclib":
            try:
                from lyricflow.core.lrclib import LRCLIBFetcher
                self._fetcher = LRCLIBFetcher()
                logger.info("Initialized LRCLIB provider")
            except ImportError:
                logger.error("LRCLIB provider requires 'requests' library")
                raise
        
        else:
            raise ValueError(f"Unknown provider: {provider}. Use 'musixmatch' or 'lrclib'")
    
    def fetch(
        self,
        title: str,
        artist: Optional[str] = None,
        album: Optional[str] = None,
        duration: Optional[int] = None,
        fetch_translation: bool = False,
        fetch_romanization: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch lyrics using the configured provider.
        
        Args:
            title: Track title
            artist: Artist name
            album: Album name (optional)
            duration: Track duration in seconds (optional)
            fetch_translation: Fetch translation (Musixmatch only)
            fetch_romanization: Fetch romanization (uses LyricFlow romanizer)
        
        Returns:
            Dictionary with lyrics data or None
        """
        if self.provider == "musixmatch":
            # Musixmatch returns LyricResult objects
            result = self._fetcher.get_best_match(title, artist or "", album)
            
            if not result:
                return None
            
            # Convert to unified format
            unified_result = {
                'provider': 'musixmatch',
                'id': result.track_id,
                'title': result.title,
                'artist': result.artist,
                'album': result.album,
                'duration': result.duration,
                'synced_lyrics': result.synced_lyrics,
                'plain_lyrics': result.lyrics,
                'translation': result.translation if fetch_translation else None,
                'romanization': result.romanization if fetch_romanization else None,
                'instrumental': result.instrumental,
                'rating': result.rating,
                'has_synced': result.has_subtitles,
                'has_plain': result.has_lyrics
            }
            
            return unified_result
        
        elif self.provider == "lrclib":
            # LRCLIB returns dict directly
            result = self._fetcher.get_best_match(title, artist or "", album, duration)
            
            if not result:
                return None
            
            # Add romanization if requested
            if fetch_romanization and (result.get('synced_lyrics') or result.get('plain_lyrics')):
                try:
                    from lyricflow.core.romanizer import Romanizer
                    from lyricflow.utils.config import Config
                    config = Config.load()
                    romanizer = Romanizer(config)
                    
                    lyrics_to_romanize = result.get('synced_lyrics') or result.get('plain_lyrics')
                    result['romanization'] = romanizer.romanize(lyrics_to_romanize)
                except Exception as e:
                    logger.error(f"Romanization error: {e}")
                    result['romanization'] = None
            
            # Ensure consistent format
            unified_result = {
                'provider': 'lrclib',
                'id': result.get('id'),
                'title': result.get('title', title),
                'artist': result.get('artist', artist or ''),
                'album': result.get('album', album or ''),
                'duration': result.get('duration', duration or 0),
                'synced_lyrics': result.get('synced_lyrics'),
                'plain_lyrics': result.get('plain_lyrics'),
                'translation': None,  # LRCLIB doesn't provide translations
                'romanization': result.get('romanization'),
                'instrumental': result.get('instrumental', False),
                'rating': None,  # LRCLIB doesn't have ratings
                'has_synced': bool(result.get('synced_lyrics')),
                'has_plain': bool(result.get('plain_lyrics')),
                'source_url': result.get('source_url')
            }
            
            return unified_result
        
        return None
    
    def search(
        self,
        title: str,
        artist: Optional[str] = None,
        album: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for multiple results (returns all matches).
        
        Args:
            title: Track title
            artist: Artist name
            album: Album name (optional)
        
        Returns:
            List of results
        """
        if self.provider == "musixmatch":
            results = self._fetcher.search(title, artist, album, fetch_lyrics=True)
            
            # Convert LyricResult objects to dicts
            unified_results = []
            for result in results:
                unified_results.append({
                    'provider': 'musixmatch',
                    'id': result.track_id,
                    'title': result.title,
                    'artist': result.artist,
                    'album': result.album,
                    'duration': result.duration,
                    'has_synced': result.has_subtitles,
                    'has_plain': result.has_lyrics,
                    'instrumental': result.instrumental,
                    'rating': result.rating
                })
            
            return unified_results
        
        elif self.provider == "lrclib":
            # LRCLIB search API
            results = self._fetcher.api.search(title, artist)
            
            # Already in dict format, just add provider
            for result in results:
                result['provider'] = 'lrclib'
            
            return results
        
        return []
    
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
            # Clean lyrics: remove spaces inside and after timestamps
            # Convert "[ 00 : 12 . 34 ] text" to "[00:12.34]text"
            cleaned_lyrics = clean_lrc_timestamps(lyrics)
            
            # Add metadata header
            lrc_content = f"[ti:{result['title']}]\n"
            lrc_content += f"[ar:{result['artist']}]\n"
            
            if result.get('album'):
                lrc_content += f"[al:{result['album']}]\n"
            
            if result.get('duration'):
                duration = int(result['duration'])  # Ensure it's an integer
                minutes = duration // 60
                seconds = duration % 60
                lrc_content += f"[length:{minutes:02d}:{seconds:02d}]\n"
            
            # Add provider info as comment
            lrc_content += f"[by:LyricFlow - {result.get('provider', 'unknown')}]\n"
            lrc_content += "\n"
            lrc_content += cleaned_lyrics
            
            output_path.write_text(lrc_content, encoding='utf-8')
            logger.info(f"Saved lyrics to {output_path}")
            
            # Save romanization if available
            if result.get('romanization'):
                romaji_path = output_path.with_stem(output_path.stem + "_romaji")
                
                # Clean romanization: remove spaces inside and after timestamps
                cleaned_romanization = clean_lrc_timestamps(result['romanization'])
                
                romaji_content = f"[ti:{result['title']}]\n"
                romaji_content += f"[ar:{result['artist']}]\n"
                romaji_content += f"[by:LyricFlow - Romanized]\n\n"
                romaji_content += cleaned_romanization
                romaji_path.write_text(romaji_content, encoding='utf-8')
                logger.info(f"Saved romanization to {romaji_path}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error saving LRC: {e}")
            return False
    
    @property
    def provider_name(self) -> str:
        """Get human-readable provider name."""
        names = {
            "musixmatch": "Musixmatch",
            "lrclib": "LRCLIB"
        }
        return names.get(self.provider, self.provider)
    
    @property
    def supports_translation(self) -> bool:
        """Check if provider supports translations."""
        return self.provider == "musixmatch"
    
    @property
    def is_free(self) -> bool:
        """Check if provider is free to use."""
        return self.provider == "lrclib"


def create_fetcher(
    provider: Optional[str] = None,
    prefer_free: bool = True
) -> UnifiedLyricsFetcher:
    """
    Factory function to create a lyrics fetcher.
    
    Args:
        provider: Specific provider to use ("musixmatch" or "lrclib")
        prefer_free: If True and provider is None, use free provider (LRCLIB)
    
    Returns:
        Configured UnifiedLyricsFetcher
    
    Example:
        >>> # Use free provider
        >>> fetcher = create_fetcher()
        
        >>> # Use specific provider
        >>> fetcher = create_fetcher(provider="musixmatch")
    """
    if provider:
        return UnifiedLyricsFetcher(provider=provider)
    
    # Default to free provider
    if prefer_free:
        return UnifiedLyricsFetcher(provider="lrclib")
    else:
        return UnifiedLyricsFetcher(provider="musixmatch")
