import os
import json
from pathlib import Path
from core.schema import Manifest, InstructionalBrain


class InstructionalBrainGenerator:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.agent_dir = self.project_path / ".agent"

        # Subdirectories
        self.rules_dir = self.agent_dir / "rules"
        self.workflows_dir = self.agent_dir / "workflows"
        self.docs_dir = self.agent_dir / "docs"
        self.skills_dir = self.agent_dir / "skills"

    def generate(self, manifest: Manifest):
        """Flushes the manifest's instructional_brain into physical files."""
        brain = manifest.instructional_brain
        if not brain:
            print(
                "\n[INFO] No Instructional Brain found in Manifest. Skipping .agent generation."
            )
            return

        self._scaffold_directories()

        # 1. Master Index (GEMINI.md)
        if brain.gemini_md:
            self._write_file_safe(self.agent_dir / "GEMINI.md", brain.gemini_md)

        # 2. Metadata Injection (metadata.json)
        if brain.metadata_json:
            self._write_file_safe(
                self.agent_dir / "metadata.json",
                json.dumps(brain.metadata_json, indent=2),
            )

        # 3. Write Rules (Including Auditor generated rules)
        for rule in brain.rules:
            self._write_file_safe(self.rules_dir / rule.filename, rule.content)

        # 4. Write Workflows (Includes Verification Hooks)
        for wf in brain.workflows:
            content = wf.content
            if wf.success_criteria:
                content += "\n\n## Verification Hooks (Success Criteria)\n"
                for criteria in wf.success_criteria:
                    content += f"- [ ] {criteria}\n"
            self._write_file_safe(self.workflows_dir / wf.filename, content)

        # 5. Write Docs
        for doc in brain.docs:
            self._write_file_safe(self.docs_dir / doc.filename, doc.content)

        # 6. Write Skills
        for skill in brain.skills:
            self._write_file_safe(self.skills_dir / skill.filename, skill.content)

        print(
            f"\n[SUCCESS] Instructional Brain generated successfully at {self.agent_dir}"
        )

    def _scaffold_directories(self):
        """Creates the required directories if they don't exist."""
        self.agent_dir.mkdir(parents=True, exist_ok=True)
        self.rules_dir.mkdir(exist_ok=True)
        self.workflows_dir.mkdir(exist_ok=True)
        self.docs_dir.mkdir(exist_ok=True)
        self.skills_dir.mkdir(exist_ok=True)

    def _write_file_safe(self, filepath: Path, content: str):
        """
        Persistence Policy: `overwrite=False` / Smart Merge approach.
        If the file already exists, it skips overwriting it to protect manual user edits.
        """
        if filepath.exists():
            print(
                f"[INFO] File {filepath.name} already exists. Skipping to preserve manual changes."
            )
            return

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
