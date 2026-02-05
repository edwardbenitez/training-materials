from pydantic import BaseModel, Field, computed_field
import os
from foundry_local import FoundryLocalManager


class ModelConfig(BaseModel):
    local: bool = True
    """Configuration for the language model used for info extraction."""
    alias: str = Field(
        default="phi-4-mini",
        description="The alias of the Foundry Local model to use for information extraction.",
    )
    temperature: float = 0.0

    @computed_field
    @property
    def model_name(self) -> str:
        """Get the model name based on the alias."""
        if self.local:
            manager = FoundryLocalManager(self.alias)
            return manager.get_model_info(self.alias).id
        return self.alias

    @computed_field
    @property
    def base_url(self) -> str:
        """Get the base URL for the model."""
        if self.local:
            manager = FoundryLocalManager(self.alias)
            return manager.endpoint
        return os.environ.get("OPENAI_API_BASE_URL", "")

    @computed_field
    @property
    def api_key(self) -> str:
        """Get the API key for the model."""
        if self.local:
            manager = FoundryLocalManager(self.alias)
            return manager.api_key
        ## TODO: if env var not set, use Microsoft identity token
        return os.environ.get("OPENAI_API_KEY", "")
