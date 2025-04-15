"""
Utility for converting between different data formats.
Handles special cases like profanity files that aren't actually valid XML.
"""
import os
import json
import logging
import xmltodict
from pathlib import Path
from typing import Dict, Any, List, Union

class Converter:
    """
    Converts data between different formats (XML, JSON, etc.)
    Includes special handling for non-standard files like profanity lists.
    """
    
    def __init__(self):
        """Initialize the converter with a logger."""
        self.logger = logging.getLogger(__name__)
    
    def convert_to_json(self, content: str, file_path: Path) -> Dict[str, Any]:
        """
        Convert content to JSON, with special handling for certain file types.
        
        Args:
            content: String content to convert
            file_path: Original file path (used to detect special file types)
            
        Returns:
            Dict: JSON representation of the content
        """
        # Check if this is a profanity file (which isn't actually XML)
        if self._is_profanity_file(file_path):
            return self._process_profanity_file(content)
        
        # Otherwise, try to parse as XML
        try:
            return xmltodict.parse(content)
        except Exception as e:
            self.logger.error(f"Failed to convert {file_path} to JSON: {e}")
            # Return empty dict to prevent further errors
            return {"error": str(e), "original_content": content}
    
    def _is_profanity_file(self, file_path: Path) -> bool:
        """
        Check if the file is a profanity file based on its name.
        
        Args:
            file_path: Path to check
            
        Returns:
            bool: True if it's a profanity file
        """
        filename = file_path.name.lower()
        return filename.startswith("profanity_") and (
            filename.endswith(".xml") or filename.endswith(".bin")
        )
    
    def _process_profanity_file(self, content: str) -> Dict[str, Dict[str, Union[List[str], int]]]:
        """
        Process a profanity file as a simple list of words.
        
        Args:
            content: Raw file content
            
        Returns:
            Dict: JSON representation of the profanity list
        """
        # Split by lines and filter out empty lines
        words = [word.strip() for word in content.splitlines() if word.strip()]
        
        # Create a JSON structure
        return {
            "profanity_list": {
                "words": words,
                "count": len(words)
            }
        } 