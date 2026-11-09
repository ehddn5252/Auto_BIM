"""(d) Can ACIS / PROXY / UNDERLAY / IMAGE / XREF / unknown entities be synthesised,
and do they survive save -> load with a recognisable type?"""
import collections
import re
import tempfile
from pathlib import Path
import ezdxf
from common import roundtrip, result

doc = ezdxf.new("R2010")  # SAT (text) ACIS; R2013+ SAB goes to ACDSDATA, tested separately in comments
doc.header["$INSUNITS"] = 4
msp = doc.modelspace()
status = {}

def attempt(label, fn):
    try:
        e = fn()
        status[label] = ("created", e.dxftype() if hasattr(e, "dxftype") else str(e))
    except Exception as ex:  # report, never hide
        status[label] = ("FAILED", f"{type(ex).__name__}: {ex}")

# Empty ACIS shells are silently NOT written by ezdxf (verified below) -> need payload.
_s = msp.add_3dsolid(); _s.sat = ["400 0 1 0", "FAKE-SAT-PAYLOAD-NOT-REAL-GEOMETRY"]
doc_empty = ezdxf.new("R2010"); _e = doc_empty.modelspace().add_3dsolid()   # no payload
_pe, _de = roundtrip(doc_empty, "empty_acis.dxf")
print("EMPTY 3DSOLID survives save/load?", [e.dxftype() for e in _de.modelspace()] or "NO (dropped)")
attempt("3DSOLID", lambda: _s)
def _reg():
    r = msp.add_region(); r.sat = ["400 0 1 0", "FAKE"]; return r
def _body():
    b = msp.add_body(); b.sat = ["400 0 1 0", "FAKE"]; return b
attempt("REGION", _reg)
attempt("BODY", _body)
def _proxy():
    from ezdxf.lldxf.tags import Tags
    from ezdxf.lldxf.types import DXFTag
    e = msp.new_entity("ACAD_PROXY_ENTITY", {"layer": "E-PROXY"})
    e.acdb_proxy_entity = Tags([DXFTag(100, "AcDbProxyEntity"), DXFTag(90, 498), DXFTag(91, 500),
                                DXFTag(92, 0), DXFTag(93, 0), DXFTag(95, 0), DXFTag(70, 1)])
    return e
attempt("PROXY(ACAD_PROXY_ENTITY)", _proxy)
def _ul():
    d = doc.add_underlay_def("fake_plan.pdf", name="1")
    return msp.add_underlay(d, insert=(0, 0, 0))
attempt("UNDERLAY(PDF)", _ul)
def _img():
    d = doc.add_image_def("fake.png", (100, 100))
    return msp.add_image(d, insert=(0, 0), size_in_units=(10, 10))
attempt("IMAGE", _img)
def _xref():
    doc.add_xref_def("missing_ref.dxf", "XR_PLAN")
    return msp.add_blockref("XR_PLAN", (0, 0))
attempt("XREF def+INSERT", _xref)
doc.add_xref_def("overlay_ref.dxf", "XR_OVL", flags=ezdxf.lldxf.const.BLK_XREF_OVERLAY | ezdxf.lldxf.const.BLK_EXTERNAL)

path, d2 = roundtrip(doc, "unsupported.dxf")
cnt = collections.Counter(e.dxftype() for e in d2.modelspace())
print("creation status:")
for k, v in status.items():
    print("  ", k, v)
print("msp types after reload:", dict(cnt))
print("xref blocks after reload:", [(b.name, b.block.is_xref, b.block.is_xref_overlay, b.block.dxf.get("xref_path")) for b in d2.blocks if b.block.is_xref])
print("XREF insert.is_xref():", [i.is_xref() for i in d2.modelspace().query("INSERT")])

# Unknown entity type: rewrite one entity's type in the DXF text and reload.
txt = Path(path).read_text(encoding="utf-8", errors="replace")
d = Path(tempfile.mkdtemp(prefix="ezdxf_spike_")); p2 = d / "unknown.dxf"
patched = txt.replace("\n3DSOLID\n", "\nFOOBAR_THING\n", 1)
p2.write_text(patched, encoding="utf-8")
d3 = ezdxf.readfile(p2)
unk = [e for e in d3.modelspace() if e.dxftype() == "FOOBAR_THING"]
print("types in patched file:", sorted({e.dxftype() for e in d3.modelspace()}))
print("unknown entity reloaded as:", [(e.dxftype(), type(e).__name__, e.dxf.handle) for e in unk])

# Auditor findings for the file with proxy/underlay
aud = d2.audit()
print("audit errors:", [str(e.message) for e in aud.errors][:5], "fixes:", len(aud.fixes))

ok = {k for k, v in status.items() if v[0] == "created"}
failed = sorted(set(status) - ok)
types_back = set(cnt)
print("types present after reload:", sorted(types_back))
result("d", "SUCCESS" if not failed else "PARTIAL",
       f"created={sorted(ok)} failed={failed}; ACIS bodies are empty shells (no real SAT/SAB geometry) "
       "- enough to test warning codes, not geometry; PROXY is a stub (no real graphics); "
       "XREF target file deliberately absent")
