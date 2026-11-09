"""Spike helpers. SPIKE CODE ONLY (D-012) - not part of src/."""
import tempfile
from pathlib import Path

import ezdxf


def roundtrip(doc, name="spike.dxf"):
    """Save to a temp dir and re-read from disk (proves file-level behaviour)."""
    d = Path(tempfile.mkdtemp(prefix="ezdxf_spike_"))
    p = d / name
    doc.saveas(p)
    return p, ezdxf.readfile(p)


def result(item, status, note=""):
    print(f"RESULT {item}: {status} {note}".rstrip())
