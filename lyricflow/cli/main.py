"""Command-line interface for LyricFlow."""

import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

from lyricflow.core.lyrics_sync import LyricsSync
from lyricflow.core.romanizer import Romanizer
from lyricflow.utils.config import Config
from lyricflow.utils.logging import setup_logger

console = Console()
logger = None


def init_logger(verbose: bool = False):
    """Initialize logger."""
    global logger
    logger = setup_logger(verbose=verbose)


@click.group()
@click.version_option(version="0.1.0", prog_name="lyricflow")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx, verbose):
    """LyricFlow - Automated processing and embedding of song lyrics."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    init_logger(verbose)


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--recursive/--no-recursive', default=True, help='Process directories recursively')
@click.option('--api', type=click.Choice(['local', 'openai', 'gemini']), help='Romanization API to use')
@click.option('--use-ai', is_flag=True, help='Use AI romanization')
@click.option('--overwrite', is_flag=True, help='Force reprocessing existing lyrics')
@click.option('--no-embed', is_flag=True, help='Generate LRC files but do not embed in audio')
@click.option('--dry-run', is_flag=True, help='Simulate processing without making changes')
@click.pass_context
def process(ctx, path, recursive, api, use_ai, overwrite, no_embed, dry_run):
    """Process audio file(s) to romanize and embed lyrics.
    
    PATH can be a single audio file or a directory.
    """
    path = Path(path)
    verbose = ctx.obj.get('verbose', False)
    
    # Load config
    config = Config.load()
    if api:
        config.api.default_provider = api
    
    # Initialize lyrics sync
    lyrics_sync = LyricsSync(config)
    
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]")
    
    # Process file or directory
    if path.is_file():
        console.print(f"[cyan]Processing file: {path.name}[/cyan]")
        
        if not dry_run:
            result = lyrics_sync.process_audio_file(path, use_ai, overwrite, no_embed)
            display_result(result)
        else:
            console.print(f"  Would process: {path}")
    
    elif path.is_dir():
        console.print(f"[cyan]Processing directory: {path}[/cyan]")
        console.print(f"  Recursive: {recursive}")
        
        if not dry_run:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Processing files...", total=None)
                results = lyrics_sync.process_directory(path, recursive, use_ai, overwrite, no_embed)
                progress.update(task, completed=True)
            
            display_summary(results)
        else:
            # Find files that would be processed
            audio_extensions = {'.mp3', '.m4a', '.flac', '.ogg', '.opus', '.wma'}
            if recursive:
                files = [f for ext in audio_extensions for f in path.rglob(f'*{ext}')]
            else:
                files = [f for ext in audio_extensions for f in path.glob(f'*{ext}')]
            
            console.print(f"\n[yellow]Would process {len(files)} files:[/yellow]")
            for f in files[:10]:  # Show first 10
                console.print(f"  - {f.name}")
            if len(files) > 10:
                console.print(f"  ... and {len(files) - 10} more")
    else:
        console.print(f"[red]Error: {path} is neither a file nor directory[/red]")
        sys.exit(1)


@cli.command()
@click.argument('input_text', required=False)
@click.option('--file', '-f', type=click.Path(exists=True), help='Input file to romanize')
@click.option('--api', type=click.Choice(['local', 'openai', 'gemini']), help='Romanization API to use')
@click.option('--use-ai', is_flag=True, help='Use AI romanization')
@click.option('--language', '-l', default='ja', help='Source language (default: ja)')
@click.pass_context
def romanize(ctx, input_text, file, api, use_ai, language):
    """Romanize Japanese text.
    
    INPUT_TEXT: Text to romanize (or use --file for file input, or stdin)
    """
    config = Config.load()
    if api:
        config.api.default_provider = api
    
    romanizer = Romanizer(config)
    
    # Get input text
    if file:
        text = Path(file).read_text(encoding='utf-8')
    elif input_text:
        text = input_text
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        console.print("[red]Error: No input provided. Use argument, --file, or pipe input.[/red]")
        sys.exit(1)
    
    # Romanize
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Romanizing text...", total=None)
            result = romanizer.romanize(text.strip(), language, use_ai)
            progress.update(task, completed=True)
        
        console.print("\n[green]Romanized text:[/green]")
        console.print(result)
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('audio_file', type=click.Path(exists=True))
@click.option('--model', default='medium', help='Whisper model size (tiny, base, small, medium, large)')
@click.option('--device', type=click.Choice(['cpu', 'cuda']), default='cpu', help='Device for processing')
@click.option('--language', '-l', default='ja', help='Audio language (default: ja)')
@click.option('--output', '-o', type=click.Path(), help='Output LRC file path')
@click.option('--word-level', is_flag=True, help='Generate word-level timestamps')
@click.pass_context
def generate(ctx, audio_file, model, device, language, output, word_level):
    """Generate lyrics from audio using Whisper ASR.
    
    AUDIO_FILE: Path to audio file
    """
    try:
        from lyricflow.core.whisper_gen import generate_lyrics_from_audio, WHISPER_AVAILABLE
    except ImportError:
        WHISPER_AVAILABLE = False
    
    if not WHISPER_AVAILABLE:
        console.print("[red]Error: Whisper ASR is not installed[/red]")
        console.print("\nInstall with: pip install lyricflow[whisper]")
        console.print("or: pip install openai-whisper torch")
        sys.exit(1)
    
    audio_path = Path(audio_file)
    
    # Determine output path
    if output:
        output_path = Path(output)
    else:
        output_path = audio_path.parent / f"{audio_path.stem}_whisper.lrc"
    
    console.print(f"[cyan]Generating lyrics from: {audio_path.name}[/cyan]")
    console.print(f"  Model: {model}")
    console.print(f"  Device: {device}")
    console.print(f"  Language: {language}")
    console.print(f"  Word-level: {word_level}")
    console.print(f"  Output: {output_path}")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Transcribing audio...", total=None)
            
            lrc_content = generate_lyrics_from_audio(
                audio_path,
                output_path=output_path,
                language=language,
                model_size=model,
                device=device,
                word_level=word_level
            )
            
            progress.update(task, completed=True)
        
        console.print(f"\n[green]✓ Lyrics generated successfully![/green]")
        console.print(f"  Saved to: {output_path}")
        
        # Show preview
        lines = lrc_content.split('\n')
        console.print("\n[cyan]Preview (first 10 lines):[/cyan]")
        for line in lines[:10]:
            console.print(f"  {line}")
        
        if len(lines) > 10:
            console.print(f"  ... ({len(lines) - 10} more lines)")
    
    except Exception as e:
        console.print(f"[red]Error generating lyrics: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.pass_context
def config_cmd(ctx):
    """View current configuration."""
    config = Config.load()
    
    table = Table(title="LyricFlow Configuration", show_header=True)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("API Provider", config.api.default_provider)
    table.add_row("OpenAI API Key", "***" if config.api.openai_api_key else "Not set")
    table.add_row("OpenAI Base URL", config.api.openai_base_url)
    table.add_row("OpenAI Model", config.api.openai_model)
    table.add_row("Gemini API Key", "***" if config.api.gemini_api_key else "Not set")
    table.add_row("Gemini Model", config.api.gemini_model)
    table.add_row("", "")
    table.add_row("Language", config.processing.language)
    table.add_row("Skip Existing", str(config.processing.skip_existing_lyrics))
    table.add_row("", "")
    table.add_row("Whisper Model", config.whisper.model_size)
    table.add_row("Whisper Device", config.whisper.device)
    table.add_row("", "")
    table.add_row("Caching", str(config.caching.enabled))
    table.add_row("Cache TTL", f"{config.caching.ttl} seconds")
    
    console.print(table)
    
    # Show config file locations
    console.print("\n[cyan]Config file locations (checked in order):[/cyan]")
    console.print("  1. ./config.yaml")
    console.print("  2. ~/.lyricflow/config.yaml")
    console.print("  3. Environment variables (OPENAI_API_KEY, GEMINI_API_KEY, GEMINI_MODEL, etc.)")


def display_result(result: dict):
    """Display processing result for a single file."""
    status_color = {
        'success': 'green',
        'partial': 'yellow',
        'skipped': 'blue',
        'no_lyrics': 'yellow',
        'error': 'red'
    }.get(result['status'], 'white')
    
    console.print(f"\n[{status_color}]Status: {result['status'].upper()}[/{status_color}]")
    console.print("\nSteps taken:")
    for step in result['steps']:
        console.print(f"  • {step}")


def display_summary(results: list):
    """Display summary of batch processing."""
    table = Table(title="Processing Summary", show_header=True)
    table.add_column("Status", style="cyan")
    table.add_column("Count", justify="right", style="green")
    
    from collections import Counter
    status_counts = Counter(r['status'] for r in results)
    
    for status, count in status_counts.items():
        table.add_row(status.upper(), str(count))
    
    console.print("\n")
    console.print(table)
    
    # Show failed files
    errors = [r for r in results if r['status'] == 'error']
    if errors:
        console.print("\n[red]Failed files:[/red]")
        for error in errors:
            console.print(f"  • {Path(error['file']).name}")
            if error['steps']:
                console.print(f"    Error: {error['steps'][-1]}")


@cli.command()
@click.option('--title', '-t', help='Song title')
@click.option('--artist', '-a', help='Artist name')
@click.option('--album', '-l', help='Album name')
@click.option('--audio', type=click.Path(exists=True), help='Audio file to embed lyrics')
@click.option('--output', '-o', type=click.Path(), help='Output LRC file path')
@click.option('--provider', '-p', type=click.Choice(['lrclib', 'musixmatch']), default='lrclib', help='Lyrics provider')
@click.option('--translation', is_flag=True, help='Fetch translation (Musixmatch only)')
@click.option('--romanization', is_flag=True, help='Fetch romanization')
@click.option('--embed', is_flag=True, help='Embed lyrics to audio file')
@click.option('--interactive', '-i', is_flag=True, help='Launch TUI for interactive selection')
@click.pass_context
def fetch(ctx, title, artist, album, audio, output, provider, translation, romanization, embed, interactive):
    """Fetch lyrics from online providers (LRCLIB or Musixmatch).
    
    Examples:
    
      # Interactive mode (no title required)
      lyricflow fetch --interactive
      lyricflow fetch -i --audio song.m4a
      
      # Interactive with pre-filled fields
      lyricflow fetch -i -t "Song Title" -a "Artist"
      
      # Fetch from LRCLIB (free, default)
      lyricflow fetch -t "Bohemian Rhapsody" -a "Queen"
      
      # Use Musixmatch provider
      lyricflow fetch -t "Song" -a "Artist" --provider musixmatch
      
      # Fetch and embed to audio file
      lyricflow fetch -t "Song" -a "Artist" --audio song.m4a --embed
      
      # With romanization (Japanese songs)
      lyricflow fetch -t "Sakura" -a "Ikimono Gakari" --romanization
      
      # Musixmatch with translation
      lyricflow fetch -t "Song" -a "Artist" -p musixmatch --translation
    """
    try:
        # Interactive TUI mode
        if interactive:
            from lyricflow.tui import launch_tui
            audio_path = Path(audio) if audio else None
            launch_tui(
                audio_file=audio_path,
                provider=provider,
                initial_title=title or "",
                initial_artist=artist or "",
                initial_album=album or ""
            )
            return
        
        # Non-interactive mode requires title
        if not title:
            console.print("[red]❌ Error: --title is required in non-interactive mode[/red]")
            console.print("[yellow]Tip: Use --interactive (-i) to launch TUI without title[/yellow]")
            sys.exit(1)
        
        # CLI mode - fetch best match automatically
        from lyricflow.core.lyrics_provider import UnifiedLyricsFetcher
        
        # Show provider info
        provider_names = {"lrclib": "LRCLIB", "musixmatch": "Musixmatch"}
        provider_name = provider_names.get(provider, provider)
        
        console.print(f"\n[cyan]🔍 Searching on {provider_name}:[/cyan] {title} by {artist or 'Unknown'}")
        
        # Warn about translation on non-Musixmatch
        if translation and provider != "musixmatch":
            console.print("[yellow]⚠️  Translation only available with Musixmatch provider[/yellow]")
            translation = False
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Searching for lyrics...", total=None)
            
            fetcher = UnifiedLyricsFetcher(provider=provider)
            
            # First, search for matches
            results = fetcher.search(
                title=title,
                artist=artist or "",
                album=album
            )
            
            if not results:
                progress.update(task, completed=True)
                console.print("[red]❌ No lyrics found[/red]")
                sys.exit(1)
            
            # Show found results
            console.print(f"\n[cyan]Found {len(results)} track(s):[/cyan]")
            for i, res in enumerate(results[:5], 1):  # Show first 5
                duration_str = "?"
                if res.get('duration'):
                    dur = int(res['duration'])
                    duration_str = f"{dur // 60}:{dur % 60:02d}"
                
                lyric_types = []
                if res.get('has_synced'):
                    lyric_types.append("Synced")
                if res.get('has_plain'):
                    lyric_types.append("Plain")
                type_str = ", ".join(lyric_types) if lyric_types else "No lyrics"
                
                console.print(f"  {i}. {res.get('title')} - {res.get('artist')} [{duration_str}] ({type_str})")
            
            if len(results) > 5:
                console.print(f"  ... and {len(results) - 5} more")
            
            # Use the best match (first result)
            best_match = results[0]
            console.print(f"\n[green]Using best match:[/green] {best_match.get('title')} - {best_match.get('artist')}")
            
            # Fetch full lyrics for the best match
            progress.update(task, description="Fetching full lyrics...")
            result = fetcher.fetch(
                title=best_match['title'],
                artist=best_match['artist'],
                album=best_match.get('album'),
                duration=best_match.get('duration'),
                fetch_translation=translation,
                fetch_romanization=romanization
            )
            
            progress.update(task, completed=True)
        
        if not result:
            console.print("[red]❌ No lyrics found[/red]")
            sys.exit(1)
        
        # Display result info
        console.print(f"\n[green]✅ Found match:[/green]")
        console.print(f"  Provider: {provider_name}")
        console.print(f"  Title:    {result['title']}")
        console.print(f"  Artist:   {result['artist']}")
        console.print(f"  Album:    {result.get('album') or 'Unknown'}")
        
        if result.get('duration'):
            duration = int(result['duration'])  # Ensure it's an integer
            console.print(f"  Duration: {duration // 60}:{duration % 60:02d}")
        
        if result.get('rating'):
            console.print(f"  Rating:   {result['rating']}")
        
        if result.get('has_synced'):
            console.print(f"  Type:     [green]Synced (LRC)[/green]")
        elif result.get('has_plain'):
            console.print(f"  Type:     [yellow]Unsynced[/yellow]")
        
        if result.get('instrumental'):
            console.print(f"  Note:     [yellow]Instrumental track[/yellow]")
        
        # Show romanization status
        if result.get('romanization'):
            console.print("  Extras:   [green]✅ Romanization[/green]")
        
        if result.get('translation'):
            console.print("            [green]✅ Translation[/green]")
        
        # Save to file
        if output or audio:
            output_path = Path(output) if output else Path(audio).with_suffix('.lrc')
            
            if fetcher.save_lrc(result, output_path):
                console.print(f"\n[green]✅ Saved lyrics to:[/green] {output_path}")
                
                # Romanization is saved automatically by save_lrc
                if result.get('romanization'):
                    romaji_path = output_path.with_stem(output_path.stem + "_romaji")
                    console.print(f"[green]✅ Saved romanization to:[/green] {romaji_path}")
            else:
                console.print("[red]❌ Failed to save lyrics[/red]")
                sys.exit(1)
        
        # Embed to audio file
        if embed and audio:
            from lyricflow.core.audio_handler import AudioHandler
            
            console.print(f"\n[cyan]📝 Embedding lyrics to audio file...[/cyan]")
            
            try:
                audio_path = Path(audio)
                handler = AudioHandler(audio_path)
                
                lyrics_to_embed = result.get('synced_lyrics') or result.get('plain_lyrics')
                handler.embed_lyrics(lyrics_to_embed, dry_run=False)
                
                console.print(f"[green]✅ Embedded lyrics to:[/green] {audio_path}")
            except Exception as e:
                console.print(f"[red]❌ Embedding failed:[/red] {e}")
                sys.exit(1)
        
        # Show preview if not saving
        if not output and not audio:
            console.print("\n[cyan]📄 Lyrics Preview:[/cyan]")
            lyrics = result.get('synced_lyrics') or result.get('plain_lyrics')
            if lyrics:
                preview_lines = lyrics.split('\n')[:10]
                for line in preview_lines:
                    console.print(f"  {line}")
                if len(lyrics.split('\n')) > 10:
                    console.print("  ...")
                console.print(f"\n[dim]Use --output or --audio to save the lyrics[/dim]")
        
        console.print("\n[green]✨ Done![/green]")
        
    except ImportError as e:
        if 'textual' in str(e) and interactive:
            console.print("[red]❌ Textual not installed. Install with:[/red]")
            console.print("   pip install lyricflow[tui]")
        elif 'requests' in str(e):
            console.print("[red]❌ requests not installed. Install with:[/red]")
            console.print("   pip install requests")
        else:
            console.print(f"[red]❌ Import error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {e}")
        if ctx.obj.get('verbose'):
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


# Rename for consistency
cli.add_command(config_cmd, name='config')


if __name__ == '__main__':
    cli(obj={})
