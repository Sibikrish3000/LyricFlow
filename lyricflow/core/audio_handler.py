"""Audio file handler for reading and embedding lyrics metadata."""

import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum

try:
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3, USLT, SYLT, Encoding, TXXX
    from mutagen.mp4 import MP4
    from mutagen.flac import FLAC
    from mutagen.oggvorbis import OggVorbis
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

from lyricflow.utils.logging import get_logger

logger = get_logger(__name__)


class LyricType(Enum):
    """Types of lyrics that can be embedded."""
    SYNCED = "synced"  # Time-synced lyrics (SYLT, LRC)
    UNSYNCED = "unsynced"  # Plain text lyrics (USLT, Lyrics tag)
    ROMANIZED = "romanized"  # Romanized lyrics


class AudioHandler:
    """Handler for audio file metadata and lyric embedding."""
    
    def __init__(self, file_path: Path):
        """
        Initialize audio handler.
        
        Args:
            file_path: Path to audio file
        """
        if not MUTAGEN_AVAILABLE:
            raise ImportError(
                "Audio handling requires mutagen. Install with: pip install mutagen"
            )
        
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        self.audio = MutagenFile(self.file_path)
        if self.audio is None:
            raise ValueError(f"Unsupported audio format: {file_path}")
        
        logger.debug(f"Loaded audio file: {file_path}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Extract metadata from audio file.
        
        Returns:
            Dictionary with title, artist, album, and other metadata
        """
        metadata = {}
        
        try:
            if hasattr(self.audio, 'tags') and self.audio.tags:
                # ID3 tags (MP3)
                if isinstance(self.audio, (type(None),)) or 'TIT2' in str(type(self.audio)):
                    metadata['title'] = str(self.audio.tags.get('TIT2', ''))
                    metadata['artist'] = str(self.audio.tags.get('TPE1', ''))
                    metadata['album'] = str(self.audio.tags.get('TALB', ''))
                
                # MP4 tags
                elif isinstance(self.audio, MP4):
                    metadata['title'] = self.audio.tags.get('©nam', [''])[0]
                    metadata['artist'] = self.audio.tags.get('©ART', [''])[0]
                    metadata['album'] = self.audio.tags.get('©alb', [''])[0]
                
                # FLAC/OGG Vorbis comments
                elif isinstance(self.audio, (FLAC, OggVorbis)):
                    metadata['title'] = self.audio.tags.get('title', [''])[0]
                    metadata['artist'] = self.audio.tags.get('artist', [''])[0]
                    metadata['album'] = self.audio.tags.get('album', [''])[0]
        
        except Exception as e:
            logger.warning(f"Error extracting metadata: {e}")
        
        return metadata
    
    def has_synced_lyrics(self) -> bool:
        """Check if audio file has synced lyrics."""
        try:
            if hasattr(self.audio, 'tags') and self.audio.tags:
                # Check for SYLT tag (ID3)
                if 'SYLT' in self.audio.tags or 'SYLT:' in str(self.audio.tags):
                    return True
                
                # Check for custom synced lyrics tag
                if isinstance(self.audio, MP4):
                    return '----:com.apple.iTunes:Lyrics' in self.audio.tags
        
        except Exception as e:
            logger.warning(f"Error checking synced lyrics: {e}")
        
        return False
    
    def has_romanized_lyrics(self) -> bool:
        """Check if audio file has romanized lyrics tag."""
        try:
            if hasattr(self.audio, 'tags') and self.audio.tags:
                # Check for TXXX:Romanized_Lyrics tag (ID3)
                for key in self.audio.tags.keys():
                    if 'Romanized_Lyrics' in str(key):
                        return True
                
                # Check for MP4 custom tag
                if isinstance(self.audio, MP4):
                    return '----:com.apple.iTunes:Romanized_Lyrics' in self.audio.tags
        
        except Exception as e:
            logger.warning(f"Error checking romanized lyrics: {e}")
        
        return False
    
    def get_lyrics(self, lyric_type: LyricType = LyricType.UNSYNCED) -> Optional[str]:
        """
        Get lyrics from audio file.
        
        Args:
            lyric_type: Type of lyrics to retrieve
            
        Returns:
            Lyrics text or None if not found
        """
        try:
            if not hasattr(self.audio, 'tags') or not self.audio.tags:
                return None
            
            if lyric_type == LyricType.UNSYNCED:
                # Try USLT tag (ID3)
                if 'USLT' in self.audio.tags or 'USLT::' in str(self.audio.tags):
                    uslt_tags = [tag for tag in self.audio.tags.values() if isinstance(tag, USLT)]
                    if uslt_tags:
                        return str(uslt_tags[0].text)
                
                # Try Lyrics tag (MP4)
                if isinstance(self.audio, MP4) and '©lyr' in self.audio.tags:
                    return self.audio.tags['©lyr'][0]
            
            elif lyric_type == LyricType.ROMANIZED:
                # Check for custom romanized lyrics tag
                for key, value in self.audio.tags.items():
                    if 'Romanized_Lyrics' in str(key):
                        return str(value)
        
        except Exception as e:
            logger.warning(f"Error getting lyrics: {e}")
        
        return None
    
    def embed_lyrics(
        self,
        lyrics: str,
        lyric_type: LyricType = LyricType.UNSYNCED,
        language: str = "eng"
    ) -> bool:
        """
        Embed lyrics into audio file.
        
        Args:
            lyrics: Lyrics text to embed
            lyric_type: Type of lyrics
            language: Language code (e.g., 'eng', 'jpn')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not hasattr(self.audio, 'tags'):
                logger.error("Audio format does not support tags")
                return False
            
            if self.audio.tags is None:
                # Initialize tags if not present
                if isinstance(self.audio, MP4):
                    self.audio.add_tags()
                else:
                    self.audio.tags = ID3()
            
            if lyric_type == LyricType.UNSYNCED:
                # Embed as USLT tag (ID3)
                if hasattr(self.audio.tags, 'add'):
                    self.audio.tags.add(USLT(encoding=Encoding.UTF8, lang=language, text=lyrics))
                # Embed as ©lyr tag (MP4)
                elif isinstance(self.audio, MP4):
                    self.audio.tags['©lyr'] = lyrics
            
            elif lyric_type == LyricType.ROMANIZED:
                # Embed as custom TXXX tag (ID3)
                if hasattr(self.audio.tags, 'add'):
                    self.audio.tags.add(
                        TXXX(encoding=Encoding.UTF8, desc='Romanized_Lyrics', text=lyrics)
                    )
                # Embed as custom tag (MP4)
                elif isinstance(self.audio, MP4):
                    self.audio.tags['----:com.apple.iTunes:Romanized_Lyrics'] = lyrics.encode('utf-8')
            
            # Save changes
            self.audio.save()
            logger.info(f"Embedded {lyric_type.value} lyrics to {self.file_path.name}")
            return True
        
        except Exception as e:
            logger.error(f"Error embedding lyrics: {e}")
            return False
    
    def embed_lrc_content(self, lrc_content: str) -> bool:
        """
        Embed LRC format lyrics as romanized synced lyrics.
        
        Args:
            lrc_content: LRC format lyrics content
            
        Returns:
            True if successful
        """
        return self.embed_lyrics(lrc_content, LyricType.ROMANIZED)
