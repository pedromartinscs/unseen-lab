from pathlib import Path

from PIL import Image

from unseen_lab.cli import main


def test_cli_writes_output(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    destination = tmp_path / "out.png"
    Image.new("RGB", (10, 10), (120, 90, 40)).save(source)

    code = main(
        [
            str(source),
            str(destination),
            "--noise",
            "1.0",
            "--seed",
            "7",
        ]
    )

    assert code == 0
    assert destination.is_file()
    with Image.open(destination) as output:
        assert output.size == (10, 10)
