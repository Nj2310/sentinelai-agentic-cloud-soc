import os

from anthropic import Anthropic

from src.agents.providers.base import LLMProvider


class ClaudeProvider(LLMProvider):
    """
    Optional Anthropic Claude provider for SentinelAI.

    Requires ANTHROPIC_API_KEY only when initialized.
    """

    def __init__(self, model_name: str = "claude-sonnet-4-5"):
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is required to use Claude."
            )

        self.model_name = model_name
        self.client = Anthropic(api_key=api_key)

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate a security analysis using Anthropic Claude.
        """
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=1024,
            temperature=0,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
        )

        return "".join(
            block.text
            for block in response.content
            if block.type == "text"
        ).strip()