"""
Core platform module for Noki Bin Dumpper.
Handles platform detection, file operations, and data extraction.
"""
import platform
import xmltodict
import json
from typing import Optional, List
from pathlib import Path
from tqdm import tqdm

from .Config import Config, Terminal, logger
from ..platforms import PlatformHandler
from ..enums import ServerType
from ..utils import BinaryDecryptor, Converter


class Platform:
    """
    Core platform management class.
    
    Responsible for coordinating platform-specific operations, 
    file processing, and the extraction workflow.
    
    Implements the Singleton pattern to ensure only one instance exists.
    """
    
    _instance: Optional['Platform'] = None
    
    def __new__(cls) -> 'Platform':
        """
        Singleton implementation to ensure only one Platform instance exists.
        
        Returns:
            Platform: The single Platform instance
        """
        if cls._instance is None:
            cls._instance = super(Platform, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialize the Platform instance with default values."""
        self._system = platform.system()
        self._handler = PlatformHandler()
        self._server_type = ServerType.LIVE
        self._output_path = Config.OUTPUT_DIR
        self._albion_path = None
        self._game_data_path = None
        
        # Initialize processing tools
        self._decryptor = BinaryDecryptor()
        self._converter = Converter()
        
    @property
    def system(self) -> str:
        """Get the current operating system name."""
        return self._system
    
    @property
    def handler(self) -> PlatformHandler:
        """Get the platform handler instance."""
        return self._handler
    
    def is_windows(self) -> bool:
        """Check if the current platform is Windows."""
        return self._system == 'Windows'
    
    def is_macos(self) -> bool:
        """Check if the current platform is macOS."""
        return self._system == 'Darwin'
    
    def is_linux(self) -> bool:
        """Check if the current platform is Linux."""
        return self._system == 'Linux'
    
    def set_albion_path(self, path: Path) -> None:
        """
        Set the Albion Online installation path.
        
        Args:
            path: Path to the Albion Online installation
        """
        self._albion_path = path
        # Reset GameData path when Albion path changes
        self._game_data_path = None
        logger.info(f"Albion Online path set: {path}")
    
    def set_server_type(self, server_type: ServerType) -> None:
        """
        Set the server type to extract data from.
        
        Args:
            server_type: Server type (LIVE or TEST)
        """
        self._server_type = server_type
        # Reset GameData path when server type changes
        self._game_data_path = None
        logger.info(f"Server: {server_type.name}")
    
    def set_output_path(self, output_path: Path) -> None:
        """
        Set the output directory path.
        
        Args:
            output_path: Path where extracted files will be saved
        """
        self._output_path = output_path
        logger.info(f"Output path set: {output_path}")

    def ensure_output_file_exists(self, file_path: Path) -> Path:
        """
        Ensure a file exists, creating it if necessary.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Path: The same file path
        """
        if not file_path.exists():
            file_path.touch()
        return file_path

    def ensure_directory_exists(self, directory: Path) -> Path:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            directory: Path to the directory
            
        Returns:
            Path: The same directory path
        """
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
        return directory
    
    def get_game_data_path(self) -> Path:
        """
        Get the path to the GameData directory for the selected server.
        Uses caching to avoid repeated lookups.
        
        Returns:
            Path: Path to the GameData directory
            
        Raises:
            ValueError: If Albion path is not defined
        """
        # Check if Albion path is defined
        if not self._albion_path:
            raise ValueError("Albion Online installation path not defined. Use set_albion_path() first.")
        
        # Use cached value if available
        if self._game_data_path is None:
            # Delegate lookup to the platform handler
            self._game_data_path = self._handler.find_game_data_path(
                self._albion_path, 
                self._server_type.value
            )
            
        return self._game_data_path
    
    def find_bin_files(self) -> List[Path]:
        """
        Find .bin files in the game data path.
        
        Returns:
            List[Path]: List of .bin files found
        """
        # Get the GameData path
        game_data_path = self.get_game_data_path()

        # Check if GameData directory exists
        if not game_data_path.exists():
            logger.error(f"GameData directory not found: {game_data_path}")
            return []
        
        # Use the handler to find .bin files
        return self._handler.find_files(game_data_path, "*.bin")
    
    def process_bin_files(self) -> None:
        """
        Process .bin files found in the game data.
        
        This method:
        1. Finds all .bin files
        2. Decrypts each file
        3. Saves the content as XML
        4. Converts XML to JSON
        5. Saves both formats maintaining the original directory structure
        """
        # Get the GameData path
        game_data_path = self.get_game_data_path()
        
        # Find .bin files
        bin_files = self.find_bin_files()
        
        if not bin_files:
            # Display warning if no .bin files found
            logger.info(f"[yellow]====================================================[/yellow]")
            logger.warning("No .bin files found to process")
            logger.info(f"[yellow]====================================================[/yellow]")
            return
        
        # Create output directories
        xml_output_path = self._output_path.joinpath("xml")
        json_output_path = self._output_path.joinpath("json")
        self.ensure_directory_exists(xml_output_path)
        self.ensure_directory_exists(json_output_path)

        # Process all .bin files
        for bin_file in tqdm(bin_files, desc="Processing files"):
            try:
                # Get relative paths preserving directory structure
                xml_relative_path = self._handler.get_relative_path(xml_output_path, bin_file, game_data_path)
                json_relative_path = self._handler.get_relative_path(json_output_path, bin_file, game_data_path)

                # Change extensions
                xml_relative_path = xml_relative_path.with_suffix('.xml')
                json_relative_path = json_relative_path.with_suffix('.json')

                # Ensure output directories exist
                self.ensure_directory_exists(xml_relative_path.parent)
                self.ensure_directory_exists(json_relative_path.parent)
                
                # Decrypt .bin file content
                content = self._decryptor.decrypt_bin(bin_file.read_bytes())
                
                # Convert bytes to string with UTF-8 BOM handling
                content_str = content.decode('utf-8-sig')
                
                # Save decrypted content as XML
                with open(xml_relative_path, 'w', encoding='utf-8') as f:
                    f.write(content_str)

                # Convert to JSON using the converter (handles special cases)
                json_content = self._converter.convert_to_json(content_str, bin_file)

                # Save JSON content
                with open(json_relative_path, 'w', encoding='utf-8') as f:
                    json.dump(json_content, f, indent=4, ensure_ascii=False)
                
            except Exception as e:
                logger.error(f"Can't process {bin_file}: {e}")
    
    def run_extraction(self) -> None:
        """
        Run the complete extraction process.
        
        This is the main method that coordinates the entire process:
        1. Validates paths and settings
        2. Processes .bin files to XML and JSON
        
        Raises:
            ValueError: If required paths are not set
            Exception: For other errors during extraction
        """
        try:
            logger.info("Starting extraction process...")
            
            # Validate Albion path
            if not self._albion_path:
                raise ValueError("Albion Online installation path not defined. Use set_albion_path() first.")
            
            # Validate server type
            if not self._server_type:
                raise ValueError("Server type not defined. Use set_server_type() first.")
            
            # Process files
            self.process_bin_files()

            logger.info("Extraction process completed successfully!")
            
        except Exception as e:
            logger.error(f"Error during extraction process: {e}")
            raise