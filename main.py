#!/usr/bin/env python
"""
Noki Bin Dumpper - Albion Online Data Extractor
Main entry point for the application
"""
import sys
import os

# Prevent Python from creating cache files
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

import io
import argparse
from pathlib import Path
from rich.markdown import Markdown

# Force UTF-8 for console output to handle special characters properly
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from src import Config, Terminal, Platform, ServerType

def setup_environment():
    """Configure the environment and initialize paths."""
    # Set root path environment variable
    root_path = os.path.dirname(os.path.abspath(__file__))
    os.environ["AONOKI-DUMPPER-PATH"] = root_path
    
    # Initialize configuration paths
    Config.initialize_paths(root_path)
    
    # Setup logging
    Config.setup_logging()

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Albion Online Data Dumpper')
    
    parser.add_argument(
        '--path', 
        required=True, 
        help='Albion Online installation path'
    )
    
    parser.add_argument(
        '--server', 
        choices=['live', 'test'], 
        default='live',
        help='Game Server to export the files (default: live)'
    )
    
    parser.add_argument(
        '--output', 
        default=None,
        help='Output directory (optional)'
    )
    
    return parser.parse_args()

def check_update():
    """Check for updates and display notification if available."""
    update_info = Config.check_for_updates()

    if update_info:
        Terminal.print(f"====================================================")
        Terminal.print(f"New version available: v{update_info['latest_version']} (current: v{update_info['current_version']})")
        Terminal.print(f"Download: {update_info['release_url']}")
        
        # Display release notes if available
        if update_info['release_notes']:
            Terminal.print("\nRelease notes:")
            Terminal.print(Markdown(update_info['release_notes']))
        Terminal.print(f"====================================================")

def run():
    """Main entry point for the application."""
    # Setup environment
    setup_environment()
    
    # Display application banner
    Terminal.print(Config.create_banner())
    
    # Check for updates
    check_update()
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Validate Albion Online path
    albion_path = Path(args.path)
    if not albion_path.exists():
        Terminal.print(f"Albion Online installation path not found: {albion_path}")
        sys.exit(1)
    
    # Configure output directory
    output_dir = args.output
    if output_dir is None:
        output_dir = Config.OUTPUT_DIR
    else:
        output_dir = Path(output_dir)
        os.makedirs(output_dir, exist_ok=True)
    
    # Set server type
    server_type = ServerType.LIVE if args.server == 'live' else ServerType.TEST
    
    # Initialize platform and run extraction
    platform = Platform()
    platform.set_albion_path(albion_path)
    platform.set_server_type(server_type)
    platform.set_output_path(output_dir)
    
    # Run extraction process
    platform.run_extraction()

if __name__ == "__main__":
    run()
