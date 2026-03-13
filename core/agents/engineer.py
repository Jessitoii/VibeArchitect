from core.agents.base import BaseAgent
from core.schema import Manifest


class EngineerAgent(BaseAgent):
    def __init__(self, manifest: Manifest):
        super().__init__("Engineer", manifest)
        self.system_prompt = """
You are 'The System Engineer'.
Your goal is to define API routes and database schemas based on the UI Map.

OUTPUT FORMAT — respond with valid JSON only, no markdown:
{
    "api_routes": [
        {
            "id": "GET_USER_PROFILE",
            "path": "/api/v1/users/{id}",
            "method": "GET",
            "request": {"params": {"id": "string"}},
            "response": {"id": "string", "name": "string"}
        }
    ],
    "database_schema": {"tables": []},
    "external_integrations": []
}

RULES:
1. Every api_route MUST have a unique "id" in SCREAMING_SNAKE_CASE. No exceptions.
2. Every UI component with a data_source_id MUST have a matching api_route id.
3. Strict types — no "any", no missing required fields.
4. Output raw JSON only — no backticks, no explanation text.
"""

    def get_prompt(self, vibe: str) -> str:
        ui_map = (
            self.manifest.ui_map.model_dump_json(indent=2)
            if self.manifest.ui_map
            else "{} "
        )
        return f"UI Map: {ui_map}\n\nDesign the API routes and database schema."
