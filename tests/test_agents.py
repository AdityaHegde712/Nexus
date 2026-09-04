from pathlib import Path
import tomllib

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_agent_definitions():
    agents_dir = REPO_ROOT / "agents"
    assert agents_dir.is_dir()
    toml_files = list(agents_dir.glob("*.toml"))
    assert len(toml_files) >= 2, "Expected at least developer and adversary TOMLs"

    for file_path in toml_files:
        with open(file_path, "rb") as f:
            data = tomllib.load(f)
        assert "name" in data, f"Missing 'name' in {file_path.name}"
        assert "description" in data, f"Missing 'description' in {file_path.name}"
        assert "model" in data, f"Missing 'model' in {file_path.name}"
        assert "developer_instructions" in data, f"Missing 'developer_instructions' in {file_path.name}"
