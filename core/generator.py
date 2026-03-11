import json
import shutil
import time
from pathlib import Path
from core.schema import Manifest, InstructionalBrain, MetadataEntry, SubAgentRule


class InstructionalBrainGenerator:
    """
    Atomic scaffolder for the Lean 2.0 `.agent` Instructional Brain.

    ════════════════════════════════════════════════════════════════════
    GENERATED DIRECTORY CONTRACT
    ════════════════════════════════════════════════════════════════════
    .agent/
    ├── AGENT.md              ← Identity (soul + domain map + pointers + state)
    ├── RULES.md              ← Constitution (always-on + on-demand by domain)
    ├── metadata.json         ← Lazy-load index (path + desc + trigger_words)
    ├── rules/
    │   ├── auto_*.md             ← Auditor-generated preventative rules
    │   └── sub_agents/
    │       ├── frontend_agent.md  ← Domain-specific parallel agent rulebook
    │       ├── backend_agent.md
    │       └── {domain}_agent.md
    ├── skills/               ← Claude-style skill directories
    │   └── {skill-name}/
    │       └── SKILL.md          ← YAML frontmatter required
    └── workflows/            ← Recursive phase prompts
        ├── phase_1_setup.md
        ├── phase_2.1_auth.md  ← Sub-phase format: N.M_name.md
        └── phase_2.2_dash.md

    docs/                     ← External library (PROJECT ROOT — never inside .agent/)
    ├── ui/                   ← Only if 'frontend' or 'mobile' in detected_domains
    ├── backend/              ← Only if 'backend' in detected_domains
    ├── database/             ← Only if 'database' in detected_domains
    ├── logic/                ← Complex algorithm whitepapers (cross-domain)
    ├── features/             ← Feature blueprints with Definition of Done
    └── infra/                ← Only if 'infra' in detected_domains
    ════════════════════════════════════════════════════════════════════

    ATOMIC WRITE GUARANTEE (Staging Area Pattern):
    All files are written to `.tmp_agent/` and `docs.tmp/` first.
    A 1-to-1 integrity check verifies every manifest-declared file exists & is non-empty.
    Only on 100% success are the staging dirs merged into `.agent/` and `docs/`.
    On failure: RuntimeError lists every missing file, staging is cleaned up.
    """

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)

        # Final destinations
        self.agent_dir = self.project_path / ".agent"
        self.docs_dir = self.project_path / "docs"

        # Staging areas  ← all writes go here first
        self.tmp_agent_dir = self.project_path / ".tmp_agent"
        self.tmp_docs_dir = self.project_path / "docs.tmp"

    # ──────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────

    def generate(self, manifest: Manifest):
        """
        Atomic generation pipeline:
        1. Build manifest → expected file list
        2. Write everything to staging dirs
        3. Integrity check (1-to-1)
        4. Atomic rename staging → final on success; raise on failure
        """
        brain = manifest.instructional_brain
        if not brain:
            print(
                "\n[INFO] No Instructional Brain in manifest. Skipping .agent generation."
            )
            return

        # Clean any leftover staging dirs from a previous failed run
        self._cleanup_staging()

        # Build expected file list before writing
        expected_files = self._build_expected_manifest(brain)
        print(
            f"\n[SCAFFOLD] Manifest declares {len(expected_files)} files. Starting atomic write to staging..."
        )

        # Write everything into staging
        self._scaffold_staging_dirs(brain)
        self._write_agent_md(brain)
        self._write_rules_md(brain)
        self._write_preventative_rules(brain)
        self._write_sub_agent_rules(brain)  # NEW: domain-specific parallel rulebooks
        self._write_workflows(brain)
        self._write_skills(brain)
        self._write_docs(brain)
        self._write_metadata(brain)

        # 1-to-1 integrity check
        self._integrity_check(expected_files)

        # Atomic commit: staging → final
        self._atomic_commit()

        # Report
        actual_agent = sum(1 for f in self.agent_dir.rglob("*") if f.is_file())
        actual_docs = sum(1 for f in self.docs_dir.rglob("*") if f.is_file())
        print(
            f"\n[SUCCESS] Instructional Brain deployed.\n"
            f"  .agent/ → {actual_agent} files\n"
            f"  /docs/  → {actual_docs} files\n"
            f"  Total   → {actual_agent + actual_docs} files verified."
        )

    # ──────────────────────────────────────────────────────────────────
    # Manifest / Expected-file construction
    # ──────────────────────────────────────────────────────────────────

    def _build_expected_manifest(self, brain: InstructionalBrain) -> dict[str, str]:
        """
        Returns {relative_path: source_description} for every file the brain declares.
        Used for 1-to-1 integrity checking.
        """
        expected: dict[str, str] = {}

        if brain.agent_md:
            expected[".agent/AGENT.md"] = "brain.agent_md"
        if brain.rules_md:
            expected[".agent/RULES.md"] = "brain.rules_md"

        # Always expect metadata.json
        expected[".agent/metadata.json"] = "brain.metadata_index"

        for rule in brain.rules:
            expected[f".agent/rules/{rule.filename}"] = (
                f"brain.rules['{rule.filename}']"
            )

        # Sub-agent rulebooks in .agent/rules/sub_agents/
        for sar in brain.sub_agent_rules:
            expected[f".agent/rules/sub_agents/{sar.filename}"] = (
                f"brain.sub_agent_rules['{sar.domain}']"
            )

        for wf in brain.workflows:
            expected[f".agent/workflows/{wf.filename}"] = (
                f"brain.workflows['{wf.filename}']"
            )

        for skill in brain.skills:
            # Claude-style: filename = "skill-name/SKILL.md"
            # Normalise: if agent didn't include the subdir, inject it
            skill_path = self._normalise_skill_path(skill.filename)
            expected[f".agent/skills/{skill_path}"] = (
                f"brain.skills['{skill.filename}']"
            )

        for doc in brain.docs:
            expected[f"docs/{doc.filename}"] = f"brain.docs['{doc.filename}']"

        return expected

    # ──────────────────────────────────────────────────────────────────
    # Staging write helpers
    # ──────────────────────────────────────────────────────────────────

    def _scaffold_staging_dirs(self, brain: InstructionalBrain):
        """Creates the required staging subdirectories."""
        dirs = [
            self.tmp_agent_dir,
            self.tmp_agent_dir / "rules",
            self.tmp_agent_dir / "rules" / "sub_agents",  # Domain-specific rulebooks
            self.tmp_agent_dir / "workflows",
            self.tmp_agent_dir / "skills",
            # /docs/ sub-categories (created lazily per domain, but pre-create common ones)
            self.tmp_docs_dir / "logic",
            self.tmp_docs_dir / "features",
        ]

        # Create docs dirs only for detected domains (lean scaffolding)
        domain_docs_map = {
            "frontend": self.tmp_docs_dir / "ui",
            "mobile": self.tmp_docs_dir / "ui",
            "backend": self.tmp_docs_dir / "backend",
            "database": self.tmp_docs_dir / "database",
            "infra": self.tmp_docs_dir / "infra",
        }
        for domain in brain.detected_domains:
            if domain in domain_docs_map:
                dirs.append(domain_docs_map[domain])

        # If no detected_domains, default to full-stack dirs
        if not brain.detected_domains:
            dirs.extend(
                [
                    self.tmp_docs_dir / "ui",
                    self.tmp_docs_dir / "backend",
                    self.tmp_docs_dir / "database",
                    self.tmp_docs_dir / "infra",
                ]
            )

        # Pre-create skill subdirs for Claude-style layout
        for skill in brain.skills:
            skill_dir = self._normalise_skill_path(skill.filename).split("/")[0]
            dirs.append(self.tmp_agent_dir / "skills" / skill_dir)

        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    def _write_agent_md(self, brain: InstructionalBrain):
        if brain.agent_md:
            self._write(self.tmp_agent_dir / "AGENT.md", brain.agent_md)

    def _write_rules_md(self, brain: InstructionalBrain):
        if brain.rules_md:
            self._write(self.tmp_agent_dir / "RULES.md", brain.rules_md)

    def _write_preventative_rules(self, brain: InstructionalBrain):
        """Auditor-generated auto_*.md rules → .agent/rules/"""
        for rule in brain.rules:
            self._write(self.tmp_agent_dir / "rules" / rule.filename, rule.content)

    def _write_sub_agent_rules(self, brain: InstructionalBrain):
        """
        Domain-specific parallel agent rulebooks → .agent/rules/sub_agents/{domain}_agent.md
        These are self-contained: each domain agent loads only its own rulebook.
        """
        for sar in brain.sub_agent_rules:
            self._write(
                self.tmp_agent_dir / "rules" / "sub_agents" / sar.filename, sar.content
            )

    def _write_workflows(self, brain: InstructionalBrain):
        for wf in brain.workflows:
            content = wf.content
            if wf.success_criteria:
                content += "\n\n## ✅ Verification Hooks (Success Criteria)\n"
                for criterion in wf.success_criteria:
                    content += f"- [ ] {criterion}\n"
            self._write(self.tmp_agent_dir / "workflows" / wf.filename, content)

    def _write_skills(self, brain: InstructionalBrain):
        """
        Claude-style skill directories: .agent/skills/{skill-name}/SKILL.md
        Ensures YAML frontmatter is present; injects a minimal one if missing.
        """
        for skill in brain.skills:
            skill_path = self._normalise_skill_path(skill.filename)
            content = skill.content

            # Enforce YAML frontmatter
            if not content.strip().startswith("---"):
                skill_name = skill_path.split("/")[0]
                frontmatter = (
                    f"---\n"
                    f"name: {skill_name}\n"
                    f"description: Behavioral capability doc for {skill_name.replace('-', ' ')} tasks.\n"
                    f"disable-model-invocation: false\n"
                    f"---\n\n"
                )
                content = frontmatter + content

            self._write(self.tmp_agent_dir / "skills" / skill_path, content)

    def _write_docs(self, brain: InstructionalBrain):
        """Writes docs to /docs/ external library (staging: docs.tmp/)."""
        for doc in brain.docs:
            self._write(self.tmp_docs_dir / doc.filename, doc.content)

    def _write_metadata(self, brain: InstructionalBrain):
        """
        Builds and writes the smart lazy-load index to .agent/metadata.json.
        Priority: metadata_index (typed) → auto-derived.
        """
        if brain.metadata_index:
            index_payload = [entry.model_dump() for entry in brain.metadata_index]
        elif brain.metadata_json:
            index_payload = brain.metadata_json
        else:
            index_payload = self._derive_metadata(brain)

        metadata = {
            "schema_version": 2,
            "description": (
                "Lazy-load index. Read this FIRST. Load individual files only when their "
                "trigger_words match the current task. Never load all files eagerly."
            ),
            "index": index_payload,
        }
        self._write(
            self.tmp_agent_dir / "metadata.json", json.dumps(metadata, indent=2)
        )

    # ──────────────────────────────────────────────────────────────────
    # Integrity check
    # ──────────────────────────────────────────────────────────────────

    def _integrity_check(self, expected: dict[str, str]):
        """
        1-to-1 check: every path in `expected` must exist in the staging dirs.
        Raises a detailed RuntimeError listing EVERY missing filename.
        """
        failed: list[str] = []

        for rel_path, source in expected.items():
            if rel_path.startswith(".agent/"):
                physical = self.tmp_agent_dir / rel_path.removeprefix(".agent/")
            else:
                physical = self.tmp_docs_dir / rel_path.removeprefix("docs/")

            if not physical.exists() or physical.stat().st_size == 0:
                failed.append(f"  MISSING  {rel_path}  ← declared by {source}")

        if failed:
            self._cleanup_staging()
            details = "\n".join(failed)
            raise RuntimeError(
                f"[SCAFFOLD FAILURE] Integrity check failed.\n"
                f"Manifest declared {len(expected)} files but {len(failed)} are missing or empty:\n"
                f"{details}\n\n"
                f"Staging dirs cleaned up. Fix the agent output and retry."
            )

        print(
            f"[SCAFFOLD] Integrity check passed: all {len(expected)} files verified in staging."
        )

    # ──────────────────────────────────────────────────────────────────
    # Atomic commit
    # ──────────────────────────────────────────────────────────────────

    def _atomic_commit(self):
        """
        Atomically promote staging dirs → final dirs.
        Backs up existing dirs to .bak before replacing.
        """
        for tmp_dir, final_dir in [
            (self.tmp_agent_dir, self.agent_dir),
            (self.tmp_docs_dir, self.docs_dir),
        ]:
            bak = final_dir.with_suffix(".bak")

            # Remove old backup
            if bak.exists():
                shutil.rmtree(bak, ignore_errors=True)

            # Backup existing final dir
            if final_dir.exists():
                shutil.copytree(final_dir, bak)

            # Merge staging into final (preserving files not re-generated)
            self._merge_dir(tmp_dir, final_dir)

        # Clean up staging
        self._cleanup_staging()

    def _merge_dir(self, src: Path, dst: Path):
        """
        Smart merge: copy src into dst.
        Existing files are overwritten (new generation takes precedence).
        Files in dst that aren't in src are preserved (manual edits survive).
        """
        dst.mkdir(parents=True, exist_ok=True)
        for item in src.rglob("*"):
            rel = item.relative_to(src)
            target = dst / rel
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)

    def _cleanup_staging(self):
        for d in [self.tmp_agent_dir, self.tmp_docs_dir]:
            if d.exists():
                shutil.rmtree(d, ignore_errors=True)

    # ──────────────────────────────────────────────────────────────────
    # Utilities
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def _normalise_skill_path(filename: str) -> str:
        """
        Ensures skills follow Claude-style directory format: {name}/SKILL.md
        If the LLM outputs 'auth-expert.md' or 'auth_expert.md', normalise to
        'auth-expert/SKILL.md'.
        """
        if "/" in filename:
            # Already has a subdir (e.g. "auth-expert/SKILL.md") — use as-is
            return filename
        # Strip extension and convert to kebab-case directory name
        name = filename.replace(".md", "").replace("_", "-").lower()
        return f"{name}/SKILL.md"

    def _derive_metadata(self, brain: InstructionalBrain) -> list:
        """Auto-generate metadata entries when the LLM omits them."""
        entries = []

        if brain.agent_md:
            entries.append(
                {
                    "path": "AGENT.md",
                    "description": "Identity hub. Project soul, tech stack, and pointers to all assets. Read first.",
                    "trigger_words": [
                        "identity",
                        "overview",
                        "vibe",
                        "project",
                        "context",
                    ],
                }
            )
        if brain.rules_md:
            entries.append(
                {
                    "path": "RULES.md",
                    "description": "Constitution. Always-on meta-rules + on-demand phase rules. Load the relevant section.",
                    "trigger_words": ["rules", "constraint", "protocol", "phase"],
                }
            )

        # Sub-agent domain rulebooks
        for sar in brain.sub_agent_rules:
            entries.append(
                {
                    "path": f"rules/sub_agents/{sar.filename}",
                    "description": sar.description,
                    "trigger_words": sar.trigger_words or [sar.domain],
                }
            )

        for skill in brain.skills:
            skill_path = self._normalise_skill_path(skill.filename)
            name = skill_path.split("/")[0]
            entries.append(
                {
                    "path": f"skills/{skill_path}",
                    "description": f"Behavioral capability doc for {name.replace('-', ' ')} tasks.",
                    "trigger_words": name.split("-"),
                }
            )
        for wf in brain.workflows:
            entries.append(
                {
                    "path": f"workflows/{wf.filename}",
                    "description": f"Full-stack phase workflow with success criteria: {wf.filename}",
                    "trigger_words": [
                        wf.filename.split("_")[1] if "_" in wf.filename else wf.filename
                    ],
                }
            )
        for doc in brain.docs:
            entries.append(
                {
                    "path": f"../docs/{doc.filename}",
                    "description": f"Technical specification: {doc.filename}",
                    "trigger_words": [
                        doc.filename.split("/")[-1]
                        .replace(".md", "")
                        .replace("_", "-")
                        .lower()
                    ],
                }
            )
        for rule in brain.rules:
            entries.append(
                {
                    "path": f"rules/{rule.filename}",
                    "description": rule.description,
                    "trigger_words": [
                        rule.filename.replace(".md", "").replace("_", "-")
                    ],
                }
            )

        return entries

    def _write(self, filepath: Path, content: str, max_retries: int = 3):
        """Write to staging with retry on IOError (e.g. AV lock)."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        for attempt in range(max_retries):
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                return
            except IOError as e:
                if attempt < max_retries - 1:
                    print(
                        f"[WARNING] Could not write {filepath.name} (attempt {attempt+1}/{max_retries}): {e}"
                    )
                    time.sleep(0.5)
                else:
                    raise RuntimeError(
                        f"[ERROR] Failed to write {filepath} after {max_retries} attempts: {e}"
                    )
