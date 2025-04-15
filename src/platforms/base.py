"""
Platform handling utilities for Noki Bin Dumpper.
Provides file system operations abstracted from the underlying OS.
"""
import os
import platform
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from ..enums import ServerType

class PlatformHandler:
    """
    Handler for platform-specific operations.
    
    This class manages file system operations and path resolution
    across different operating systems, providing a unified interface
    for the application.
    """
    
    def __init__(self):
        """Initialize the platform handler with platform-specific paths."""
        self.logger = logging.getLogger(__name__)
        
        # Define default installation paths for supported platforms
        self._default_paths = {
            'Windows': Path("C:/Program Files (x86)/AlbionOnline"),
            'Linux': Path.home().joinpath(".steam/steam/steamapps/common/AlbionOnline"),
            'Darwin': Path.home().joinpath("Library/Application Support/Steam/steamapps/common/AlbionOnline")
        }
    
    def get_default_path(self) -> Optional[Path]:
        """
        Get the default Albion Online installation path for the current platform.
        
        Returns:
            Path: Default installation path for this platform or None if not supported
        """
        system = platform.system()
        return self._default_paths.get(system)
    
    def find_game_data_path(self, albion_path: Path, server_type: int) -> Path:
        """
        Find the GameData directory path based on Albion installation path.
        
        Args:
            albion_path: Base installation path for Albion Online
            server_type: Server type (1 = Live, 2 = Test)
            
        Returns:
            Path: Path to the GameData directory
            
        Raises:
            ValueError: If paths are not defined
            FileNotFoundError: If GameData directory is not found
        """
        # Validate parameters
        if not albion_path:
            raise ValueError("Albion Online installation path not defined. Use set_albion_path() first.")
        
        if not server_type:
            raise ValueError("Server type not defined. Use set_server_type() first.")

        # Construct GameData path
        game_data_path = os.path.join(
            albion_path, 
            ServerType(server_type).folder_name, 
            "Albion-Online_Data", 
            "StreamingAssets", 
            "GameData"
        )

        # Validate path exists
        if not Path(game_data_path).exists():
            raise FileNotFoundError(f"GameData directory not found: {game_data_path}")
        
        return Path(game_data_path)
    
    def find_files(self, directory: Path, pattern: str = "*.bin") -> List[Path]:
        """
        Find files matching a pattern in a directory (recursively).
        
        Args:
            directory: Directory to search in
            pattern: Glob pattern to match files (default: *.bin)
            
        Returns:
            List[Path]: List of matching file paths
        """
        if not directory.exists():
            self.logger.warning(f"Directory not found: {directory}")
            return []
        
        # Find all files matching the pattern recursively
        files = list(directory.glob(f"**/{pattern}"))

        # Log results
        self.logger.info(f"Found {len(files)} files matching pattern '{pattern}' in {directory}")
        
        return files
    
    def get_relative_path(self, output_path: Path, file_path: Path, base_path: Path) -> Path:
        """
        Get the relative path while preserving the original directory structure.
        
        Creates a path that preserves the original structure but inside the output path.
        
        Args:
            output_path: Base output path
            file_path: Original file path
            base_path: Base path to calculate relative path from
            
        Returns:
            Path: New path with preserved structure inside output_path
        """
        try:
            # Get path relative to the base path
            relative = file_path.relative_to(base_path)
            
            # Create path starting with output_path while preserving structure
            result_path = output_path.joinpath(relative)
            
            return result_path
        except ValueError:
            # If relative path can't be calculated, use just the filename
            self.logger.warning(
                f"Can't get relative path for {file_path}, using only the file name in output directory"
            )
            return output_path.joinpath(file_path.name)
    
    def validate_paths(self, paths_to_check: Dict[str, Path]) -> Dict[str, bool]:
        """
        Validate that paths exist.
        
        Args:
            paths_to_check: Dictionary of {name: path} to validate
            
        Returns:
            Dict[str, bool]: Results of validation for each path
        """
        result = {}
        for name, path in paths_to_check.items():
            exists = path.exists()
            if not exists:
                self.logger.warning(f"Path '{name}' not found: {path}")
            result[name] = exists
        return result 