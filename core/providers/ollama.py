import json
import httpx
import os
import ssl
from typing import AsyncGenerator, Optional
from core.exceptions import ProviderTimeout


class OllamaProvider:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = f"{base_url}/api/chat"
        self.model = "qwen2.5-coder:latest"  # Recommended for coding/structuring
        self.dev_mode = os.getenv("DEV_MODE", "False").lower() == "true"

        self.proxy = (
            os.getenv("HTTPS_PROXY")
            or os.getenv("HTTP_PROXY")
            or os.getenv("https_proxy")
            or os.getenv("http_proxy")
        )

    async def stream_chat(
        self, prompt: str, system_prompt: str
    ) -> AsyncGenerator[str, None]:
        """
        Local fallback streaming call to Ollama.
        """
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "stream": True,
            "options": {"temperature": 0.2},
        }

        try:
            verify_ssl = not self.dev_mode
            async with httpx.AsyncClient(
                timeout=60.0, verify=verify_ssl, proxy=self.proxy
            ) as client:
                async with client.stream(
                    "POST", self.base_url, json=payload
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        raise ProviderTimeout(
                            f"Ollama Error: {response.status_code} - {error_text.decode()}"
                        )

                    async for line in response.aiter_lines():
                        if not line:
                            continue

                        try:
                            data = json.loads(line)
                            chunk = data.get("message", {}).get("content", "")
                            if chunk:
                                yield chunk

                            if data.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue
        except ssl.SSLCertVerificationError as e:
            raise ProviderTimeout(
                f"Corporate Firewall Detected (SSL Error on Ollama): {str(e)}. Try setting DEV_MODE=True in .env."
            )
        except httpx.ConnectError as e:
            if "CERTIFICATE_VERIFY_FAILED" in str(e):
                raise ProviderTimeout(
                    f"Corporate Firewall Detected (SSL Error on Ollama): {str(e)}. Try setting DEV_MODE=True in .env."
                )
            raise ProviderTimeout(
                f"Ollama server not found or connection blocked: {str(e)}. Ensure Ollama is running."
            )
        except Exception as e:
            raise ProviderTimeout(f"Ollama connection failed: {str(e)}")
