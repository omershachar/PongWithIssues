"""
Build script for creating distributable PongWithIssues executables.
Uses PyInstaller to create standalone executables for Windows, macOS, and Linux.

Usage:
    python scripts/build.py [--onefile] [--console]

Requirements:
    pip install pyinstaller

Options:
    --onefile   Create a single executable file (slower startup, easier distribution)
    --console   Show console window (useful for debugging)
"""
import os
import sys
import shutil
import subprocess
import argparse

# Project paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LAUNCHER = os.path.join(PROJECT_ROOT, 'launcher.py')
ASSETS_DIR = os.path.join(PROJECT_ROOT, 'assets')
PONG_DIR = os.path.join(PROJECT_ROOT, 'pong')
VERSIONS_DIR = os.path.join(PROJECT_ROOT, 'versions')
DIST_DIR = os.path.join(PROJECT_ROOT, 'dist')
BUILD_DIR = os.path.join(PROJECT_ROOT, 'build')

# App info
APP_NAME = 'PongWithIssues'
ICON_PATH = os.path.join(ASSETS_DIR, 'icon.png')  # Will be converted if needed


def check_dependencies():
    """Check if required build tools are installed."""
    try:
        import PyInstaller
        print(f'PyInstaller version: {PyInstaller.__version__}')
        return True
    except ImportError:
        print('ERROR: PyInstaller not found.')
        print('Install it with: pip install pyinstaller')
        return False


def generate_icons():
    """Generate icons if they don't exist."""
    if not os.path.exists(ICON_PATH):
        print('Generating icons...')
        icon_script = os.path.join(PROJECT_ROOT, 'scripts', 'generate_icon.py')
        subprocess.run([sys.executable, icon_script], check=True)


def get_data_files():
    """Get list of data files to include in the build."""
    data_files = []

    # Include pong module (fonts, etc.)
    fonts_dir = os.path.join(PONG_DIR, 'FONTS')
    if os.path.exists(fonts_dir):
        data_files.append((fonts_dir, 'pong/FONTS'))

    # Include assets
    if os.path.exists(ASSETS_DIR):
        data_files.append((ASSETS_DIR, 'assets'))

    return data_files


def build(onefile=False, console=False):
    """Build the executable."""
    if not check_dependencies():
        return False

    generate_icons()

    # Clean previous builds
    for d in [DIST_DIR, BUILD_DIR]:
        if os.path.exists(d):
            print(f'Cleaning {d}...')
            shutil.rmtree(d)

    # Build PyInstaller command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name', APP_NAME,
        '--clean',
    ]

    # One file or directory
    if onefile:
        cmd.append('--onefile')
    else:
        cmd.append('--onedir')

    # Console or windowed
    if not console:
        cmd.append('--windowed')  # No console window

    # Add icon if it exists
    ico_path = os.path.join(ASSETS_DIR, 'icon.ico')
    if os.path.exists(ico_path):
        cmd.extend(['--icon', ico_path])
    elif os.path.exists(ICON_PATH):
        # Try to use PNG (works on some platforms)
        cmd.extend(['--icon', ICON_PATH])

    # Add data files
    for src, dest in get_data_files():
        cmd.extend(['--add-data', f'{src}{os.pathsep}{dest}'])

    # Hidden imports for pygame
    cmd.extend([
        '--hidden-import', 'pygame',
        '--hidden-import', 'numpy',
    ])

    # Add the launcher script
    cmd.append(LAUNCHER)

    print(f'Running: {" ".join(cmd)}')
    print()

    # Run PyInstaller
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)

    if result.returncode == 0:
        print()
        print('=' * 60)
        print('BUILD SUCCESSFUL!')
        print('=' * 60)
        if onefile:
            print(f'Executable: {os.path.join(DIST_DIR, APP_NAME)}')
        else:
            print(f'Distribution folder: {os.path.join(DIST_DIR, APP_NAME)}')
        print()
        print('To run the game:')
        if sys.platform == 'win32':
            print(f'  dist\\{APP_NAME}\\{APP_NAME}.exe')
        else:
            print(f'  ./dist/{APP_NAME}/{APP_NAME}')
        return True
    else:
        print()
        print('BUILD FAILED!')
        return False


def main():
    parser = argparse.ArgumentParser(description='Build PongWithIssues executable')
    parser.add_argument('--onefile', action='store_true',
                       help='Create a single executable file')
    parser.add_argument('--console', action='store_true',
                       help='Show console window (for debugging)')
    args = parser.parse_args()

    success = build(onefile=args.onefile, console=args.console)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
