from abc import abstractmethod
from DTO.llmConfig import LLMConfig

class LLMProvider:

    @abstractmethod
    def chat(self, query, messages, config: LLMConfig):
        pass