#!/usr/bin/env python
"""Startup script that runs migrations before starting the FastAPI app."""

import subprocess
import sys

def main():
    print("Running database migrations...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Migration failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    print("Migrations completed successfully")
    print(result.stdout)

    print("Starting uvicorn server...")
    subprocess.run([
        "uvicorn",
        "main:app",
        "--host", "0.0.0.0",
        "--port", "8000"
    ])

if __name__ == "__main__":
    main()
