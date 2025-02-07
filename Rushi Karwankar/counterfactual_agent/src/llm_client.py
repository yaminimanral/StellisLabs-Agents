import json
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .config import Config

class LLMClient:
    def __init__(self, api_url, logger):
        self.api_url = api_url
        self.logger = logger
        self.api_call_count = 0
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((json.JSONDecodeError, KeyError)),
    )
    def call_llm(self, prompt):
        if self.api_call_count >= Config.COST_THRESHOLD:
            raise Exception("Cost threshold exceeded")
            
        self.api_call_count += 1
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": "llama3.1:latest",
                    "prompt": prompt,
                    "stream": True,
                },
                stream=True,
            )
            response.raise_for_status()
            return response
        except Exception as e:
            self.logger.log(f"Error calling Ollama API: {e}", style="bold red")
            raise

    def validate_json(self, chunk):
        """Validate if the chunk is a valid JSON object."""
        try:
            chunk_data = json.loads(chunk.decode("utf-8"))
            if "response" not in chunk_data:
                raise KeyError("Missing 'response' key in JSON.")
            return chunk_data
        except (json.JSONDecodeError, KeyError) as e:
            self.log(f"Invalid JSON response: {e}", style="bold yellow")
            raise