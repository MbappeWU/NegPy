from negpy.kernel.system.i18n import tr

from negpy.desktop.view.sidebar.base import BaseSidebar
from negpy.desktop.view.styles.templates import hint_label
from negpy.desktop.view.widgets.choice_button import SegmentedChoice
from negpy.features.process.models import scan_setup_rig

_LIGHT_HINT = {
    "camera": {
        "white": tr("A lightbox or high-CRI LED panel — one broadband exposure"),
        "narrowband": tr("A Scanlight or RGB-LED source — pure red, green and blue bands"),
    },
    "scanner": {
        "white": tr("A cold-cathode or white-LED lamp — Plustek, Epson, most flatbeds"),
        "narrowband": tr("RGB-LED illumination — Nikon Coolscan, Kodak Pakon"),
    },
}


def detected_capture(state) -> str:
    """A camera RAW (it has a camera matrix) reads as "camera", anything else as "scanner"; with no frame open, "camera"."""
    if not state.current_file_hash:
        return "camera"
    return "camera" if state.preview_cam_xyz is not None else "scanner"


def resolved_rig(repo, state) -> tuple[str, str]:
    """(capture, light) of the scanning setup, Auto resolved against the open frame."""
    capture, light = scan_setup_rig(repo.get_global_setting("scan_setup"))
    return (detected_capture(state) if capture == "auto" else capture), light


class ScanSetupSidebar(BaseSidebar):
    """How the roll was scanned: it sets the RAW decode and the print stock, and decides which
    Roll-tab controls show. One setting for the app, as the rig is."""

    def _init_ui(self) -> None:
        self.capture_btn = SegmentedChoice(
            (("fa5s.magic", tr("Auto")), ("fa5s.camera", tr("Camera")), ("fa5s.camera-retro", tr("Film Scanner"))),
            tr(
                "What the negatives were scanned with. Auto reads it from the file: a camera RAW is a "
                "camera, anything else a film scanner. Pick one to override it."
            ),
            data=("auto", "camera", "scanner"),
        )
        self.light_btn = SegmentedChoice(
            (("mdi6.lightbulb-outline", tr("White Light")), ("mdi6.led-on", tr("Narrowband RGB"))),
            tr("The light behind the negative"),
            data=("white", "narrowband"),
        )
        self.hint = hint_label("")
        self.layout.addWidget(self.capture_btn)
        self.layout.addWidget(self.light_btn)
        self.layout.addWidget(self.hint)

    def _connect_signals(self) -> None:
        self.capture_btn.currentChanged.connect(self._on_changed)
        self.light_btn.currentChanged.connect(self._on_changed)

    def _on_changed(self, _index: int) -> None:
        self.controller.apply_scan_setup(self.capture_btn.currentData(), self.light_btn.currentData())
        # With no frame open nothing re-syncs the panel, and the cards follow the setup.
        self.controller.config_updated.emit()

    def sync_ui(self) -> None:
        capture, light = scan_setup_rig(self.controller.session.repo.get_global_setting("scan_setup"))
        for btn, value in ((self.capture_btn, capture), (self.light_btn, light)):
            btn.blockSignals(True)
            btn.setCurrentIndex(btn.findData(value))
            btn.blockSignals(False)
        resolved = detected_capture(self.state) if capture == "auto" else capture
        detected = (
            (tr("A camera RAW, so a camera.") if resolved == "camera" else tr("Not a camera RAW, so a film scanner."))
            if capture == "auto" and self.state.current_file_hash
            else ""
        )
        self.hint.setText(" ".join(t for t in (detected, _LIGHT_HINT[resolved][light]) if t))
