#!/usr/bin/env python3
"""
Entry point script for LyricFlow CLI.
This allows running: python -m lyricflow
"""

if __name__ == '__main__':
    from lyricflow.cli.main import cli
    cli(obj={})
