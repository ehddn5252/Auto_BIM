"""Run all spike scripts, print RESULT lines (full evidence: run each script individually)."""
import subprocess, sys
from pathlib import Path
here = Path(__file__).parent
for f in sorted(here.glob("[a-f]_*.py")):
    r = subprocess.run([sys.executable, str(f)], cwd=here, capture_output=True, text=True, encoding="utf-8")
    line = [l for l in r.stdout.splitlines() if l.startswith("RESULT")]
    print(f.name, "rc=", r.returncode, line[-1][:160] if line else r.stderr[-300:])
