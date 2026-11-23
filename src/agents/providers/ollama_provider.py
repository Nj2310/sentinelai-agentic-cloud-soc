from ollama import chat

from src.agents.providers.base import LLMProvider


class OllamaProvider(LLMProvider):
    """
    Local Ollama language model provider for SentinelAI.
    """

    def __init__(self, model_name: str = "qwen3:4b"):
        self.model_name = model_name

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate a response using a locally hosted Ollama model.
        """
        response = chat(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            think=False,
            options={"temperature": 0},
        )

        content = response.message.content or ""

        # Remove any remaining model thinking content.
        if "</think>" in content:
            content = content.split("</think>", 1)[1]

        return content.strip()