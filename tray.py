"""
System Tray Manager for BotMyPC.

Integrates with Windows Notification Area via pystray and Pillow:
- Context menu: 'Mostra' (restore GUI) and 'Esci' (orderly shutdown).
- Icon generation/loading.
- Runs non-blocking (run_detached) so main thread remains exclusively for CustomTkinter.
"""

from __future__ import annotations
import logging
from pathlib import Path
from typing import Callable, Optional
from PIL import Image, ImageDraw
import pystray

from config import APP_NAME, APP_DISPLAY_TITLE, ICON_PATH
from i18n import t

logger = logging.getLogger(APP_NAME)


def _load_or_generate_icon() -> Image.Image:
    """Loads the application icon or generates a fallback Matrix-style Pillow image."""
    if ICON_PATH.exists():
        try:
            return Image.open(ICON_PATH)
        except Exception as e:
            logger.warning(t("log_tray_icon_error", path=ICON_PATH, e=e))

    # Fallback in-memory image
    size = 64
    img = Image.new("RGBA", (size, size), (10, 10, 10, 255))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([4, 4, 59, 59], radius=8, outline=(0, 255, 102, 255), width=3)
    draw.line([(16, 24), (24, 32), (16, 40)], fill=(0, 255, 102, 255), width=3)
    draw.line([(28, 40), (40, 40)], fill=(0, 255, 102, 255), width=3)
    return img


class SystemTrayManager:
    """
    Manages the Windows Notification Area tray icon and actions.
    """

    def __init__(
        self,
        on_show: Callable[[], None],
        on_exit: Callable[[], None],
    ) -> None:
        self._on_show = on_show
        self._on_exit = on_exit
        self._icon: Optional[pystray.Icon] = None
        self._is_running = False

    def start(self) -> None:
        """Starts the system tray icon in detached mode."""
        if self._is_running:
            return

        image = _load_or_generate_icon()
        menu = pystray.Menu(
            pystray.MenuItem(t("tray_show"), self._handle_show, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(t("tray_exit"), self._handle_exit),
        )

        self._icon = pystray.Icon(
            name=APP_NAME,
            icon=image,
            title=APP_DISPLAY_TITLE,
            menu=menu,
        )

        try:
            self._icon.run_detached()
            self._is_running = True
            logger.info(t("log_tray_started"))
        except Exception as e:
            logger.error(t("log_tray_start_error", e=e))

    def stop(self) -> None:
        """Stops and removes the system tray icon."""
        if self._icon and self._is_running:
            try:
                self._icon.stop()
            except Exception:
                pass
            self._is_running = False
            logger.info(t("log_tray_stopped"))

    def _handle_show(self, icon: Optional[pystray.Icon] = None, item: Optional[pystray.MenuItem] = None) -> None:
        try:
            self._on_show()
        except Exception as e:
            logger.error(t("log_tray_show_error", e=e))

    def _handle_exit(self, icon: Optional[pystray.Icon] = None, item: Optional[pystray.MenuItem] = None) -> None:
        try:
            self._on_exit()
        except Exception as e:
            logger.error(t("log_tray_exit_error", e=e))
