"""Custom exceptions for the Bedrock-Langfuse integration."""


class BedrockLangfuseError(Exception):
    """Base exception for Bedrock-Langfuse integration errors."""
    pass


class ModelNotAvailableError(BedrockLangfuseError):
    """Raised when a requested model is not available or accessible."""
    pass


class AuthenticationError(BedrockLangfuseError):
    """Raised when AWS or Langfuse authentication fails."""
    pass


class RateLimitError(BedrockLangfuseError):
    """Raised when rate limits are exceeded."""
    pass


class InvalidRequestError(BedrockLangfuseError):
    """Raised when the request is invalid or malformed."""
    pass


class ServiceUnavailableError(BedrockLangfuseError):
    """Raised when the AWS Bedrock service is unavailable."""
    pass
