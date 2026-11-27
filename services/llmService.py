# from openai import OpenAI

# class LLMService:

#     def __init__(self, sys_prompt, model, api_key, endpoint):
#         self.sys_prompt = sys_prompt
#         self.model = model
        
#         self.endpoint = endpoint
#         self.api_key = api_key


#     def chat(self, query, stream=False):
#         headers = {
#             "Authorization": f"Bearer ${self.api_key}",
#             "Accept": "text/event-stream" if stream else "application/json",
#         }

#         payload = {
#             "messaes": [
#                 {
#                 "role": "user",
#                 "content": [
#                     {
#                     "type": "text",
#                     "text": "What is in this image?"
#                     },
#                     {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": "https://assets.ngc.nvidia.com/products/api-catalog/phi-3-5-vision/example1b.jpg"
#                     }
#                     }
#                 ]
#                 }
#             ],
#             "model": "minimaxai/minimax-m3.1-flash",
#             "max_tokens": 16384,
#             "seed": 0,
#             "stream": stream,
#             "temperature": 1,
#             "top_p": 0.95
#             }


