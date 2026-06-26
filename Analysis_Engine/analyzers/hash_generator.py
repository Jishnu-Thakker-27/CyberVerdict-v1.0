"""
Hash Generator Module

Computes deterministic hash signatures (SHA-256, SHA-1, MD5) and size metadata
for a target APK file. Use SHA-256 as the primary identifier.
"""

import hashlib
import logging
from pathlib import Path

from exceptions import HashGeneratorError

logger = logging.getLogger(__name__)

class HashGenerator:
    """
    Generates deterministic cryptographic hashes and metadata for files.
    
    This class handles efficient streaming file reading to compute hashes
    without loading the entire file into memory.
    """
    
    def __init__(self, chunk_size: int = 65536) -> None:
        """
        Initializes the HashGenerator.
        
        Args:
            chunk_size (int): Size in bytes for streaming file reads. Defaults to 64KB.
        """
        self.chunk_size = chunk_size

    def generate(self, apk_path: str | Path) -> dict:
        """
        Computes hashes and size of the APK file.
        
        Args:
            apk_path (str | Path): Path to the target APK file.
            
        Returns:
            dict: Dictionary containing sha256, sha1, md5, and size_bytes.
            
        Raises:
            HashGeneratorError: If the file is inaccessible or a hashing error occurs.
        """
        path = Path(apk_path)
        logger.info("Generating hashes for APK: %s", path.name)
        
        if not path.exists():
            raise HashGeneratorError(
                message=f"File not found: '{path}'",
                stage="hash_generation",
                technical_details="FileNotFoundError: Path does not exist."
            )
        if not path.is_file():
            raise HashGeneratorError(
                message=f"Provided path is not a file: '{path}'",
                stage="hash_generation",
                technical_details="IsADirectoryError: Path exists but refers to a directory."
            )

        # Initialize hash objects
        sha256_hash = hashlib.sha256()
        sha1_hash = hashlib.sha1()
        md5_hash = hashlib.md5()
        size_bytes = 0

        try:
            with open(path, "rb") as f:
                while chunk := f.read(self.chunk_size):
                    sha256_hash.update(chunk)
                    sha1_hash.update(chunk)
                    md5_hash.update(chunk)
                    size_bytes += len(chunk)
        except Exception as exc:
            logger.error("Error reading file '%s' for hash generation: %s", path.name, str(exc), exc_info=True)
            raise HashGeneratorError(
                message=f"Failed to read file for hash computation: {path.name}",
                stage="hash_generation",
                technical_details=f"OSError/IOException: {str(exc)}"
            )

        hashes = {
            "sha256": sha256_hash.hexdigest(),
            "sha1": sha1_hash.hexdigest(),
            "md5": md5_hash.hexdigest(),
            "size_bytes": size_bytes
        }
        
        logger.info("Successfully computed hashes for %s (SHA-256: %s)", path.name, hashes["sha256"])
        return hashes
