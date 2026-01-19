#!/usr/bin/env python3
"""WOPR Installation Script

This script checks your system for required dependencies and installs them.
Run with: python3 install.py
"""

import subprocess
import sys
from importlib.metadata import version, PackageNotFoundError


# Minimum Python version required
MIN_PYTHON = (3, 10)

# Required packages for basic functionality
REQUIRED_PACKAGES = {
    "textual": "0.50.0",
    "rich": "13.0.0",
    "python-chess": "1.10",
    "pyttsx3": "2.90",
}

# Optional packages for audio support
AUDIO_PACKAGES = {
    "pygame": "2.0.0",
}

# Alternative audio packages (if pygame not available)
AUDIO_ALT_PACKAGES = {
    "simpleaudio": "1.0.4",
}


def print_header():
    """Print the WOPR header."""
    print("\n" + "=" * 60)
    print("""
██╗    ██╗ ██████╗ ██████╗ ██████╗
██║    ██║██╔═══██╗██╔══██╗██╔══██╗
██║ █╗ ██║██║   ██║██████╔╝██████╔╝
██║███╗██║██║   ██║██╔═══╝ ██╔══██╗
╚███╔███╔╝╚██████╔╝██║     ██║  ██║
 ╚══╝╚══╝  ╚═════╝ ╚═╝     ╚═╝  ╚═╝
    """)
    print("         INSTALLATION SCRIPT")
    print("=" * 60 + "\n")


def check_python_version():
    """Check if Python version meets minimum requirements."""
    current = sys.version_info[:2]
    if current < MIN_PYTHON:
        return False, f"{current[0]}.{current[1]}", f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}+"
    return True, f"{current[0]}.{current[1]}", f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}+"


def get_installed_version(package_name):
    """Get the installed version of a package, or None if not installed."""
    try:
        return version(package_name)
    except PackageNotFoundError:
        return None


def compare_versions(installed, required):
    """Check if installed version meets required version."""
    if installed is None:
        return False

    def parse_version(v):
        return tuple(int(x) for x in v.split(".")[:3])

    try:
        return parse_version(installed) >= parse_version(required)
    except (ValueError, IndexError):
        return True  # If we can't parse, assume it's fine


def check_packages(packages):
    """Check status of packages. Returns (installed, needs_upgrade, missing)."""
    installed = {}
    needs_upgrade = {}
    missing = {}

    for package, min_version in packages.items():
        current = get_installed_version(package)
        if current is None:
            missing[package] = min_version
        elif not compare_versions(current, min_version):
            needs_upgrade[package] = (current, min_version)
        else:
            installed[package] = current

    return installed, needs_upgrade, missing


def print_status(label, packages, status_char, color_code):
    """Print package status with formatting."""
    if not packages:
        return

    print(f"\n{label}:")
    for pkg, ver in packages.items():
        if isinstance(ver, tuple):
            print(f"  {status_char} {pkg}: {ver[0]} -> {ver[1]} (upgrade needed)")
        else:
            print(f"  {status_char} {pkg}: {ver}")


def install_packages(packages):
    """Install or upgrade packages using pip."""
    if not packages:
        return True

    pkg_list = list(packages.keys())
    print(f"\nInstalling: {', '.join(pkg_list)}")

    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", *pkg_list
        ])
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    print_header()

    # Check Python version
    print("Checking Python version...")
    py_ok, py_current, py_required = check_python_version()

    if py_ok:
        print(f"  [OK] Python {py_current} (requires {py_required})")
    else:
        print(f"  [X] Python {py_current} - REQUIRES {py_required}")
        print("\nERROR: Please upgrade Python to version 3.10 or higher.")
        print("Visit https://www.python.org/downloads/")
        sys.exit(1)

    # Check required packages
    print("\nChecking required packages...")
    req_installed, req_upgrade, req_missing = check_packages(REQUIRED_PACKAGES)

    print_status("Installed", req_installed, "[OK]", "32")
    print_status("Needs Upgrade", req_upgrade, "[!]", "33")
    print_status("Missing", req_missing, "[X]", "31")

    # Check audio packages
    print("\nChecking audio packages (optional)...")
    audio_installed, audio_upgrade, audio_missing = check_packages(AUDIO_PACKAGES)

    # Check alternative audio if primary not available
    has_audio = bool(audio_installed) or bool(audio_upgrade)
    if not has_audio:
        alt_installed, alt_upgrade, alt_missing = check_packages(AUDIO_ALT_PACKAGES)
        has_audio = bool(alt_installed) or bool(alt_upgrade)
        if alt_installed:
            audio_installed.update(alt_installed)
        if alt_upgrade:
            audio_upgrade.update(alt_upgrade)

    if audio_installed:
        print_status("Installed", audio_installed, "[OK]", "32")
    if audio_upgrade:
        print_status("Needs Upgrade", audio_upgrade, "[!]", "33")
    if not has_audio:
        print("  [!] No audio package found (pygame or simpleaudio)")
        print("      Sound effects will be disabled without audio support.")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    to_install = {**req_missing, **{k: v[1] for k, v in req_upgrade.items()}}

    if not to_install and has_audio:
        print("\n[OK] All dependencies are installed!")
        print("\nRun WOPR with: python3 -m wopr")
        print("=" * 60)
        return

    if to_install:
        print(f"\nRequired packages to install/upgrade: {len(to_install)}")
        for pkg in to_install:
            print(f"  - {pkg}")

    if not has_audio:
        print("\nOptional: Install pygame for sound effects")

    # Ask user
    print("\n" + "-" * 60)

    if to_install:
        response = input("\nInstall required packages now? [Y/n]: ").strip().lower()
        if response in ("", "y", "yes"):
            print()
            if install_packages(to_install):
                print("\n[OK] Required packages installed successfully!")
            else:
                print("\n[!] Some packages failed to install.")
                print("    Try running: pip3 install textual rich python-chess pyttsx3")
                sys.exit(1)
        else:
            print("\nInstallation cancelled.")
            print("To install manually, run:")
            print("  pip3 install textual rich python-chess pyttsx3")
            sys.exit(0)

    if not has_audio:
        response = input("\nInstall pygame for sound effects? [Y/n]: ").strip().lower()
        if response in ("", "y", "yes"):
            if install_packages({"pygame": "2.0.0"}):
                print("\n[OK] Audio support installed!")
            else:
                print("\n[!] pygame installation failed.")
                print("    WOPR will run without sound effects.")

    # Final message
    print("\n" + "=" * 60)
    print("INSTALLATION COMPLETE")
    print("=" * 60)
    print("\nRun WOPR with: python3 -m wopr")
    print("\nFor the full experience, try:")
    print("  python3 -m wopr")
    print("\nFor quick access (skip intro):")
    print("  python3 -m wopr --fast --skip-intro")
    print("\nEnjoy! Remember: the only winning move is not to play.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
