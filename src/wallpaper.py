"""Wallpaper setter for Ubuntu and other Linux desktops."""

import logging
import os
import subprocess
from pathlib import Path
from typing import Literal

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s: %(message)s : %(asctime)s",
)
logger = logging.getLogger(__name__)


def detect_desktop_environment() -> str:
    """Detect the current desktop environment."""
    desktop_env = os.getenv("XDG_CURRENT_DESKTOP", "").lower()

    if "gnome" in desktop_env:
        return "gnome"
    if "kde" in desktop_env or "plasmadesktop" in desktop_env:
        return "kde"
    if "xfce" in desktop_env:
        return "xfce"
    if "cinnamon" in desktop_env:
        return "cinnamon"
    return "unknown"


def validate_image(image_path: str) -> Path:
    """Validate that the image file exists and is readable."""
    path = Path(image_path).expanduser().absolute()

    if not path.exists():
        msg = f"Image file not found: {image_path}"
        raise FileNotFoundError(msg)

    if not path.is_file():
        msg = f"Path is not a file: {image_path}"
        raise IsADirectoryError(msg)

    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}
    if path.suffix.lower() not in valid_extensions:
        msg = f"Unsupported image format: {path.suffix}"
        raise ValueError(msg)

    return path


def set_wallpaper_gnome(image_path: Path) -> bool:
    """Set wallpaper for GNOME Desktop."""
    try:
        # Set both light and dark wallpapers
        cmd = [
            "gsettings",
            "set",
            "org.gnome.desktop.background",
            "picture-uri",
            f"file://{image_path}",
        ]
        subprocess.run(cmd, check=True, capture_output=True)  # noqa: S603

        # Also set the dark variant for newer GNOME versions
        try:
            cmd_dark = [
                "gsettings",
                "set",
                "org.gnome.desktop.background",
                "picture-uri-dark",
                f"file://{image_path}",
            ]
            subprocess.run(cmd_dark, check=True, capture_output=True)  # noqa: S603
        except subprocess.CalledProcessError:
            pass  # Dark variant might not exist in older GNOME versions

    except subprocess.CalledProcessError:
        logger.exception(
            "Error setting GNOME wallpaper",
        )
        return False
    except Exception:
        logger.exception("Unexpected error with GNOME")
        return False
    else:
        return True


def set_wallpaper_kde(image_path: Path) -> bool:
    """Set wallpaper for KDE Plasma."""
    try:
        # Create a simple POSIX shell script that KDE understands
        script = f"""
        dbus-send --session --dest=org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript 'string:
        var Plasma = getApiVersion(1);
        var desktops = desktops();
        for (var i=0; i<desktops.length; i++) {{
            desktops[i].wallpaperPlugin = "org.kde.image";
            desktops[i].currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
            desktops[i].writeConfig("Image", "file://{image_path}");
        }}'
        """  # noqa: E501
        subprocess.run(script, shell=True, check=True, capture_output=True)  # noqa: S602

    except subprocess.CalledProcessError:
        logger.exception("Error setting KDE wallpaper")
        return False
    except Exception:
        logger.exception("Unexpected error with KDE")
        return False
    else:
        return True


def set_wallpaper_xfce(image_path: Path) -> bool:
    """Set wallpaper for Xfce Desktop."""
    try:
        # Get the monitor info
        result = subprocess.run(
            ["xfconf-query", "-c", "xfce4-desktop", "-l"],  # noqa: S607
            capture_output=True,
            text=True,
            check=False,
        )

        # Set wallpaper for each monitor
        for line in result.stdout.split("\n"):
            if "/backdrop/" in line and "image-path" in line:
                cmd = [
                    "xfconf-query",
                    "-c",
                    "xfce4-desktop",
                    "-p",
                    line.strip(),
                    "-s",
                    str(image_path),
                ]
                subprocess.run(cmd, check=True, capture_output=True)  # noqa: S603

    except subprocess.CalledProcessError:
        logger.exception("Error setting Xfce wallpaper:")
        return False
    except Exception:
        logger.exception("Unexpected error with Xfce")
        return False
    else:
        return True


def set_wallpaper_cinnamon(image_path: Path) -> bool:
    """Set wallpaper for Cinnamon Desktop."""
    try:
        cmd = [
            "gsettings",
            "set",
            "org.cinnamon.desktop.background",
            "picture-uri",
            f"file://{image_path}",
        ]
        subprocess.run(cmd, check=True, capture_output=True)  # noqa: S603

    except subprocess.CalledProcessError:
        logger.exception("Error setting Cinnamon wallpaper")
        return False
    except Exception:
        logger.exception("Unexpected error with Cinnamon")
        return False
    else:
        return True


def main(
    image_file: str = "./apod.jpg",
    desktop: Literal["gnome", "kde", "xfce", "cinnamon", "auto"] = "auto",
) -> int:
    """Parse arguments and set wallpaper."""
    # Validate image
    try:
        image_path = validate_image(image_file)
        logger.debug("✓ Image file validated: %s", image_path)
    except FileNotFoundError, IsADirectoryError, ValueError:
        logger.exception("✗ Validation error")
        return 1

    # Detect desktop environment
    if desktop == "auto":
        desktop = detect_desktop_environment()  # ty:ignore[invalid-assignment]
        logger.debug("✓ Detected desktop environment: %s", desktop)

    # Set wallpaper based on desktop environment
    success = False

    if desktop in {"gnome", "auto"}:
        logger.debug("→ Attempting to set GNOME wallpaper...")
        success = set_wallpaper_gnome(image_path)

    if not success and (desktop == "kde" or (desktop == "auto" and not success)):
        logger.debug("→ Attempting to set KDE wallpaper...")
        success = set_wallpaper_kde(image_path)

    if not success and (desktop == "xfce" or (desktop == "auto" and not success)):
        logger.debug("→ Attempting to set Xfce wallpaper...")
        success = set_wallpaper_xfce(image_path)

    if not success and (desktop == "cinnamon" or (desktop == "auto" and not success)):
        logger.debug("→ Attempting to set Cinnamon wallpaper...")
        success = set_wallpaper_cinnamon(image_path)

    if success:
        logger.info("✓ Wallpaper set successfully: %s", image_path.name)
        return 0
    logger.error(
        "✗ Failed to set wallpaper. Your desktop environment may not be supported."
    )
    return 1
