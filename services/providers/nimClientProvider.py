from openai import ContentFilterFinishReasonError
from openai.types.realtime import RealtimeAudioConfigOutput
from asyncio import QueueEmpty
from DTO.llmConfig import LLMConfig
import requests
from openai import OpenAi
from interfaces.llmProvider import LLMProvider

#"z-ai/glm-5.3-flash",
class NIMClientProvier(LLMProvider):

    def __init__(self, sys_prompt, model, api_key, endpoint):

        self.client = OpenAi(api_key = api_key, base_url = endpoint)

        self.sys_prompt = sys_prompt

        self.model = model

    
    def chat(self, query, messages, config: LLMConfig):
        
        if messages == []:
            messages.append({"role": "system", "content": f"{self.sys_prompt}"})
        
        messages.append({"role":"user", "content": query})

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=config.temperature,
            top_p=config.top_p,
            max_tokens=config.max_tokens,
            stream=config.stream
        )

        messages.append({"role":"assistant", "content": completion.choices[0].message})

        return messages