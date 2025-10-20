"""
LyricFlow - A modular Python toolkit for automated processing and embedding of song lyrics.

This package provides tools for:
- Audio metadata handling and lyric embedding
- Romanization of Japanese lyrics (local and AI-based)
- Translation of lyrics
- Automatic Speech Recognition (ASR) for lyric generation
- Synced lyrics (.lrc) processing
"""

__version__ = "0.1.0"
__author__ = "LyricFlow Contributors"

from lyricflow.core.romanizer import Romanizer
from lyricflow.core.audio_handler import AudioHandler
from lyricflow.core.lyrics_sync import LyricsSync

__all__ = [
    "Romanizer",
    "AudioHandler",
    "LyricsSync",
]
