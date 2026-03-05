from core.agents.base import BaseAgent
from core.schema import Manifest


class EngineerAgent(BaseAgent):
    def __init__(self, manifest: Manifest):
        super().__init__("Engineer", manifest)
        self.system_prompt = """
        You are 'The System Engineer'.
        Your goal is to define API routes and database schemas based on the UI Map.
        
        OUTPUT FORMAT:
        You must output valid JSON matching the 'TechSpecs' model:
        {
            "api_routes": [
                {"id": "X_ID", "path": "/api/v1/...", "method": "GET", "request": {...}, "response": {...}}
            ],
            "database_schema": {"tables": [...]},
            "external_integrations": ["list of external services"]
        }
        
        RULES:
        1. Strict Typing. Define API responses with exact fields.
        2. Consistency. If the UI Architect planned a component with ID 'USER_CREDITS', you MUST provide an endpoint with ID 'USER_CREDITS'.
        3. Performance. Design for high-speed agentic execution.
        """

    def get_prompt(self, vibe: str) -> str:
        ui_map = (
            self.manifest.ui_map.model_dump_json(indent=2)
            if self.manifest.ui_map
            else "{} "
        )
        return f"UI Map: {ui_map}\n\nDesign the API routes and database schema."
