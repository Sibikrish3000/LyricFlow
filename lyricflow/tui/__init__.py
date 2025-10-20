"""
Textual TUI for LyricFlow - Interactive lyrics search and selection.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
    from textual.widgets import (
        Header, Footer, Input, Button, Label,
        DataTable, TextArea, Checkbox, RadioButton, RadioSet
    )
    from textual.binding import Binding
    from textual.screen import Screen
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False

from lyricflow.core.lyrics_provider import UnifiedLyricsFetcher
from lyricflow.core.audio_handler import AudioHandler

logger = logging.getLogger(__name__)


if TEXTUAL_AVAILABLE:
    class SearchScreen(Screen):
        """Main search screen for lyrics."""
        
        BINDINGS = [
            Binding("ctrl+q", "quit", "Quit"),
            Binding("ctrl+s", "search", "Search"),
            Binding("escape", "clear", "Clear"),
        ]
        
        CSS = """
        Screen {
            background: $surface;
        }
        
        #title-label {
            text-align: center;
            text-style: bold;
            color: $accent;
            padding: 1;
            background: $boost;
        }
        
        #input-container {
            height: auto;
            padding: 1 2;
        }
        
        .input-group {
            height: auto;
            margin: 0 1;
        }
        
        .input-group Label {
            margin-bottom: 1;
            color: $text;
        }
        
        .input-group Input {
            width: 100%;
        }
        
        #provider-container {
            height: auto;
            padding: 1 2;
            border: solid $primary;
        }
        
        #options-container {
            height: auto;
            padding: 1 2;
            align: center middle;
        }
        
        #status-label {
            text-align: center;
            padding: 1;
            color: $warning;
        }
        
        #results-table {
            height: 15;
            margin: 1 2;
            border: solid $accent;
        }
        
        #preview-container {
            height: 20;
            margin: 1 2;
            border: solid $primary;
        }
        
        #preview-text {
            height: 1fr;
        }
        
        #button-container {
            height: auto;
            padding: 1 2;
            align: center middle;
        }
        
        Button {
            margin: 0 1;
        }
        """
        
        def __init__(
            self,
            audio_file: Optional[Path] = None,
            provider: str = "lrclib",
            initial_title: str = "",
            initial_artist: str = "",
            initial_album: str = ""
        ):
            super().__init__()
            self.audio_file = audio_file
            self.provider = provider
            self.results: List[Dict[str, Any]] = []
            self.selected_result: Optional[Dict[str, Any]] = None
            
            # Pre-fill from parameters or audio file metadata
            self.initial_title = initial_title
            self.initial_artist = initial_artist
            self.initial_album = initial_album
            
            # If no initial values provided, try to get from audio file
            if audio_file and audio_file.exists() and not (initial_title or initial_artist):
                try:
                    handler = AudioHandler(audio_file)
                    metadata = handler.get_metadata()
                    self.initial_title = self.initial_title or metadata.get('title', '')
                    self.initial_artist = self.initial_artist or metadata.get('artist', '')
                    self.initial_album = self.initial_album or metadata.get('album', '')
                except Exception as e:
                    logger.error(f"Error reading audio metadata: {e}")
        
        def compose(self) -> ComposeResult:
            """Compose the UI."""
            yield Header()
            
            yield Label("🎵 LyricFlow - Lyrics Searcher", id="title-label")
            
            # Provider selection
            with Container(id="provider-container"):
                yield Label("Provider:")
                with RadioSet(id="provider-radio"):
                    yield RadioButton("LRCLIB (Free)", value=True, id="lrclib-radio")
                    yield RadioButton("Musixmatch", id="musixmatch-radio")
            
            # Input fields
            with Container(id="input-container"):
                with Horizontal():
                    with Vertical(classes="input-group"):
                        yield Label("Title: *")
                        yield Input(
                            placeholder="Enter song title",
                            value=self.initial_title,
                            id="title-input"
                        )
                    
                    with Vertical(classes="input-group"):
                        yield Label("Artist:")
                        yield Input(
                            placeholder="Enter artist name",
                            value=self.initial_artist,
                            id="artist-input"
                        )
                
                with Horizontal():
                    with Vertical(classes="input-group"):
                        yield Label("Album (optional):")
                        yield Input(
                            placeholder="Enter album name",
                            value=self.initial_album,
                            id="album-input"
                        )
            
            # Options
            with Container(id="options-container"):
                with Horizontal():
                    yield Checkbox("Romanization", value=False, id="romanization-check")
                    yield Checkbox("Translation (Musixmatch only)", value=False, id="translation-check")
                    yield Button("Search", variant="primary", id="search-button")
            
            # Status
            yield Label("", id="status-label")
            
            # Results table
            yield DataTable(id="results-table")
            
            # Preview
            with ScrollableContainer(id="preview-container"):
                yield Label("📄 Lyrics Preview", id="preview-title")
                yield TextArea("", id="preview-text", read_only=True)
            
            # Action buttons
            with Container(id="button-container"):
                with Horizontal():
                    yield Button("Save LRC", variant="success", id="save-button", disabled=True)
                    yield Button("Embed to Audio", variant="success", id="embed-button", disabled=True)
                    yield Button("Clear", variant="warning", id="clear-button")
                    yield Button("Quit", variant="error", id="quit-button")
            
            yield Footer()
        
        def on_mount(self) -> None:
            """Initialize the table."""
            table = self.query_one("#results-table", DataTable)
            table.add_columns("Title", "Artist", "Album", "Duration", "Type", "Provider")
            table.cursor_type = "row"
            
            # Set provider based on initial selection
            if self.provider == "musixmatch":
                musixmatch_radio = self.query_one("#musixmatch-radio", RadioButton)
                musixmatch_radio.value = True
        
        def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
            """Handle provider selection change."""
            if event.radio_set.id == "provider-radio":
                if event.pressed.id == "lrclib-radio":
                    self.provider = "lrclib"
                    self.query_one("#status-label", Label).update("Provider: LRCLIB (Free)")
                elif event.pressed.id == "musixmatch-radio":
                    self.provider = "musixmatch"
                    self.query_one("#status-label", Label).update("Provider: Musixmatch")
        
        def on_button_pressed(self, event: Button.Pressed) -> None:
            """Handle button presses."""
            if event.button.id == "search-button":
                self.action_search()
            elif event.button.id == "save-button":
                self.save_lrc()
            elif event.button.id == "embed-button":
                self.embed_to_audio()
            elif event.button.id == "clear-button":
                self.action_clear()
            elif event.button.id == "quit-button":
                self.app.exit()
        
        def on_input_submitted(self, event: Input.Submitted) -> None:
            """Handle Enter key in input fields."""
            if event.input.id in ["title-input", "artist-input", "album-input"]:
                self.action_search()
        
        def action_search(self) -> None:
            """Perform lyrics search."""
            title_input = self.query_one("#title-input", Input)
            artist_input = self.query_one("#artist-input", Input)
            album_input = self.query_one("#album-input", Input)
            romanization_check = self.query_one("#romanization-check", Checkbox)
            translation_check = self.query_one("#translation-check", Checkbox)
            status_label = self.query_one("#status-label", Label)
            
            title = title_input.value.strip()
            artist = artist_input.value.strip()
            album = album_input.value.strip()
            
            if not title:
                status_label.update("⚠️ Please enter a song title")
                return
            
            # Warn about translation on non-Musixmatch
            fetch_translation = translation_check.value
            if fetch_translation and self.provider != "musixmatch":
                status_label.update("⚠️ Translation only available with Musixmatch")
                fetch_translation = False
            
            status_label.update(f"🔍 Searching on {self.provider.upper()}...")
            self.results = []
            
            # Store search params for worker
            self.search_params = {
                'title': title,
                'artist': artist,
                'album': album,
                'fetch_translation': fetch_translation,
                'fetch_romanization': romanization_check.value
            }
            
            # Run search in worker thread to avoid blocking UI
            self.run_worker(self._search_worker, thread=True)
        
        def _search_worker(self) -> List[Dict[str, Any]]:
            """Worker thread for searching lyrics."""
            try:
                params = self.search_params
                fetcher = UnifiedLyricsFetcher(provider=self.provider)
                
                # Search for ALL results (not just best match)
                results = fetcher.search(
                    title=params['title'],
                    artist=params['artist'] if params['artist'] else None,
                    album=params['album'] if params['album'] else None
                )
                
                return results if results else []
                
            except Exception as e:
                logger.error(f"Search error: {e}", exc_info=True)
                return []
        
        def _display_search_results(self, results: List[Dict[str, Any]]) -> None:
            """Display search results in the table."""
            status_label = self.query_one("#status-label", Label)
            table = self.query_one("#results-table", DataTable)
            table.clear()
            
            try:
                if not results:
                    status_label.update("❌ No results found")
                    return
                
                # Ensure results is a list
                if not isinstance(results, list):
                    results = [results]
                
                self.results = results
                
                # Add all results to table
                for result in results:
                    if not isinstance(result, dict):
                        continue
                    
                    duration_str = "?"
                    if result.get('duration'):
                        dur = int(result['duration'])
                        duration_str = f"{dur // 60}:{dur % 60:02d}"
                    
                    lyric_type = []
                    if result.get('has_synced'):
                        lyric_type.append("Synced")
                    if result.get('has_plain'):
                        lyric_type.append("Plain")
                    type_str = ", ".join(lyric_type) if lyric_type else "None"
                    
                    table.add_row(
                        result.get('title', ''),
                        result.get('artist', ''),
                        result.get('album', '-'),
                        duration_str,
                        type_str,
                        result.get('provider', '').upper()
                    )
                
                status_label.update(f"✅ Found {len(results)} result(s) from {self.provider.upper()}")
                
            except Exception as e:
                status_label.update(f"❌ Error: {str(e)}")
                logger.error(f"Display results error: {e}", exc_info=True)
        
        def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
            """Handle row selection in results table."""
            if event.cursor_row < len(self.results):
                self.selected_result = self.results[event.cursor_row]
                
                # Fetch full lyrics if not already present
                if not self.selected_result.get('synced_lyrics') and not self.selected_result.get('plain_lyrics'):
                    status_label = self.query_one("#status-label", Label)
                    status_label.update("🔄 Fetching lyrics for selected track...")
                    
                    # Store index for worker
                    self.selected_index = event.cursor_row
                    
                    # Fetch lyrics in worker thread
                    self.run_worker(self._fetch_lyrics_worker, thread=True)
                else:
                    self.update_preview()
                    
                    # Enable action buttons
                    self.query_one("#save-button", Button).disabled = False
                    if self.audio_file:
                        self.query_one("#embed-button", Button).disabled = False
        
        def _fetch_lyrics_worker(self) -> Dict[str, Any]:
            """Worker thread for fetching full lyrics."""
            try:
                result = self.results[self.selected_index]
                fetcher = UnifiedLyricsFetcher(provider=self.provider)
                
                # Fetch full lyrics for this specific result
                full_result = fetcher.fetch(
                    title=result['title'],
                    artist=result['artist'],
                    album=result.get('album'),
                    duration=result.get('duration')
                )
                
                if full_result:
                    # Update the result with full lyrics
                    self.results[self.selected_index].update(full_result)
                    return self.results[self.selected_index]
                
                return result
                
            except Exception as e:
                logger.error(f"Fetch lyrics error: {e}", exc_info=True)
                return result
        
        def on_worker_state_changed(self, event) -> None:
            """Handle worker state changes."""
            if event.worker.name == "_search_worker":
                if event.worker.is_finished:
                    self._display_search_results(event.worker.result)
            elif event.worker.name == "_fetch_lyrics_worker":
                if event.worker.is_finished:
                    self.selected_result = event.worker.result
                    self.update_preview()
                    
                    # Enable action buttons
                    self.query_one("#save-button", Button).disabled = False
                    if self.audio_file:
                        self.query_one("#embed-button", Button).disabled = False
                    
                    # Update status
                    status_label = self.query_one("#status-label", Label)
                    status_label.update("✅ Lyrics loaded")
        
        def update_preview(self) -> None:
            """Update the lyrics preview."""
            if not self.selected_result:
                return
            
            preview = self.query_one("#preview-text", TextArea)
            
            # Build preview text
            text = f"{'=' * 60}\n"
            text += f"Title:    {self.selected_result.get('title', '')}\n"
            text += f"Artist:   {self.selected_result.get('artist', '')}\n"
            text += f"Album:    {self.selected_result.get('album', 'Unknown')}\n"
            
            if self.selected_result.get('duration'):
                dur = int(self.selected_result['duration'])
                text += f"Duration: {dur // 60}:{dur % 60:02d}\n"
            
            text += f"Provider: {self.selected_result.get('provider', '').upper()}\n"
            text += f"{'=' * 60}\n\n"
            
            # Show synced lyrics first, then unsynced
            if self.selected_result.get('synced_lyrics'):
                text += "🎵 SYNCED LYRICS (LRC):\n"
                text += f"{'=' * 60}\n"
                text += self.selected_result['synced_lyrics']
                text += "\n\n"
            
            if self.selected_result.get('plain_lyrics'):
                text += "📝 PLAIN LYRICS:\n"
                text += f"{'=' * 60}\n"
                text += self.selected_result['plain_lyrics']
                text += "\n\n"
            
            if self.selected_result.get('translation'):
                text += "🌍 TRANSLATION:\n"
                text += f"{'=' * 60}\n"
                text += self.selected_result['translation']
                text += "\n\n"
            
            if self.selected_result.get('romanization'):
                text += "🔤 ROMANIZATION:\n"
                text += f"{'=' * 60}\n"
                text += self.selected_result['romanization']
            
            preview.text = text
        
        def save_lrc(self) -> None:
            """Save selected lyrics to LRC file."""
            if not self.selected_result:
                return
            
            status_label = self.query_one("#status-label", Label)
            
            try:
                fetcher = UnifiedLyricsFetcher(provider=self.provider)
                
                if self.audio_file:
                    # Save next to audio file
                    output_path = self.audio_file.with_suffix('.lrc')
                else:
                    # Save in current directory
                    title = self.selected_result.get('title', 'song')
                    artist = self.selected_result.get('artist', 'artist')
                    safe_filename = f"{artist} - {title}.lrc"
                    safe_filename = "".join(c for c in safe_filename if c.isalnum() or c in (' ', '-', '_', '.'))
                    output_path = Path(safe_filename)
                
                if fetcher.save_lrc(self.selected_result, output_path):
                    status_label.update(f"✅ Saved to {output_path.name}")
                else:
                    status_label.update("❌ Failed to save LRC")
                    
            except Exception as e:
                status_label.update(f"❌ Error: {str(e)}")
                logger.error(f"Save error: {e}", exc_info=True)
        
        def embed_to_audio(self) -> None:
            """Embed lyrics to audio file."""
            if not self.selected_result or not self.audio_file:
                return
            
            status_label = self.query_one("#status-label", Label)
            
            try:
                handler = AudioHandler(self.audio_file)
                
                # Embed synced lyrics if available
                lyrics_to_embed = self.selected_result.get('synced_lyrics') or self.selected_result.get('plain_lyrics')
                
                if not lyrics_to_embed:
                    status_label.update("❌ No lyrics to embed")
                    return
                
                handler.embed_lyrics(lyrics_to_embed, dry_run=False)
                status_label.update(f"✅ Embedded lyrics to {self.audio_file.name}")
                
            except Exception as e:
                status_label.update(f"❌ Error: {str(e)}")
                logger.error(f"Embed error: {e}", exc_info=True)
        
        def action_clear(self) -> None:
            """Clear search results."""
            self.query_one("#title-input", Input).value = ""
            self.query_one("#artist-input", Input).value = ""
            self.query_one("#album-input", Input).value = ""
            self.query_one("#results-table", DataTable).clear()
            self.query_one("#preview-text", TextArea).text = ""
            self.query_one("#status-label", Label).update("")
            self.query_one("#save-button", Button).disabled = True
            self.query_one("#embed-button", Button).disabled = True
            self.results = []
            self.selected_result = None


    class LyricFlowTUI(App):
        """LyricFlow Textual TUI Application."""
        
        TITLE = "LyricFlow - Lyrics Searcher"
        
        def __init__(
            self,
            audio_file: Optional[Path] = None,
            provider: str = "lrclib",
            initial_title: str = "",
            initial_artist: str = "",
            initial_album: str = ""
        ):
            super().__init__()
            self.audio_file = audio_file
            self.provider = provider
            self.initial_title = initial_title
            self.initial_artist = initial_artist
            self.initial_album = initial_album
        
        def on_mount(self) -> None:
            """Mount the search screen."""
            self.push_screen(SearchScreen(
                self.audio_file,
                self.provider,
                self.initial_title,
                self.initial_artist,
                self.initial_album
            ))


def launch_tui(
    audio_file: Optional[Path] = None,
    provider: str = "lrclib",
    initial_title: str = "",
    initial_artist: str = "",
    initial_album: str = ""
):
    """
    Launch the Textual TUI.
    
    Args:
        audio_file: Optional audio file path
        provider: Lyrics provider ("lrclib" or "musixmatch")
        initial_title: Pre-fill title field
        initial_artist: Pre-fill artist field
        initial_album: Pre-fill album field
    """
    if not TEXTUAL_AVAILABLE:
        raise ImportError("textual library is required for TUI. Install with: pip install lyricflow[tui]")
    
    # Disable console logging to prevent overlay issues in TUI
    # Save original state
    root_logger = logging.getLogger()
    lyricflow_logger = logging.getLogger('lyricflow')
    
    original_level = root_logger.level
    original_handlers = root_logger.handlers[:]
    lyricflow_handlers = lyricflow_logger.handlers[:]
    
    # Remove all stream handlers (console output)
    for handler in original_handlers:
        if isinstance(handler, logging.StreamHandler) and hasattr(handler, 'stream'):
            # Check if it's stdout/stderr
            import sys
            if handler.stream in (sys.stdout, sys.stderr):
                root_logger.removeHandler(handler)
    
    for handler in lyricflow_handlers:
        if isinstance(handler, logging.StreamHandler) and hasattr(handler, 'stream'):
            import sys
            if handler.stream in (sys.stdout, sys.stderr):
                lyricflow_logger.removeHandler(handler)
    
    # Optionally: Add file handler for debugging
    # file_handler = logging.FileHandler('lyricflow_tui.log')
    # file_handler.setLevel(logging.DEBUG)
    # lyricflow_logger.addHandler(file_handler)
    
    try:
        app = LyricFlowTUI(audio_file, provider, initial_title, initial_artist, initial_album)
        app.run()
    finally:
        # Restore logging handlers
        for handler in original_handlers:
            if handler not in root_logger.handlers:
                root_logger.addHandler(handler)
        for handler in lyricflow_handlers:
            if handler not in lyricflow_logger.handlers:
                lyricflow_logger.addHandler(handler)
