"""
APK Parser Module

Serves as a lightweight loader and accessor for the APK's zip structure and files.
Exposes only raw, uninterpreted Python types (lists, dicts, bytes) to downstream analyzers
to keep coupling low and prevent library lock-in.
"""

import logging
from pathlib import Path
import zipfile

from exceptions import ParserError

logger = logging.getLogger(__name__)

class APKParser:
    """
    A lightweight accessor for APK archive structures and binary contents.
    
    This parser does not decode or interpret internal artifacts (such as manifest XMLs
    or DEX bytecodes) and exposes only raw, plain Python types to avoid high coupling.
    """

    def __init__(self, apk_path: str | Path) -> None:
        """
        Initializes the APKParser and checks archive validity.
        
        Args:
            apk_path (str | Path): Path to the target APK file.
            
        Raises:
            ParserError: If the file cannot be opened or is not a valid ZIP.
        """
        self.apk_path = Path(apk_path)
        logger.info("Initializing APKParser for %s", self.apk_path.name)
        
        if not self.apk_path.exists():
            raise ParserError(
                message=f"APK file not found: '{self.apk_path}'",
                stage="parsing",
                technical_details="FileNotFoundError: Path does not exist."
            )
            
        if not zipfile.is_zipfile(self.apk_path):
            raise ParserError(
                message="Target file is not a valid ZIP archive",
                stage="parsing",
                technical_details="InvalidZipError: zipfile.is_zipfile returned False."
            )

    def list_files(self) -> list[str]:
        """
        Lists all file entries inside the APK.
        
        Returns:
            list[str]: Sorted list of internal file paths.
            
        Raises:
            ParserError: If reading the ZIP contents fails.
        """
        logger.debug("Listing file entries inside APK")
        try:
            with zipfile.ZipFile(self.apk_path, "r") as zfile:
                # Filter out entries that represent directories
                files = [
                    info.filename for info in zfile.infolist()
                    if not info.is_dir()
                ]
                return sorted(files)
        except Exception as exc:
            logger.error("Failed to list files inside APK: %s", str(exc), exc_info=True)
            raise ParserError(
                message="Failed to list files inside APK",
                stage="parsing",
                technical_details=f"ZipAccessError: {str(exc)}"
            )

    def list_directories(self) -> list[str]:
        """
        Lists all directory entries inside the APK.
        
        Returns:
            list[str]: Sorted list of internal directory paths.
            
        Raises:
            ParserError: If reading the ZIP contents fails.
        """
        logger.debug("Listing directory entries inside APK")
        try:
            with zipfile.ZipFile(self.apk_path, "r") as zfile:
                # Get explicit directories
                directories = {
                    info.filename for info in zfile.infolist()
                    if info.is_dir()
                }
                
                # Infer directories from file paths as well (in case there are no explicit directory entries)
                for info in zfile.infolist():
                    if not info.is_dir():
                        parts = Path(info.filename).parts
                        if len(parts) > 1:
                            # Reconstruct directory prefixes
                            for i in range(1, len(parts)):
                                dir_path = "/".join(parts[:i]) + "/"
                                directories.add(dir_path)
                                
                return sorted(list(directories))
        except Exception as exc:
            logger.error("Failed to list directories inside APK: %s", str(exc), exc_info=True)
            raise ParserError(
                message="Failed to list directories inside APK",
                stage="parsing",
                technical_details=f"ZipAccessError: {str(exc)}"
            )

    def list_dex_files(self) -> list[str]:
        """
        Lists all DEX executable files inside the APK.
        
        Returns:
            list[str]: List of internal paths to DEX files (e.g. ['classes.dex', 'classes2.dex']).
            
        Raises:
            ParserError: If listing files fails.
        """
        logger.info("Enumerate DEX files inside APK")
        files = self.list_files()
        dex_files = [
            f for f in files
            if f.endswith(".dex") and (f == "classes.dex" or (f.startswith("classes") and f.endswith(".dex")))
        ]
        return sorted(dex_files)

    def read_file_bytes(self, file_path: str) -> bytes:
        """
        Reads the raw content of an internal file.
        
        Args:
            file_path (str): The internal path of the target file.
            
        Returns:
            bytes: The raw byte array of the file.
            
        Raises:
            ParserError: If the file does not exist inside the APK or reading fails.
        """
        logger.info("Reading file bytes for: %s", file_path)
        try:
            with zipfile.ZipFile(self.apk_path, "r") as zfile:
                # We check first if the file exists in the namelist
                if file_path not in zfile.namelist():
                    raise ParserError(
                        message=f"File '{file_path}' not found inside the APK archive.",
                        stage="parsing",
                        technical_details="FileNotFoundError: Path is not in the ZIP archive list."
                    )
                return zfile.read(file_path)
        except ParserError:
            raise
        except Exception as exc:
            logger.error("Failed to read file '%s' bytes: %s", file_path, str(exc), exc_info=True)
            raise ParserError(
                message=f"Failed to read file bytes from archive: {file_path}",
                stage="parsing",
                technical_details=f"ZipReadError: {str(exc)}"
            )

    def get_raw_manifest_bytes(self) -> bytes:
        """
        Retrieves the raw bytes of AndroidManifest.xml from the APK root.
        
        Note: The returned bytes represent the binary XML format stored in the APK.
              This method does not parse or decompress it.
              
        Returns:
            bytes: The raw binary XML bytes of AndroidManifest.xml.
            
        Raises:
            ParserError: If AndroidManifest.xml is missing or reading fails.
        """
        logger.info("Extracting raw AndroidManifest.xml binary bytes")
        return self.read_file_bytes("AndroidManifest.xml")
