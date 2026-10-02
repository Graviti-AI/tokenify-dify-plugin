from dify_plugin import ModelProvider
from dify_plugin.errors.model import CredentialsValidateFailedError


class TokenifyProvider(ModelProvider):
    def validate_provider_credentials(self, credentials: dict) -> None:
        # Each model is validated when the user adds it.
        if not credentials or not credentials.get("api_key"):
            raise CredentialsValidateFailedError("API key is required")
