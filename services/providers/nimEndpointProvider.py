from DTO.llmConfig import LLMConfig
import requests
from interfaces.llmProvider import LLMProvider
#"minimaxai/minimax-m3.1-flash",
class NIMEndpointProvider(LLMProvider):

    def __init__(self, sys_prompt, model, api_key, endpoint):
        self.sys_prompt = sys_prompt
        self.model = model
        
        self.endpoint = endpoint
        self.api_key = api_key


    #returns whole response for now. i think this sholud be changed to standard LLMResponse DTO later.
    def chat(self, query, messages, config: LLMConfig):
        headers = {
            "Authorization": f"Bearer ${self.api_key}",
            "Accept": "text/event-stream" if config.stream else "application/json",
        }


        messages.append({
                "role": "user",
                "content": query
                })

        payload = {
            "messages": messages,
            "model": config.model,
            "max_tokens": config.max_tokens,
            "seed": 0,
            "stream": config.stream,
            "temperature": config.temperature,
            "top_p": config.top_p
            }

        response = requests.post(config.endpoint, headers=headers, json=payload, stream=config.stream)

        if config.stream:
            for line in response.iter_lines():
                if line:
                    print(line.decode("utf-8"))
        else:
            print(response.json())

        return response


