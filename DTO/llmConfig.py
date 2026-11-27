from dataclasses import dataclass

@dataclass
class LLMConfig:
    model: str
    provider: str
    api_key: str
    endpoint: str
    sys_prompt: str
    top_p: int = 1
    temperature: int = 0.5
    stream: bool = False
    max_tokens: int = 8192
