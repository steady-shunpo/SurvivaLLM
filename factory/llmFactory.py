from DTO.llmConfig import LLMConfig
from services.providers.nimEndpointProvider import NIMEndpointProvider
from services.providers.nimClientProvider import NIMClientProvier

class LLMFactory:

    @staticmethod
    def create_llm_object(config: LLMConfig):
        if config.provider == "NIMClientProvider":
            return NIMClientProvier(config.sys_prompt, config.model, config.api_key, config.endpoint)

        elif config.provider == "NIMEndpointProvider":
            return NIMEndpointProvider(config.sys_prompt, config.model, config.api_key, config.endpoint)     