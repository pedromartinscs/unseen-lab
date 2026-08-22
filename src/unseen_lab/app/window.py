from __future__ import annotations

import math
from pathlib import Path

from PIL import Image
from PIL.ImageQt import ImageQt
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QImage, QKeySequence, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from unseen_lab.core.models import PipelineConfig, ProcessingResult
from unseen_lab.core.pipeline import process_image
from unseen_lab.io import load_image, save_image


class ImageEditorWindow(QMainWindow):
    """Focused image editor shell backed by the shared core pipeline."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Unseen Lab")
        self.resize(1280, 800)
        self.setMinimumSize(900, 620)

        self._path: Path | None = None
        self._original: Image.Image | None = None
        self._result: ProcessingResult | None = None
        self._show_original = False

        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(140)
        self._preview_timer.timeout.connect(self._rebuild_preview)

        self._build_toolbar()
        self._build_workspace()
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Open an image to begin")
        self._sync_enabled_state()

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Main", self)
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)

        self.open_action = QAction("Open", self)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.triggered.connect(self._open_image)
        toolbar.addAction(self.open_action)

        self.save_action = QAction("Save As", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.save_action.triggered.connect(self._save_as)
        toolbar.addAction(self.save_action)

        toolbar.addSeparator()

        self.reset_action = QAction("Reset", self)
        self.reset_action.triggered.connect(self._reset_controls)
        toolbar.addAction(self.reset_action)

        self.original_action = QAction("Show Original", self)
        self.original_action.setCheckable(True)
        self.original_action.toggled.connect(self._toggle_original)
        toolbar.addAction(self.original_action)

    def _build_workspace(self) -> None:
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.setCentralWidget(splitter)

        self.preview_label = QLabel("IMAGE PREVIEW\n\nOpen an image to start")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(480, 360)
        self.preview_label.setStyleSheet(
            "QLabel { background: #16191f; color: #8f98a8; border: 1px solid #2a303a; }"
        )

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.preview_label)
        splitter.addWidget(scroll)

        inspector = QWidget()
        inspector.setMinimumWidth(310)
        inspector.setMaximumWidth(390)
        layout = QVBoxLayout(inspector)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("UNSEEN LAB")
        title.setStyleSheet("font-size: 18px; font-weight: 700; letter-spacing: 2px;")
        subtitle = QLabel("Controlled transformation workspace")
        subtitle.setStyleSheet("color: #7f8896;")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        transform_group = QGroupBox("Transform Stack")
        form = QFormLayout(transform_group)

        self.noise_spin = QDoubleSpinBox()
        self.noise_spin.setRange(0.0, 25.0)
        self.noise_spin.setDecimals(2)
        self.noise_spin.setSingleStep(0.25)
        self.noise_spin.setValue(2.0)
        self.noise_spin.setSuffix(" σ")
        form.addRow("Gaussian noise", self.noise_spin)

        self.monochrome_check = QCheckBox("Shared across RGB channels")
        form.addRow("Noise mode", self.monochrome_check)

        self.blur_spin = QDoubleSpinBox()
        self.blur_spin.setRange(0.0, 5.0)
        self.blur_spin.setDecimals(2)
        self.blur_spin.setSingleStep(0.05)
        self.blur_spin.setValue(0.0)
        self.blur_spin.setSuffix(" px")
        form.addRow("Gaussian blur", self.blur_spin)

        self.resample_spin = QDoubleSpinBox()
        self.resample_spin.setRange(0.90, 1.10)
        self.resample_spin.setDecimals(4)
        self.resample_spin.setSingleStep(0.001)
        self.resample_spin.setValue(1.0)
        form.addRow("Micro-resample", self.resample_spin)

        self.jpeg_check = QCheckBox("Enable JPEG round-trip")
        form.addRow("Compression", self.jpeg_check)

        self.jpeg_quality_spin = QSpinBox()
        self.jpeg_quality_spin.setRange(1, 100)
        self.jpeg_quality_spin.setValue(96)
        self.jpeg_quality_spin.setEnabled(False)
        form.addRow("JPEG quality", self.jpeg_quality_spin)

        self.seed_spin = QSpinBox()
        self.seed_spin.setRange(-1, 2_147_483_647)
        self.seed_spin.setSpecialValueText("Random")
        self.seed_spin.setValue(42)
        form.addRow("Seed", self.seed_spin)

        layout.addWidget(transform_group)

        metrics_group = QGroupBox("Similarity")
        metrics_form = QFormLayout(metrics_group)
        self.mae_value = QLabel("—")
        self.rmse_value = QLabel("—")
        self.psnr_value = QLabel("—")
        metrics_form.addRow("MAE", self.mae_value)
        metrics_form.addRow("RMSE", self.rmse_value)
        metrics_form.addRow("PSNR", self.psnr_value)
        layout.addWidget(metrics_group)

        button_row = QHBoxLayout()
        self.preview_button = QPushButton("Preview")
        self.preview_button.clicked.connect(self._rebuild_preview)
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self._reset_controls)
        button_row.addWidget(self.preview_button)
        button_row.addWidget(self.reset_button)
        layout.addLayout(button_row)
        layout.addStretch(1)

        splitter.addWidget(inspector)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        splitter.setSizes([900, 340])

        self.jpeg_check.toggled.connect(self.jpeg_quality_spin.setEnabled)
        for control in (
            self.noise_spin,
            self.blur_spin,
            self.resample_spin,
            self.jpeg_quality_spin,
            self.seed_spin,
        ):
            control.valueChanged.connect(self._schedule_preview)
        self.monochrome_check.toggled.connect(self._schedule_preview)
        self.jpeg_check.toggled.connect(self._schedule_preview)

    def _sync_enabled_state(self) -> None:
        enabled = self._original is not None
        for widget in (
            self.save_action,
            self.reset_action,
            self.original_action,
            self.preview_button,
            self.reset_button,
        ):
            widget.setEnabled(enabled)

    def _config(self) -> PipelineConfig:
        seed = None if self.seed_spin.value() < 0 else self.seed_spin.value()
        jpeg_quality = self.jpeg_quality_spin.value() if self.jpeg_check.isChecked() else None
        return PipelineConfig(
            noise_sigma=self.noise_spin.value(),
            monochrome_noise=self.monochrome_check.isChecked(),
            blur_radius=self.blur_spin.value(),
            resample_scale=self.resample_spin.value(),
            jpeg_quality=jpeg_quality,
            seed=seed,
        )

    def _schedule_preview(self, *_args: object) -> None:
        if self._original is not None:
            self._preview_timer.start()

    def _open_image(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open image",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff)",
        )
        if not filename:
            return
        try:
            self._original = load_image(filename)
        except Exception as exc:
            QMessageBox.critical(self, "Open failed", str(exc))
            return

        self._path = Path(filename)
        self._result = None
        self.setWindowTitle(f"Unseen Lab — {self._path.name}")
        self._sync_enabled_state()
        self._rebuild_preview()

    def _save_as(self) -> None:
        if self._result is None:
            return
        default_name = (
            f"{self._path.stem}-unseen.png" if self._path is not None else "processed.png"
        )
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save processed image",
            default_name,
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;WebP (*.webp)",
        )
        if not filename:
            return
        try:
            save_image(self._result.image, filename)
        except Exception as exc:
            QMessageBox.critical(self, "Save failed", str(exc))
            return
        self.statusBar().showMessage(f"Saved {filename}", 5000)

    def _reset_controls(self) -> None:
        self.noise_spin.setValue(2.0)
        self.monochrome_check.setChecked(False)
        self.blur_spin.setValue(0.0)
        self.resample_spin.setValue(1.0)
        self.jpeg_check.setChecked(False)
        self.jpeg_quality_spin.setValue(96)
        self.seed_spin.setValue(42)
        self.original_action.setChecked(False)
        self._rebuild_preview()

    def _toggle_original(self, checked: bool) -> None:
        self._show_original = checked
        self._render_current_image()

    def _rebuild_preview(self) -> None:
        if self._original is None:
            return
        try:
            self._result = process_image(self._original, self._config())
        except Exception as exc:
            QMessageBox.critical(self, "Processing failed", str(exc))
            return

        metrics = self._result.metrics
        self.mae_value.setText(f"{metrics.mae:.4f}")
        self.rmse_value.setText(f"{metrics.rmse:.4f}")
        self.psnr_value.setText(
            "∞" if math.isinf(metrics.psnr_db) else f"{metrics.psnr_db:.2f} dB"
        )
        self.statusBar().showMessage(
            f"{self._original.width} × {self._original.height}  •  preview updated"
        )
        self._render_current_image()

    def _render_current_image(self) -> None:
        if self._original is None:
            return
        image = (
            self._original
            if self._show_original or self._result is None
            else self._result.image
        )
        qimage = QImage(ImageQt(image.convert("RGBA")))
        pixmap = QPixmap.fromImage(qimage)
        target = self.preview_label.size()
        if target.width() > 2 and target.height() > 2:
            pixmap = pixmap.scaled(
                target,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        self.preview_label.setPixmap(pixmap)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._render_current_image()
