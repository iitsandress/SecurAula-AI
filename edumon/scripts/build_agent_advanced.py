#!/usr/bin/env python3
"""
Advanced agent builder script
Builds EduMon agent for multiple platforms with optimizations
"""
import os
import sys
import shutil
import subprocess
import platform
import argparse
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result


def get_version():
    """Get version from pyproject.toml"""
    try:
        import tomllib
        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
        return data["project"]["version"]
    except:
        return "2.0.0"


def build_agent(args):
    """Build the agent executable"""
    agent_dir = Path("agent")
    if not agent_dir.exists():
        print("Error: agent directory not found")
        return False
    
    # Change to agent directory
    os.chdir(agent_dir)
    
    # Install dependencies
    print("Installing dependencies...")
    run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    run_command([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Prepare build
    dist_dir = Path("dist")
    build_dir = Path("build")
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # PyInstaller options
    pyinstaller_args = [
        sys.executable, "-m", "PyInstaller",
        "--name", "EduMonAgent",
        "--onedir" if not args.onefile else "--onefile",
        "--windowed" if args.windowed else "--console",
        "--clean",
        "--noconfirm",
    ]
    
    # Add icon if available
    icon_path = Path("assets/icon.ico")
    if icon_path.exists():
        pyinstaller_args.extend(["--icon", str(icon_path)])
    
    # Add hidden imports
    hidden_imports = [
        "PyQt6.QtCore",
        "PyQt6.QtWidgets", 
        "PyQt6.QtGui",
        "psutil",
        "requests",
        "json",
        "sqlite3"
    ]
    
    for imp in hidden_imports:
        pyinstaller_args.extend(["--hidden-import", imp])
    
    # Add data files
    data_files = [
        ("config.example.json", "."),
        ("README_AGENT.md", "."),
    ]
    
    for src, dst in data_files:
        if Path(src).exists():
            pyinstaller_args.extend(["--add-data", f"{src}{os.pathsep}{dst}"])
    
    # Exclude unnecessary modules
    excludes = [
        "tkinter",
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",
        "PIL",
        "cv2"
    ]
    
    for exc in excludes:
        pyinstaller_args.extend(["--exclude-module", exc])
    
    # Main script
    pyinstaller_args.append("main.py")
    
    # Build
    print("Building executable...")
    try:
        run_command(pyinstaller_args)
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False
    
    # Post-build steps
    if args.onefile:
        exe_path = dist_dir / "EduMonAgent.exe" if platform.system() == "Windows" else dist_dir / "EduMonAgent"
    else:
        exe_dir = dist_dir / "EduMonAgent"
        exe_path = exe_dir / ("EduMonAgent.exe" if platform.system() == "Windows" else "EduMonAgent")
        
        # Copy additional files to dist directory
        if exe_dir.exists():
            # Copy config example
            if Path("config.example.json").exists():
                shutil.copy2("config.example.json", exe_dir)
            
            # Copy README
            if Path("README_AGENT.md").exists():
                shutil.copy2("README_AGENT.md", exe_dir)
            
            # Create logs directory
            (exe_dir / "logs").mkdir(exist_ok=True)
    
    if exe_path.exists():
        print(f"✓ Build successful: {exe_path}")
        print(f"  Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
        return True
    else:
        print("✗ Build failed: executable not found")
        return False


def create_installer(args):
    """Create installer package"""
    if platform.system() == "Windows":
        return create_windows_installer(args)
    elif platform.system() == "Darwin":
        return create_macos_installer(args)
    else:
        return create_linux_package(args)


def create_windows_installer(args):
    """Create Windows installer using NSIS"""
    try:
        # Check if NSIS is available
        run_command(["makensis", "/VERSION"])
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("NSIS not found. Skipping installer creation.")
        return False
    
    # Create NSIS script
    nsis_script = f"""
!define APP_NAME "EduMon Agent"
!define APP_VERSION "{get_version()}"
!define APP_PUBLISHER "EduMon Team"
!define APP_EXE "EduMonAgent.exe"

Name "${{APP_NAME}}"
OutFile "EduMonAgent-Setup-${{APP_VERSION}}.exe"
InstallDir "$PROGRAMFILES\\EduMon Agent"

Page directory
Page instfiles

Section "Install"
    SetOutPath $INSTDIR
    File /r "dist\\EduMonAgent\\*"
    
    CreateDirectory "$SMPROGRAMS\\EduMon"
    CreateShortCut "$SMPROGRAMS\\EduMon\\EduMon Agent.lnk" "$INSTDIR\\${{APP_EXE}}"
    CreateShortCut "$DESKTOP\\EduMon Agent.lnk" "$INSTDIR\\${{APP_EXE}}"
    
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\*.*"
    RMDir /r "$INSTDIR"
    Delete "$SMPROGRAMS\\EduMon\\*.*"
    RMDir "$SMPROGRAMS\\EduMon"
    Delete "$DESKTOP\\EduMon Agent.lnk"
SectionEnd
"""
    
    with open("installer.nsi", "w") as f:
        f.write(nsis_script)
    
    try:
        run_command(["makensis", "installer.nsi"])
        print("✓ Windows installer created")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to create Windows installer")
        return False


def create_macos_installer(args):
    """Create macOS app bundle and DMG"""
    print("Creating macOS app bundle...")
    
    app_name = "EduMon Agent.app"
    app_dir = Path("dist") / app_name
    
    if app_dir.exists():
        shutil.rmtree(app_dir)
    
    # Create app bundle structure
    contents_dir = app_dir / "Contents"
    macos_dir = contents_dir / "MacOS"
    resources_dir = contents_dir / "Resources"
    
    macos_dir.mkdir(parents=True)
    resources_dir.mkdir(parents=True)
    
    # Copy executable
    exe_src = Path("dist/EduMonAgent/EduMonAgent")
    exe_dst = macos_dir / "EduMonAgent"
    shutil.copy2(exe_src, exe_dst)
    
    # Make executable
    os.chmod(exe_dst, 0o755)
    
    # Create Info.plist
    info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>EduMon Agent</string>
    <key>CFBundleDisplayName</key>
    <string>EduMon Agent</string>
    <key>CFBundleIdentifier</key>
    <string>com.edumon.agent</string>
    <key>CFBundleVersion</key>
    <string>{get_version()}</string>
    <key>CFBundleExecutable</key>
    <string>EduMonAgent</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>"""
    
    with open(contents_dir / "Info.plist", "w") as f:
        f.write(info_plist)
    
    print(f"✓ macOS app bundle created: {app_dir}")
    return True


def create_linux_package(args):
    """Create Linux package (AppImage or DEB)"""
    print("Creating Linux package...")
    
    # For now, just create a tar.gz
    import tarfile
    
    version = get_version()
    archive_name = f"edumon-agent-{version}-linux.tar.gz"
    
    with tarfile.open(archive_name, "w:gz") as tar:
        tar.add("dist/EduMonAgent", arcname="edumon-agent")
    
    print(f"✓ Linux package created: {archive_name}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Build EduMon Agent")
    parser.add_argument("--onefile", action="store_true", help="Create single file executable")
    parser.add_argument("--windowed", action="store_true", help="Create windowed application (no console)")
    parser.add_argument("--installer", action="store_true", help="Create installer package")
    parser.add_argument("--clean", action="store_true", help="Clean build directories first")
    
    args = parser.parse_args()
    
    # Change to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    print(f"Building EduMon Agent v{get_version()}")
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"Python: {sys.version}")
    
    # Clean if requested
    if args.clean:
        print("Cleaning build directories...")
        for dir_name in ["dist", "build"]:
            dir_path = Path("agent") / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
    
    # Build agent
    if not build_agent(args):
        return 1
    
    # Create installer if requested
    if args.installer:
        if not create_installer(args):
            print("Warning: Installer creation failed")
    
    print("\n✓ Build completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())