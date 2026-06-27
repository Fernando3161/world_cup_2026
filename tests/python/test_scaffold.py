from pathlib import Path


def test_stage_1_scaffold_directories_exist() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    expected_directories = [
        "frontend/src",
        "frontend/public/data",
        "scripts",
        "data/raw/elo",
        "data/raw/results",
        "data/manual",
        "data/snapshots",
        "data/processed",
        "data/frontend",
        "tests/python",
        "tests/frontend",
        "docs",
    ]

    for directory in expected_directories:
        assert (repo_root / directory).is_dir(), directory

