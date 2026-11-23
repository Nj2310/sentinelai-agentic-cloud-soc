from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Common interface for SentinelAI language model providers.

    Every provider must implement the generate() method.
    """

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate a response using the configured language model.

        Args:
            system_prompt: Security instructions for the model.
            user_prompt: Security evidence or investigation request.

        Returns:
            The model-generated response as a string.
        """
        pass