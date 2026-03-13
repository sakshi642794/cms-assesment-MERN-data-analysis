import subprocess
import sys


SCRIPTS = [
    "scripts/extract_worldbank.py",
    "scripts/extract_who_gho.py",
    "scripts/transform_integration.py",
    "scripts/load_sqlite.py",
]


def main() -> None:
    for script in SCRIPTS:
        result = subprocess.run([sys.executable, script], check=False)
        if result.returncode != 0:
            raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
