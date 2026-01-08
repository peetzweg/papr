#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
from pathlib import Path
from watchfiles import watch

def main():
    """
    Dev mode: Watch for file changes and rerun papr command.
    Usage: papr-dev [same arguments as papr]
    """
    # Get the papr source directory
    papr_dir = Path(__file__).parent

    # Get the command arguments (everything after papr-dev)
    papr_args = sys.argv[1:]

    if not papr_args:
        print("Error: Please provide papr arguments")
        print("Usage: papr-dev [papr arguments]")
        print("Example: papr-dev -y 2023 -m 2 -f='Avenir Next' -p A3 oneyear")
        sys.exit(1)

    # Build the command to run
    cmd = [sys.executable, "-m", "papr.papr"] + papr_args

    print(f"🔧 Dev mode started")
    print(f"📂 Watching: {papr_dir}")
    print(f"🚀 Running: papr {' '.join(papr_args)}")
    print("=" * 60)

    def run_command():
        """Run the papr command"""
        try:
            result = subprocess.run(cmd, check=False)
            if result.returncode == 0:
                print("\n✅ Command completed successfully")
            else:
                print(f"\n❌ Command failed with exit code {result.returncode}")
        except Exception as e:
            print(f"\n❌ Error running command: {e}")

    # Run once initially
    run_command()

    print("\n👀 Watching for changes... (Press Ctrl+C to stop)")
    print("=" * 60)

    # Watch for changes and rerun
    try:
        for changes in watch(papr_dir, watch_filter=lambda change, path: path.endswith('.py')):
            # Clear screen for clean output
            os.system('clear' if os.name == 'posix' else 'cls')

            print("🔄 Files changed, rerunning...")
            for change_type, path in changes:
                print(f"  {change_type.name}: {Path(path).relative_to(papr_dir.parent)}")
            print("=" * 60)

            run_command()

            print("\n👀 Watching for changes... (Press Ctrl+C to stop)")
            print("=" * 60)
    except KeyboardInterrupt:
        print("\n\n👋 Dev mode stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()
