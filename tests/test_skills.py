from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_skills_inventory_and_markdown():
    skills_dir = REPO_ROOT / "skills"
    assert skills_dir.is_dir()
    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir()]
    assert len(skill_dirs) == 20, f"Expected 20 skills, found {len(skill_dirs)}"

    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    for skill_path in skill_dirs:
        skill_md = skill_path / "SKILL.md"
        assert skill_md.is_file(), f"Missing SKILL.md in {skill_path.name}"
        content = skill_md.read_text(encoding="utf-8")
        # Strip fenced code blocks
        clean_content = re.sub(r"```[\s\S]*?```", "", content)
        # Strip inline code
        clean_content = re.sub(r"`[^`\n]+`", "", clean_content)

        for match in link_pattern.finditer(clean_content):
            url = match.group(2).strip()
            # If it's an external url, skip
            if url.startswith("http://") or url.startswith("https://") or url.startswith("#") or url.startswith("mailto:"):
                continue
            # Strip anchors
            file_part = url.split("#")[0]
            if not file_part:
                continue

            target_file = (skill_path / file_part).resolve()
            assert target_file.exists(), (
                f"Broken relative link in {skill_md}: '{url}' resolved to '{target_file}' which does not exist."
            )
