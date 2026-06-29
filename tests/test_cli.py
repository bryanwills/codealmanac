from pathlib import Path

from codealmanac.cli.main import main


def test_cli_init_creates_wiki_and_prints_name(
    tmp_path: Path,
    isolated_home: Path,
    capsys,
):
    repo = tmp_path / "My Repo"
    repo.mkdir()

    exit_code = main(["init", str(repo), "--description", "cli test"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "my-repo\n"
    assert "initialized" in captured.err
    assert (repo / ".almanac/pages/getting-started.md").is_file()
    assert (isolated_home / ".almanac/registry.json").is_file()


def test_cli_list_outputs_registered_wikis(
    tmp_path: Path,
    isolated_home: Path,
    capsys,
):
    repo = tmp_path / "repo"
    repo.mkdir()

    assert main(["init", str(repo)]) == 0
    capsys.readouterr()

    exit_code = main(["list"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == f"repo\t{repo}\n"
