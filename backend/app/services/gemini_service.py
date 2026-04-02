from google import genai
from google.genai import types
from app.core.config import settings
from app.core.exceptions import LLMError
from app.core.logger import logger

class GeminiService:
    def __init__(self):
        # Base model initialization
        self.model_name = settings.GEMINI_MODEL
        # New generic client initialization
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def generate_response(self, contents: list[dict], system_instruction: str) -> str:
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            raise LLMError(f"Failed to generate response: {e}")

    async def stream(self, contents: list[dict], system_instruction: str):
        try:
            response_stream = await self.client.aio.models.generate_content_stream(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
            async for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Gemini Streaming Error: {e}")
            raise LLMError(f"Failed to stream response: {e}")

gemini_service = GeminiService()
