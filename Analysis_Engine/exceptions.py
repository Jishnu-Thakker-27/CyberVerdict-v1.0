"""
CyberVerdict Custom Exceptions

This module defines the exception hierarchy for the CyberVerdict Deterministic Analysis Engine.
All custom exceptions inherit from the base class `AnalysisEngineError`.
"""

class AnalysisEngineError(Exception):
    """
    Base exception class for all errors in the CyberVerdict Analysis Engine.
    
    Attributes:
        message (str): User-friendly description of the error.
        stage (str): The stage of analysis where the error occurred.
        technical_details (str | None): Detailed technical or system error logs.
    """
    def __init__(self, message: str, stage: str = "initialization", technical_details: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.stage = stage
        self.technical_details = technical_details

    def __str__(self) -> str:
        base = f"[{self.stage.upper()}] {self.message}"
        if self.technical_details:
            base += f" (Details: {self.technical_details})"
        return base


class ValidationError(AnalysisEngineError):
    """
    Raised when the APK fails structural integrity or format validation.
    
    This includes checks such as file existence, extension, zip corruption,
    and missing mandatory files (AndroidManifest.xml, classes.dex).
    """
    def __init__(self, message: str, stage: str, technical_details: str | None = None) -> None:
        super().__init__(message, stage=stage, technical_details=technical_details)


class ParserError(AnalysisEngineError):
    """
    Raised when the APK parsing module fails to open or read the file contents.
    
    This includes file access errors, decompression issues, and issues reading binary XMLs.
    """
    def __init__(self, message: str, stage: str = "parsing", technical_details: str | None = None) -> None:
        super().__init__(message, stage=stage, technical_details=technical_details)


class HashGeneratorError(AnalysisEngineError):
    """
    Raised when hash generation fails.
    
    This includes issues reading the APK file or hashing raw bytes.
    """
    def __init__(self, message: str, stage: str = "hash_generation", technical_details: str | None = None) -> None:
        super().__init__(message, stage=stage, technical_details=technical_details)
