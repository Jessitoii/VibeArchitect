from typing import AsyncGenerator
import json
import asyncio


class MockProvider:
    def __init__(self):
        self.primary_name = "mock"

    async def stream_chat(
        self, prompt: str, system_prompt: str
    ) -> AsyncGenerator[str, None]:
        """
        Emergency Mock Provider for Offline/Firewall block scenarios.
        Returns pre-defined dummy JSON structures so the orchestrator state machine can proceed
        with UI and pipeline testing when completely isolated.
        """

        system_prompt_lower = system_prompt.lower()
        prompt_lower = prompt.lower()

        if "visionary" in system_prompt_lower:
            output = {
                "features": ["Emergency Mock Feature 1", "Offline Development Mode"],
                "tech_stack": {
                    "frontend": "React",
                    "backend": "Python/FastAPI",
                    "database": "SQLite",
                },
                "constraints": ["Mock Environment", "No Live LLM Connection Allowed"],
                "high_level_goals": [
                    "Test Orchestrator State Machine",
                    "Bypass Corporate Firewall",
                ],
            }
        elif "architect" in system_prompt_lower or "ui map" in prompt_lower:
            output = {
                "screens": [
                    {
                        "name": "Mock Emergency Dashboard",
                        "components": [
                            {
                                "name": "MockConnectionStatus",
                                "description": "Displays offline mode",
                                "logic": "Loads status locally",
                                "data_source_id": "MOCK_STATUS_API",
                            }
                        ],
                        "user_journey": "User opens dashboard and sees mock items because the firewall blocked everything.",
                    }
                ],
                "theme": {"primary": "#ff0000", "secondary": "#000000"},
            }
        elif "engineer" in system_prompt_lower or "api routes" in prompt_lower:
            output = {
                "api_routes": [
                    {
                        "id": "MOCK_STATUS_API",
                        "path": "/api/v1/mock-status",
                        "method": "GET",
                        "request": {},
                        "response": {
                            "status": "offline_mode",
                            "items": ["array of mock data"],
                        },
                    }
                ],
                "database_schema": {
                    "tables": [{"name": "mock_status", "columns": ["id", "status"]}]
                },
                "external_integrations": ["Mock API"],
            }
        elif "antigravity expert" in system_prompt_lower:
            output = {
                "gemini_md": "# Project Vision\n\nThis is a mocked blueprint document.",
                "context_md": "Mock context description.",
                "metadata_json": {"version": "1.0", "mock": True},
                "rules": [
                    {
                        "filename": "offline_rule.md",
                        "content": "Always handle offline gracefully.",
                        "description": "Offline handling",
                    }
                ],
                "workflows": [
                    {
                        "filename": "build_mock.md",
                        "content": "1. Build mock.",
                        "success_criteria": ["Mock built"],
                    }
                ],
                "docs": [
                    {
                        "filename": "api_mock.md",
                        "content": "# API Mock\nMock API endpoints.",
                    }
                ],
                "skills": [
                    {
                        "filename": "mock_skill.py",
                        "content": "def mock_run():\n    return 'Mock executed in offline mode'",
                    }
                ],
            }
        elif "auditor" in system_prompt_lower:
            output = {
                "approved": True,
                "audit_log": [
                    {
                        "severity": "info",
                        "message": "Mock audit passed successfully during offline mode simulation.",
                        "location": "mock_layer",
                        "check_id": "MOCK_AUDIT_OK",
                    }
                ],
            }
        else:
            output = {"status": "Mock fallback general success"}

        # Simulate streaming latency
        json_str = json.dumps(output, indent=2)

        chunk_size = 20
        # Yield 'thinking' thought process explicitly if possible, or just raw tokens
        for i in range(0, len(json_str), chunk_size):
            await asyncio.sleep(0.01)
            yield json_str[i : i + chunk_size]
