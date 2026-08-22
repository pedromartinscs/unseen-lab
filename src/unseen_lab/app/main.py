from __future__ import annotations

import sys


def main() -> int:
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise SystemExit(
            'The desktop UI requires PySide6. Install it with: pip install -e ".[desktop]"'
        ) from exc

    from unseen_lab.app.window import ImageEditorWindow

    app = QApplication(sys.argv)
    app.setApplicationName("Unseen Lab")
    app.setOrganizationName("Unseen Lab")

    window = ImageEditorWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
