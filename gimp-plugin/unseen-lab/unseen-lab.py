#!/usr/bin/env python3
from __future__ import annotations

import sys

import gi
import numpy as np

gi.require_version("Gimp", "3.0")
gi.require_version("Gegl", "0.4")

from gi.repository import Gegl, Gimp, GLib, GObject

from unseen_lab.core.noise import add_gaussian_noise_array

PROCEDURE_NAME = "plug-in-unseen-lab-subtle-noise"
PLUGIN_BINARY = "unseen-lab"


def _run(procedure, run_mode, image, drawables, config, data):
    if len(drawables) != 1:
        return procedure.new_return_values(
            Gimp.PDBStatusType.CALLING_ERROR,
            GLib.Error("Unseen Lab currently requires exactly one drawable."),
        )

    if run_mode == Gimp.RunMode.INTERACTIVE:
        gi.require_version("GimpUi", "3.0")
        from gi.repository import GimpUi

        GimpUi.init(PLUGIN_BINARY)
        dialog = GimpUi.ProcedureDialog.new(
            procedure,
            config,
            "Unseen Lab — Subtle Gaussian Noise",
        )
        dialog.fill(["sigma", "monochrome", "seed"])
        if not dialog.run():
            dialog.destroy()
            return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, None)
        dialog.destroy()

    drawable = drawables[0]
    sigma = float(config.get_property("sigma"))
    monochrome = bool(config.get_property("monochrome"))
    configured_seed = int(config.get_property("seed"))
    seed = None if configured_seed < 0 else configured_seed

    buffer = drawable.get_buffer()
    rect = buffer.get_extent()
    format_name = "R'G'B'A u8"

    raw = buffer.introspectable_get(
        rect,
        1.0,
        format_name,
        Gegl.AbyssPolicy.NONE,
    )
    pixels = np.frombuffer(raw, dtype=np.uint8).reshape(rect.height, rect.width, 4).copy()

    pixels[..., :3] = add_gaussian_noise_array(
        pixels[..., :3],
        sigma=sigma,
        monochrome=monochrome,
        seed=seed,
    )

    image.undo_group_start()
    try:
        buffer.introspectable_set(rect, format_name, pixels.tobytes())
        buffer.flush()
        drawable.update(rect.x, rect.y, rect.width, rect.height)
    finally:
        image.undo_group_end()

    Gimp.displays_flush()
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)


class UnseenLabPlugin(Gimp.PlugIn):
    def do_query_procedures(self):
        return [PROCEDURE_NAME]

    def do_create_procedure(self, name):
        if name != PROCEDURE_NAME:
            return None

        procedure = Gimp.ImageProcedure.new(
            self,
            name,
            Gimp.PDBProcType.PLUGIN,
            _run,
            None,
        )
        procedure.set_image_types("RGB*, GRAY*")
        procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.DRAWABLE)
        procedure.set_menu_label("Subtle Gaussian Noise…")
        procedure.add_menu_path("<Image>/Filters/Unseen Lab/")
        procedure.set_documentation(
            "Add controlled Gaussian noise with Unseen Lab.",
            "Applies the shared Unseen Lab Gaussian-noise primitive to one drawable.",
            PROCEDURE_NAME,
        )
        procedure.set_attribution("Pedro Martins", "Pedro Martins", "2026")

        procedure.add_double_argument(
            "sigma",
            "Sigma",
            "Gaussian standard deviation in 8-bit channel units.",
            0.0,
            25.0,
            2.0,
            GObject.ParamFlags.READWRITE,
        )
        procedure.add_boolean_argument(
            "monochrome",
            "Monochrome noise",
            "Use one noise value per pixel across RGB channels.",
            False,
            GObject.ParamFlags.READWRITE,
        )
        procedure.add_int_argument(
            "seed",
            "Seed",
            "Deterministic seed; use -1 for a random seed.",
            -1,
            2_147_483_647,
            42,
            GObject.ParamFlags.READWRITE,
        )
        return procedure


Gimp.main(UnseenLabPlugin.__gtype__, sys.argv)
