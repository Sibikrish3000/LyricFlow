"""Lyrics synchronization and processing module."""

import re
from pathlib import Path
from typing import Optional, Tuple, List

from lyricflow.core.audio_handler import AudioHandler, LyricType
from lyricflow.core.romanizer import Romanizer
from lyricflow.utils.logging import get_logger
from lyricflow.utils.config import Config

logger = get_logger(__name__)


class LyricsSync:
    """Main class for synchronizing and processing lyrics."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize LyricsSync.
        
        Args:
            config: Configuration object
        """
        self.config = config or Config.load()
        self.romanizer = Romanizer(self.config)
    
    def find_lrc_file(self, audio_path: Path) -> Optional[Path]:
        """
        Find matching LRC file for audio file.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Path to LRC file if found, None otherwise
        """
        base_name = audio_path.stem
        parent_dir = audio_path.parent
        
        # Try exact match
        lrc_path = parent_dir / f"{base_name}.lrc"
        if lrc_path.exists():
            logger.debug(f"Found LRC file: {lrc_path}")
            return lrc_path
        
        # Try case-insensitive match
        for file in parent_dir.glob("*.lrc"):
            if file.stem.lower() == base_name.lower():
                logger.debug(f"Found LRC file (case-insensitive): {file}")
                return file
        
        logger.debug(f"No LRC file found for: {audio_path.name}")
        return None
    
    def romanize_lrc_content(self, lrc_content: str, use_ai: bool = False) -> str:
        """
        Romanize LRC file content.
        
        Args:
            lrc_content: LRC file content
            use_ai: Whether to use AI romanization
            
        Returns:
            Romanized LRC content
        """
        lines = lrc_content.strip().split('\n')
        romanized_lines = []
        lrc_pattern = re.compile(r'^(\[\d{2}:\d{2}[.,]\d{2,3}\])(.*)$')
        
        for line in lines:
            match = lrc_pattern.match(line.strip())
            
            if match:
                timestamp = match.group(1)
                japanese_text = match.group(2).strip()
                
                if japanese_text:
                    # Romanize the text
                    romaji_text = self.romanizer.romanize(
                        japanese_text,
                        language=self.config.processing.language,
                        use_ai=use_ai
                    )
                    romanized_lines.append(f"{timestamp} {romaji_text}")
                else:
                    romanized_lines.append(line.strip())
            else:
                # Keep non-timestamp lines as-is (metadata, etc.)
                romanized_lines.append(line.strip())
        
        return '\n'.join(romanized_lines)
    
    def save_romanized_lrc(self, lrc_path: Path, romanized_content: str) -> Path:
        """
        Save romanized LRC content to a new file.
        
        Args:
            lrc_path: Original LRC file path
            romanized_content: Romanized content
            
        Returns:
            Path to saved romanized LRC file
        """
        base_name = lrc_path.stem
        parent_dir = lrc_path.parent
        romaji_path = parent_dir / f"{base_name}_romaji.lrc"
        
        romaji_path.write_text(romanized_content, encoding='utf-8')
        logger.info(f"Saved romanized LRC: {romaji_path}")
        
        return romaji_path
    
    def process_audio_file(
        self,
        audio_path: Path,
        use_ai: bool = False,
        overwrite: bool = False,
        no_embed: bool = False,
    ) -> dict:
        """
        Process an audio file: find/generate romanized lyrics and embed them.
        
        Workflow:
        1. Check for existing romanized lyrics in tags (skip if present unless overwrite)
        2. Check for existing synced lyrics in tags (romanize and embed)
        3. Search for local .lrc file (romanize and embed)
        4. Return status indicating what was done
        
        Args:
            audio_path: Path to audio file
            use_ai: Whether to use AI romanization
            overwrite: Force reprocessing even if romanized lyrics exist
            no_embed: Generate LRC files but don't embed in audio
            
        Returns:
            Dictionary with processing status and steps taken
        """
        audio_path = Path(audio_path)
        steps = []
        status = "success"
        
        try:
            # Load audio file
            audio_handler = AudioHandler(audio_path)
            metadata = audio_handler.get_metadata()
            steps.append(f"Loaded audio file: {audio_path.name}")
            
            if metadata.get('title'):
                steps.append(f"Metadata: {metadata.get('artist', '')} - {metadata['title']}")
            
            # Step 1: Check for existing romanized lyrics
            if not overwrite and audio_handler.has_romanized_lyrics():
                logger.info(f"Romanized lyrics already exist in: {audio_path.name}")
                steps.append("Romanized lyrics already embedded (use --overwrite to force)")
                return {"file": str(audio_path), "status": "skipped", "steps": steps}
            
            # Step 2: Check for embedded synced lyrics
            if audio_handler.has_synced_lyrics():
                steps.append("Found embedded synced lyrics")
                synced_lyrics = audio_handler.get_lyrics(LyricType.SYNCED)
                
                if synced_lyrics:
                    logger.info("Romanizing embedded synced lyrics")
                    romanized = self.romanize_lrc_content(synced_lyrics, use_ai)
                    
                    if not no_embed:
                        audio_handler.embed_lrc_content(romanized)
                        steps.append("Romanized and embedded synced lyrics")
                    
                    # Also save as LRC file
                    lrc_path = audio_path.with_suffix('.lrc')
                    self.save_romanized_lrc(lrc_path, romanized)
                    steps.append(f"Saved romanized LRC: {lrc_path.name}_romaji.lrc")
                    
                    return {"file": str(audio_path), "status": status, "steps": steps}
            
            # Step 3: Search for local LRC file
            lrc_path = self.find_lrc_file(audio_path)
            
            if lrc_path:
                steps.append(f"Found local LRC file: {lrc_path.name}")
                logger.info(f"Processing LRC file: {lrc_path}")
                
                # Read and romanize LRC content
                lrc_content = lrc_path.read_text(encoding='utf-8')
                romanized = self.romanize_lrc_content(lrc_content, use_ai)
                
                # Save romanized LRC
                romaji_lrc_path = self.save_romanized_lrc(lrc_path, romanized)
                steps.append(f"Created {romaji_lrc_path.name}")
                
                # Embed in audio file
                if not no_embed:
                    success = audio_handler.embed_lrc_content(romanized)
                    if success:
                        steps.append("Embedded romanized lyrics in audio file")
                    else:
                        steps.append("Warning: Failed to embed lyrics in audio file")
                        status = "partial"
                
                return {"file": str(audio_path), "status": status, "steps": steps}
            
            # Step 4: No lyrics found
            steps.append("No synced lyrics or LRC file found")
            steps.append("Consider using: lyricflow generate <file> to create lyrics with Whisper")
            status = "no_lyrics"
        
        except Exception as e:
            logger.error(f"Error processing {audio_path}: {e}")
            steps.append(f"Error: {str(e)}")
            status = "error"
        
        return {"file": str(audio_path), "status": status, "steps": steps}
    
    def process_directory(
        self,
        directory: Path,
        recursive: bool = True,
        use_ai: bool = False,
        overwrite: bool = False,
        no_embed: bool = False,
    ) -> List[dict]:
        """
        Process all audio files in a directory.
        
        Args:
            directory: Directory path
            recursive: Process subdirectories
            use_ai: Use AI romanization
            overwrite: Force reprocessing
            no_embed: Don't embed in audio files
            
        Returns:
            List of results for each file
        """
        directory = Path(directory)
        audio_extensions = {'.mp3', '.m4a', '.flac', '.ogg', '.opus', '.wma'}
        
        results = []
        
        # Find all audio files
        if recursive:
            audio_files = [
                f for ext in audio_extensions
                for f in directory.rglob(f'*{ext}')
            ]
        else:
            audio_files = [
                f for ext in audio_extensions
                for f in directory.glob(f'*{ext}')
            ]
        
        logger.info(f"Found {len(audio_files)} audio files in {directory}")
        
        for audio_file in audio_files:
            logger.info(f"Processing: {audio_file.name}")
            result = self.process_audio_file(audio_file, use_ai, overwrite, no_embed)
            results.append(result)
        
        return results
