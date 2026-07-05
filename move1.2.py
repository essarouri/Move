"""
╔══════════════════════════════════════════╗
║          Move v1.2 - Stay Awake          ║
║      Windows System Tray Utility         ║
╚══════════════════════════════════════════╝
"""

import ctypes
import time
import threading
import sys

try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    print("Install dependencies:")
    print("  pip install pystray Pillow")
    sys.exit(1)

# Check platform
if sys.platform != 'win32':
    print("❌ Move v1.2 is Windows-only!")
    sys.exit(1)

# App Info
APP_NAME    = "Move"
APP_VERSION = "1.2"
APP_FULL    = f"{APP_NAME} v{APP_VERSION}"

# Windows API Constants
ES_CONTINUOUS       = 0x80000000
ES_SYSTEM_REQUIRED  = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002


class Move:
    def __init__(self):
        self.active = False
        self.thread = None
        self.interval = 30
        self.icon = None
        self.timer_minutes = 0
        self.start_time = None

    # ──────────────────────────────────────────────
    #  Mouse (Animal) Icon Creation
    # ──────────────────────────────────────────────
    def _create_icon(self, active=False):
        """Create a cute mouse (animal) icon."""
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        if active:
            body_color   = '#A0A0A0'
            ear_color    = '#FFB6C1'
            nose_color   = '#FF6B8A'
            eye_color    = '#000000'
            tail_color   = '#FF8FAB'
            outline      = '#707070'
            whisker_col  = '#505050'
            bg_glow      = '#4CAF50'
        else:
            body_color   = '#B0B0B0'
            ear_color    = '#C8A0A0'
            nose_color   = '#C08080'
            eye_color    = '#404040'
            tail_color   = '#C0A0A0'
            outline      = '#909090'
            whisker_col  = '#808080'
            bg_glow      = None

        if bg_glow:
            draw.ellipse([2, 8, 62, 62], fill=None, outline=bg_glow, width=2)

        tail_points = [(8, 45), (4, 38), (6, 28), (12, 22), (16, 26)]
        draw.line(tail_points, fill=tail_color, width=3, joint='curve')

        draw.ellipse([14, 28, 54, 56], fill=body_color, outline=outline, width=2)
        draw.ellipse([34, 18, 60, 44], fill=body_color, outline=outline, width=2)

        draw.ellipse([32, 6, 46, 24], fill=body_color, outline=outline, width=2)
        draw.ellipse([35, 9, 43, 21], fill=ear_color)

        draw.ellipse([46, 4, 62, 22], fill=body_color, outline=outline, width=2)
        draw.ellipse([49, 7, 59, 19], fill=ear_color)

        draw.ellipse([46, 26, 52, 32], fill=eye_color)
        draw.ellipse([48, 27, 50, 29], fill='#FFFFFF')

        draw.ellipse([56, 32, 62, 38], fill=nose_color)

        draw.line([(56, 33), (63, 28)], fill=whisker_col, width=1)
        draw.line([(55, 34), (63, 32)], fill=whisker_col, width=1)
        draw.line([(56, 37), (63, 38)], fill=whisker_col, width=1)
        draw.line([(55, 38), (63, 42)], fill=whisker_col, width=1)

        draw.ellipse([40, 50, 48, 58], fill=body_color, outline=outline, width=1)

        if active:
            draw.ellipse([0, 0, 14, 14], fill='#4CAF50', outline='white', width=2)

        return img

    # ──────────────────────────────────────────────
    #  Windows API - Keep Awake
    # ──────────────────────────────────────────────
    def _keep_awake(self):
        """Use Windows API to prevent sleep."""
        while self.active:
            if self.timer_minutes > 0 and self.start_time:
                elapsed = time.time() - self.start_time
                if elapsed >= self.timer_minutes * 60:
                    self._deactivate()
                    return

            ctypes.windll.kernel32.SetThreadExecutionState(
                ES_CONTINUOUS |
                ES_SYSTEM_REQUIRED |
                ES_DISPLAY_REQUIRED
            )
            time.sleep(self.interval)

        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)

    # ──────────────────────────────────────────────
    #  Activate / Deactivate
    # ──────────────────────────────────────────────
    def _activate(self):
        """Turn Move ON."""
        self.active = True
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._keep_awake, daemon=True)
        self.thread.start()
        self._update_icon()

    def _deactivate(self):
        """Turn Move OFF."""
        self.active = False
        self.start_time = None
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
        self._update_icon()

    def _update_icon(self):
        """Update tray icon and tooltip."""
        if not self.icon:
            return

        self.icon.icon = self._create_icon(active=self.active)

        if self.active:
            if self.timer_minutes > 0:
                self.icon.title = f"🐭 {APP_FULL} — ON ({self.timer_minutes} min)"
            else:
                self.icon.title = f"🐭 {APP_FULL} — ON (Indefinite)"
        else:
            self.icon.title = f"🐭 {APP_FULL} — OFF"

    # ──────────────────────────────────────────────
    #  Menu Actions
    # ──────────────────────────────────────────────
    def toggle(self, icon=None, item=None):
        """Toggle Move on/off."""
        if self.active:
            self._deactivate()
        else:
            self.timer_minutes = 0
            self._activate()

    def activate_timed(self, minutes):
        """Activate for a set number of minutes."""
        def action(icon=None, item=None):
            if self.active:
                self._deactivate()
            self.timer_minutes = minutes
            self._activate()
        return action

    def activate_indefinite(self, icon=None, item=None):
        """Activate indefinitely."""
        if self.active:
            self._deactivate()
        self.timer_minutes = 0
        self._activate()

    def show_about(self, icon=None, item=None):
        """Show About dialog in a separate thread."""
        def _show():
            ctypes.windll.user32.MessageBoxW(
                0,
                f"🐭 {APP_FULL}\n\n"
                f"A lightweight stay-awake utility for Windows.\n\n"
                f"Prevents your PC from sleeping, locking,\n"
                f"or turning off the display.\n\n"
                f"Uses Windows SetThreadExecutionState API.\n"
                f"No mouse movement required.\n\n"
                f"© 2026, essarouri.com\n\n"
                f"Keep your mouse (🐭) moving!",
                f"About {APP_FULL}",
                0x40
            )

        about_thread = threading.Thread(target=_show, daemon=True)
        about_thread.start()

    def quit_app(self, icon=None, item=None):
        """Quit the application."""
        self._deactivate()
        if self.icon:
            self.icon.stop()

    def _is_active(self, item):
        """Check if Move is active (for menu checkmark)."""
        return self.active

    # ──────────────────────────────────────────────
    #  ✅ AUTO-START: Activate on tray icon setup
    # ──────────────────────────────────────────────
    def _on_setup(self, icon):
        """Called when tray icon is ready. Auto-activates Move."""
        icon.visible = True
        self._activate()

    # ──────────────────────────────────────────────
    #  Build Menu & Run
    # ──────────────────────────────────────────────
    def run(self):
        """Build system tray menu and run."""

        menu = pystray.Menu(
            pystray.MenuItem(
                f"🐭 {APP_FULL}",
                lambda icon, item: None,
                enabled=False
            ),

            pystray.Menu.SEPARATOR,

            pystray.MenuItem(
                "Toggle",
                self.toggle,
                default=True,
                checked=self._is_active
            ),

            pystray.Menu.SEPARATOR,

            pystray.MenuItem(
                "⏱ Activate For...",
                pystray.Menu(
                    pystray.MenuItem("15 Minutes", self.activate_timed(15)),
                    pystray.MenuItem("30 Minutes", self.activate_timed(30)),
                    pystray.MenuItem("1 Hour",     self.activate_timed(60)),
                    pystray.MenuItem("2 Hours",    self.activate_timed(120)),
                    pystray.MenuItem("4 Hours",    self.activate_timed(240)),
                    pystray.MenuItem("8 Hours",    self.activate_timed(480)),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem("♾ Indefinite", self.activate_indefinite),
                )
            ),

            pystray.Menu.SEPARATOR,

            pystray.MenuItem(
                "ℹ About",
                self.show_about
            ),

            pystray.MenuItem(f"❌ Quit {APP_NAME}", self.quit_app),
        )

        # ✅ Create tray icon with ACTIVE state from start
        self.icon = pystray.Icon(
            name=APP_NAME,
            icon=self._create_icon(active=True),    # ✅ Start with green icon
            title=f"🐭 {APP_FULL} — ON (Indefinite)",  # ✅ Start with ON tooltip
            menu=menu
        )

        # ✅ Run with setup callback — auto-activates!
        self.icon.run(setup=self._on_setup)


# ──────────────────────────────────────────────
#  Entry Point
# ──────────────────────────────────────────────
if __name__ == "__main__":
    app = Move()
    app.run()