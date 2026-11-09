"""(f) Re-find the original entity from a (file, insert-handle-path, entity handle) record.
Also checks: handles survive save/load, virtual entities lose handles, paper-space entities."""
import ezdxf
from common import roundtrip, result

doc = ezdxf.new("R2018")
doc.header["$INSUNITS"] = 4
leaf = doc.blocks.new("LAMP"); leaf.add_circle((0, 0), 100)
mid = doc.blocks.new("ROOM"); mid.add_blockref("LAMP", (500, 500))
mid.add_blockref("LAMP", (900, 500))
msp = doc.modelspace()
msp.add_blockref("ROOM", (0, 0)); msp.add_blockref("ROOM", (5000, 0))
psp = doc.layout("Layout1") if "Layout1" in doc.layouts else doc.layouts.new("Layout1")
psp.add_blockref("LAMP", (10, 10))
orig_handles = sorted(e.dxf.handle for e in msp.query("INSERT"))

path, d2 = roundtrip(doc, "trace.dxf")
print("handles stable across save/load:", orig_handles == sorted(e.dxf.handle for e in d2.modelspace().query("INSERT")))

# Parser-style records: one per instance, with insert_path of handles
records = []
def walk(entities, space, path=()):
    for e in entities:
        if e.dxftype() == "INSERT":
            if e.dxf.name == "LAMP":
                records.append({"space": space, "block": "LAMP", "handle": e.dxf.handle,
                                "insert_path": list(path), "owner": e.dxf.owner})
            walk(d2.blocks.get(e.dxf.name), space, path + (e.dxf.handle,))
walk(d2.modelspace(), "Model")
walk(d2.layout("Layout1"), "Paper:Layout1")
print("records:", len(records))
# Re-lookup everything from the stored identifiers only
bad = 0
for r in records:
    ent = d2.entitydb.get(r["handle"])
    chain = [d2.entitydb.get(h) for h in r["insert_path"]]
    ok = ent is not None and ent.dxftype() == "INSERT" and ent.dxf.name == r["block"] and all(c is not None and c.dxftype() == "INSERT" for c in chain)
    # the entity's owner block-record tells which layout / block it lives in
    owner = d2.entitydb.get(ent.dxf.owner) if ent is not None else None
    r["owner_name"] = owner.dxf.name if owner is not None else None
    # chain consistency: the owner of child == block named by the last insert in path
    if r["insert_path"]:
        parent_block = chain[-1].dxf.name
        ok = ok and r["owner_name"] == parent_block
    bad += (not ok)
    print("  ", r, "OK" if ok else "BAD")

# virtual entities: no stable handle -> cannot be used as evidence
v = list(d2.modelspace().query("INSERT")[0].virtual_entities())
print("virtual_entities handles:", [x.dxf.handle for x in v], "(None => not traceable; walk INSERTs instead)")
vs = [x.source_of_copy for x in v] if hasattr(v[0], "source_of_copy") else None
print("virtual entity source_of_copy handles:", [getattr(s, 'dxf', None) and s.dxf.handle for s in vs] if vs else vs)

assert len(records) == 5 and bad == 0
result("f", "SUCCESS", "entitydb.get(handle) re-finds the INSERT and every INSERT in insert_path; handles stable "
       "across save/load; handle is unique per DOCUMENT (same block-def entity is shared by all instances, so "
       "instance identity = insert_path + handle, NOT handle alone); virtual_entities() yields handle=None")
