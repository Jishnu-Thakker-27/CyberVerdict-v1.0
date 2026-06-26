"""
APK Validator Module

Validates the structural and format integrity of a target APK file.
Performs checks for file existence, extension, ZIP archive validity,
and presence of mandatory internal files (AndroidManifest.xml, classes.dex).
"""

from datetime import datetime
import logging
from pathlib import Path
import zipfile

from exceptions import ValidationError

logger = logging.getLogger(__name__)

class APKValidator:
    """
    Validates structural integrity of an APK file.
    
    This validator is deterministic and does not perform any static analysis,
    permission extraction, or security checks.
    """
    
    def __init__(self) -> None:
        """Initializes the APKValidator."""
        pass

    def validate(self, apk_path: str | Path) -> dict:
        """
        Validates the structure of the target APK file.
        
        Args:
            apk_path (str | Path): The filesystem path to the APK file.
            
        Returns:
            dict: The validation result in a standardized format.
        """
        path = Path(apk_path)
        # Use datetime.now().isoformat() or utcnow if required. datetime.now(timezone.utc) is best in modern python.
        timestamp = datetime.now().astimezone().isoformat()
        logger.info("Starting APK validation for %s", path.name)
        
        try:
            self._check_file_exists(path)
            self._check_extension(path)
            self._check_zip_integrity(path)
            self._check_manifest_existence(path)
            self._check_dex_existence(path)
            
            logger.info("APK validation completed successfully for %s", path.name)
            return {
                "success": True,
                "validator": "APKValidator",
                "stage": "completed",
                "timestamp": timestamp,
                "reason": None,
                "technical_details": None
            }
            
        except ValidationError as val_err:
            logger.warning(
                "APK validation failed at stage '%s': %s", 
                val_err.stage, val_err.message
            )
            return {
                "success": False,
                "validator": "APKValidator",
                "stage": val_err.stage,
                "timestamp": timestamp,
                "reason": val_err.message,
                "technical_details": val_err.technical_details
            }
        except Exception as exc:
            logger.error("Unexpected error during APK validation: %s", str(exc), exc_info=True)
            return {
                "success": False,
                "validator": "APKValidator",
                "stage": "unexpected_error",
                "timestamp": timestamp,
                "reason": "An unexpected error occurred during validation",
                "technical_details": str(exc)
            }

    def _check_file_exists(self, path: Path) -> None:
        """Checks if the file exists and is a file (not a directory)."""
        stage = "file_existence_check"
        if not path.exists():
            raise ValidationError(
                message=f"APK file not found: '{path}'",
                stage=stage,
                technical_details="FileNotFoundError: The file path does not reference an existing entity."
            )
        if not path.is_file():
            raise ValidationError(
                message=f"Provided path is not a file: '{path}'",
                stage=stage,
                technical_details="IsADirectoryError: Path exists but refers to a directory."
            )

    def _check_extension(self, path: Path) -> None:
        """Checks if the file has the correct extension (.apk)."""
        stage = "extension_check"
        if path.suffix.lower() != ".apk":
            raise ValidationError(
                message=f"Invalid file extension: '{path.suffix}'",
                stage=stage,
                technical_details="ExtensionMismatchError: File does not end with the mandatory '.apk' suffix."
            )

    def _check_zip_integrity(self, path: Path) -> None:
        """Checks if the file is a valid ZIP archive."""
        stage = "zip_integrity_check"
        if not zipfile.is_zipfile(path):
            raise ValidationError(
                message="File is not a valid ZIP archive",
                stage=stage,
                technical_details="ZipError: zipfile.is_zipfile returned False."
            )
        try:
            with zipfile.ZipFile(path, "r") as zfile:
                # Testzip returns the first corrupt file name, or None if no errors are found.
                corruption = zfile.testzip()
                if corruption is not None:
                    raise ValidationError(
                        message=f"ZIP archive is corrupted at file: {corruption}",
                        stage=stage,
                        technical_details=f"ZipCorruptionError: testzip() returned bad file: {corruption}"
                    )
        except zipfile.BadZipFile as bad_zip_err:
            raise ValidationError(
                message="ZIP archive structure is corrupted or invalid",
                stage=stage,
                technical_details=f"BadZipFile: {str(bad_zip_err)}"
            )

    def _check_manifest_existence(self, path: Path) -> None:
        """Checks if AndroidManifest.xml exists inside the APK archive."""
        stage = "manifest_existence_check"
        try:
            with zipfile.ZipFile(path, "r") as zfile:
                namelist = zfile.namelist()
                if "AndroidManifest.xml" not in namelist:
                    raise ValidationError(
                        message="Mandatory AndroidManifest.xml file is missing from the APK root.",
                        stage=stage,
                        technical_details="MissingManifestError: AndroidManifest.xml was not found in the ZIP namelist."
                    )
        except ValidationError:
            raise
        except Exception as exc:
            raise ValidationError(
                message="Failed to read ZIP contents to check for manifest",
                stage=stage,
                technical_details=f"ZipAccessError: {str(exc)}"
            )

    def _check_dex_existence(self, path: Path) -> None:
        """Checks if at least one classes.dex file exists inside the APK archive."""
        stage = "dex_existence_check"
        try:
            with zipfile.ZipFile(path, "r") as zfile:
                namelist = zfile.namelist()
                # Android apps require classes.dex to run bytecode.
                has_dex = any(name == "classes.dex" or (name.startswith("classes") and name.endswith(".dex")) for name in namelist)
                if not has_dex:
                    raise ValidationError(
                        message="Mandatory classes.dex file is missing from the APK.",
                        stage=stage,
                        technical_details="MissingDexError: No DEX files (e.g. classes.dex) were found in the ZIP namelist."
                    )
        except ValidationError:
            raise
        except Exception as exc:
            raise ValidationError(
                message="Failed to read ZIP contents to check for DEX files",
                stage=stage,
                technical_details=f"ZipAccessError: {str(exc)}"
            )