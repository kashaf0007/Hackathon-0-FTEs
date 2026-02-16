"""Skill Loader for Bronze Tier Constitutional FTE.

Dynamically loads, validates, and manages skills from .claude/skills/ directory.
"""

from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from src.models import SkillDefinition
from src.utils import validate_skill_sections


class SkillLoader:
    """Skill loader for dynamic skill management.

    Discovers, parses, validates, and caches skills from .claude/skills/ directory.
    Ensures all skills follow required SKILL.md schema.
    """

    REQUIRED_SECTIONS = [
        "Purpose",
        "Constitutional Alignment",
        "Inputs",
        "Outputs",
        "Risk Classification",
        "Execution Logic",
        "HITL Checkpoint",
        "Logging Requirements",
        "Failure Handling",
        "Completion Condition"
    ]

    def __init__(self, skills_path: Path):
        """Initialize skill loader.

        Args:
            skills_path: Path to .claude/skills directory
        """
        self.skills_path = Path(skills_path)
        self.skill_cache: Dict[str, SkillDefinition] = {}
        self.last_scan: Optional[datetime] = None

    def discover_skills(self) -> List[Path]:
        """Discover all skill directories in .claude/skills/.

        Returns:
            List of paths to skill directories containing SKILL.md
        """
        if not self.skills_path.exists():
            return []

        skill_dirs = []
        for skill_dir in self.skills_path.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    skill_dirs.append(skill_dir)

        return skill_dirs

    def parse_skill_md(self, skill_file: Path) -> Dict[str, str]:
        """Parse SKILL.md file into sections.

        Args:
            skill_file: Path to SKILL.md file

        Returns:
            Dictionary mapping section names to content

        Raises:
            ValueError: If file cannot be parsed
        """
        try:
            content = skill_file.read_text(encoding='utf-8')
        except Exception as e:
            raise ValueError(f"Cannot read SKILL.md: {e}")

        sections = {}
        current_section = None
        current_content = []

        for line in content.split('\n'):
            # Check for section header (## Section Name)
            if line.startswith('## '):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()

                # Start new section
                current_section = line[3:].strip()
                current_content = []
            elif line.startswith('# '):
                # Skill title (first line)
                sections['title'] = line[2:].strip()
            else:
                # Section content
                if current_section:
                    current_content.append(line)

        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def validate_skill_sections(self, sections: Dict[str, str], skill_name: str) -> List[str]:
        """Validate that all required sections are present.

        Args:
            sections: Parsed sections from SKILL.md
            skill_name: Name of skill for error messages

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check for required sections
        for required in self.REQUIRED_SECTIONS:
            if required not in sections:
                errors.append(f"Missing required section: {required}")
            elif not sections[required].strip():
                errors.append(f"Empty required section: {required}")

        # Check for title
        if 'title' not in sections or not sections['title'].strip():
            errors.append("Missing skill title (# Skill Name)")

        # Validate Risk Classification values
        if 'Risk Classification' in sections:
            risk = sections['Risk Classification'].strip().upper()
            if risk not in ['LOW', 'MEDIUM', 'HIGH']:
                errors.append(f"Invalid Risk Classification: {risk} (must be LOW, MEDIUM, or HIGH)")

        return errors

    def load_skill(self, skill_dir: Path, use_cache: bool = True) -> Optional[SkillDefinition]:
        """Load and validate a single skill.

        Args:
            skill_dir: Path to skill directory
            use_cache: Whether to use cached skill if available

        Returns:
            SkillDefinition or None if invalid
        """
        skill_name = skill_dir.name

        # Check cache
        if use_cache and skill_name in self.skill_cache:
            return self.skill_cache[skill_name]

        skill_file = skill_dir / "SKILL.md"

        try:
            # Parse SKILL.md
            sections = self.parse_skill_md(skill_file)

            # Validate sections
            errors = self.validate_skill_sections(sections, skill_name)
            if errors:
                error_msg = f"Skill '{skill_name}' validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
                raise ValueError(error_msg)

            # Extract risk level
            risk_level = sections.get('Risk Classification', 'MEDIUM').strip().upper()

            # Create SkillDefinition
            skill = SkillDefinition(
                name=skill_name,
                title=sections.get('title', skill_name),
                purpose=sections.get('Purpose', ''),
                risk_level=risk_level,
                constitutional_alignment=sections.get('Constitutional Alignment', ''),
                inputs=sections.get('Inputs', ''),
                outputs=sections.get('Outputs', ''),
                execution_logic=sections.get('Execution Logic', ''),
                hitl_checkpoint=sections.get('HITL Checkpoint', ''),
                logging_requirements=sections.get('Logging Requirements', ''),
                failure_handling=sections.get('Failure Handling', ''),
                completion_condition=sections.get('Completion Condition', ''),
                skill_path=str(skill_dir)
            )

            # Cache the skill
            self.skill_cache[skill_name] = skill

            return skill

        except Exception as e:
            print(f"ERROR loading skill '{skill_name}': {e}")
            return None

    def load_all_skills(self, use_cache: bool = True) -> Dict[str, SkillDefinition]:
        """Load all skills from .claude/skills/ directory.

        Args:
            use_cache: Whether to use cached skills if available

        Returns:
            Dictionary mapping skill names to SkillDefinition objects
        """
        skill_dirs = self.discover_skills()
        skills = {}

        for skill_dir in skill_dirs:
            skill = self.load_skill(skill_dir, use_cache=use_cache)
            if skill:
                skills[skill.name] = skill

        self.last_scan = datetime.now()
        return skills

    def validate_all_skills(self) -> Dict[str, List[str]]:
        """Validate all skills and return errors.

        Returns:
            Dictionary mapping skill names to list of validation errors
        """
        skill_dirs = self.discover_skills()
        validation_results = {}

        for skill_dir in skill_dirs:
            skill_name = skill_dir.name
            skill_file = skill_dir / "SKILL.md"

            try:
                sections = self.parse_skill_md(skill_file)
                errors = self.validate_skill_sections(sections, skill_name)
                if errors:
                    validation_results[skill_name] = errors
            except Exception as e:
                validation_results[skill_name] = [str(e)]

        return validation_results

    def get_skill(self, skill_name: str) -> Optional[SkillDefinition]:
        """Get a skill by name from cache.

        Args:
            skill_name: Name of skill to retrieve

        Returns:
            SkillDefinition or None if not found
        """
        return self.skill_cache.get(skill_name)

    def clear_cache(self) -> None:
        """Clear the skill cache."""
        self.skill_cache.clear()
        self.last_scan = None
