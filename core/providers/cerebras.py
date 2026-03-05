import os
import json
import httpx
import ssl
from typing import AsyncGenerator, Optional
from core.exceptions import ProviderTimeout
from dotenv import load_dotenv

load_dotenv()


class CerebrasProvider:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("CEREBRAS_API_KEY")
        self.base_url = "https://api.cerebras.ai/v1/chat/completions"
        self.model = "gpt-oss-120b"
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
        Async streaming call to Cerebras API.
        Optimized for 450+ tokens/sec.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "stream": True,
            "temperature": 0.2,
        }

        try:
            verify_ssl = not self.dev_mode
            async with httpx.AsyncClient(
                timeout=30.0, verify=verify_ssl, proxy=self.proxy
            ) as client:
                async with client.stream(
                    "POST", self.base_url, headers=headers, json=payload
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        raise ProviderTimeout(
                            f"Cerebras API Error: {response.status_code} - {error_text.decode()}"
                        )

                    async for line in response.aiter_lines():
                        if not line or line == "data: [DONE]":
                            continue

                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                chunk = data["choices"][0]["delta"].get("content", "")
                                if chunk:
                                    yield chunk
                            except (KeyError, json.JSONDecodeError):
                                continue
        except ssl.SSLCertVerificationError as e:
            raise ProviderTimeout(
                f"Corporate Firewall Detected (SSL Error on Cerebras): {str(e)}. Try setting DEV_MODE=True in .env."
            )
        except httpx.ConnectError as e:
            if "CERTIFICATE_VERIFY_FAILED" in str(e):
                raise ProviderTimeout(
                    f"Corporate Firewall Detected (SSL Error on Cerebras): {str(e)}. Try setting DEV_MODE=True in .env."
                )
            raise ProviderTimeout(
                f"Corporate Firewall Detected (Connection blocked on Cerebras): {str(e)}."
            )
        except httpx.ReadTimeout:
            raise ProviderTimeout("Cerebras API timed out during streaming.")
        except Exception as e:
            raise ProviderTimeout(f"Cerebras connection failed: {str(e)}")
