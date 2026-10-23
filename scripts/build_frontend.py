"""Build the browser application before packaging the Vercel FastAPI function."""

import os
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parent.parent
env = {**os.environ, "VITE_API_BASE_URL": "/api"}
npm = "npm.cmd" if os.name == "nt" else "npm"
for command in ([npm, "ci"], [npm, "run", "build"]):
    subprocess.run(command, cwd=root / "frontend", env=env, check=True)
