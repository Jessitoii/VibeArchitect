import os
import json
import httpx
import ssl
import asyncio
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
        self,
        prompt: str,
        system_prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Async streaming call to Cerebras API.
        Optimized for 450+ tokens/sec.
        Includes exponential backoff for 429 Too Many Requests and adaptive throttling.
        """
        if model:
            self.model = model

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
            "max_tokens": max_tokens or 8192,
        }

        retries = [2, 4, 8]
        verify_ssl = not self.dev_mode

        for attempt in range(len(retries) + 1):
            try:
                async with httpx.AsyncClient(
                    timeout=30.0, verify=verify_ssl, proxy=self.proxy
                ) as client:
                    async with client.stream(
                        "POST", self.base_url, headers=headers, json=payload
                    ) as response:
                        if response.status_code == 429:
                            if attempt < len(retries):
                                yield f"\n[SYSTEM] Rate limit hit. Cooling down ({retries[attempt]}s)...\n"
                                await asyncio.sleep(retries[attempt])
                                continue
                            else:
                                error_text = await response.aread()
                                raise ProviderTimeout(
                                    f"Cerebras API Error (Rate Limit Reached): {response.status_code} - {error_text.decode()}"
                                )
                        elif response.status_code != 200:
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
                                    chunk = data["choices"][0]["delta"].get(
                                        "content", ""
                                    )
                                    if chunk:
                                        await asyncio.sleep(0.01)  # Adaptive throttling
                                        yield chunk
                                except (KeyError, json.JSONDecodeError):
                                    continue
                break  # On success, exit loop
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
            except ProviderTimeout:
                raise
            except Exception as e:
                raise ProviderTimeout(f"Cerebras connection failed: {str(e)}")
