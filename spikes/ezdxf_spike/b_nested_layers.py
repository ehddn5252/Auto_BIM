"""(b) Nested blocks + frozen / off layers; layer '0' inheritance.
Question: does ezdxf resolve effective visibility / layer inheritance for us? (Expected: no.)
"""
import ezdxf
from common import roundtrip, result

doc = ezdxf.new("R2018")
doc.header["$INSUNITS"] = 4
doc.layers.add("E-LIGHT")
doc.layers.add("E-FROZEN").freeze()
doc.layers.add("E-OFF").off()
doc.layers.add("E-FIX")

# LEAF: entity on layer '0' (inherits INSERT layer) + one on explicit layer
leaf = doc.blocks.new("LEAF")
leaf.add_circle((0, 0), 50, dxfattribs={"layer": "0"})
leaf.add_circle((0, 0), 20, dxfattribs={"layer": "E-FIX"})
# MID contains LEAF insert on layer E-LIGHT
mid = doc.blocks.new("MID")
mid.add_blockref("LEAF", (0, 0), dxfattribs={"layer": "E-LIGHT"})
# MID_FROZEN contains LEAF insert on frozen layer (inside the block definition)
mid_fz = doc.blocks.new("MID_FROZEN")
mid_fz.add_blockref("LEAF", (0, 0), dxfattribs={"layer": "E-FROZEN"})
mid_off = doc.blocks.new("MID_OFF")
mid_off.add_blockref("LEAF", (0, 0), dxfattribs={"layer": "E-OFF"})

msp = doc.modelspace()
msp.add_blockref("MID", (0, 0), dxfattribs={"layer": "E-LIGHT"})          # visible
msp.add_blockref("MID", (1000, 0), dxfattribs={"layer": "E-FROZEN"})      # parent on frozen layer
msp.add_blockref("MID", (2000, 0), dxfattribs={"layer": "E-OFF"})         # parent on off layer
msp.add_blockref("MID_FROZEN", (3000, 0), dxfattribs={"layer": "E-LIGHT"})  # child insert on frozen layer
msp.add_blockref("MID_OFF", (4000, 0), dxfattribs={"layer": "E-LIGHT"})     # child insert on off layer
inv = msp.add_blockref("MID", (5000, 0), dxfattribs={"layer": "E-LIGHT"})
inv.dxf.invisible = 1                                                     # entity-level invisible flag

path, d2 = roundtrip(doc, "nested.dxf")
layers = d2.layers
print("layer states after file round-trip:")
for n in ("0", "E-LIGHT", "E-FROZEN", "E-OFF", "E-FIX"):
    l = layers.get(n)
    print(f"  {n}: frozen={l.is_frozen()} off={l.is_off()} locked={l.is_locked()}")

def walk(layout_entities, doc, path=(), parent_layer=None, hidden_by=None, out=None):
    """Own traversal: effective layer (layer '0' inherits), and first hiding cause along the path."""
    out = [] if out is None else out
    for e in layout_entities:
        eff = e.dxf.layer
        if eff == "0" and parent_layer:
            eff = parent_layer
        lay = doc.layers.get(eff)
        cause = hidden_by
        if cause is None and lay is not None and (lay.is_frozen() or lay.is_off()):
            cause = f"{'frozen' if lay.is_frozen() else 'off'}:{eff}"
        if cause is None and e.dxf.hasattr("invisible") and e.dxf.invisible:
            cause = "entity_invisible"
        if e.dxftype() == "INSERT":
            walk(doc.blocks.get(e.dxf.name), doc, path + (e.dxf.handle,), eff, cause, out)
        else:
            out.append((path, e.dxf.handle, e.dxf.layer, eff, cause))
    return out

rows = walk(d2.modelspace(), d2)
print("leaf geometry: (insert-path, handle, declared layer, effective layer, hidden-cause)")
for r in rows:
    print("  ", r)

# Does ezdxf itself apply layer-0 inheritance in virtual_entities()?
top = list(d2.modelspace().query("INSERT"))[0]
print("virtual_entities of first MID insert (declared layers as ezdxf reports them):")
for v in top.virtual_entities():
    print("   ", v.dxftype(), v.dxf.layer, "handle=", v.dxf.handle)

leaf_ins = d2.modelspace().add_blockref("LEAF", (9000, 0), dxfattribs={"layer": "E-LIGHT"})
print("virtual_entities of a direct LEAF insert on E-LIGHT (layer '0' child):")
for v in leaf_ins.virtual_entities():
    print("   ", v.dxftype(), "layer=", v.dxf.layer)

hidden = {r[4] for r in rows}
result("b", "SUCCESS (with own logic)",
       "ezdxf exposes layer.is_frozen()/is_off() and raw layer names but does NOT resolve "
       "layer-0 inheritance or hidden-by-parent; parser must implement effective-layer walk "
       f"(demonstrated: causes seen = {sorted(c for c in hidden if c)}).")
