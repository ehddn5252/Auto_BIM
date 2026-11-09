"""(a) Can the original name of a dynamic block be recovered from a *U anonymous block?

Real AutoCAD files cannot be used (no real drawings). We synthesise the markers that
ezdxf's own reader (ezdxf.dynblkhelper) documents, i.e.:
  - dynamic block DEFINITION block_record has XDATA 'AcDbDynamicBlockGUID'
  - anonymous '*Un' block_record has XDATA 'AcDbBlockRepBTag' with (1005, <handle of definition record>)
Caveat: these markers are produced by us, so this proves the READ PATH works, not that
real AutoCAD output has exactly this shape.
"""
import ezdxf
from ezdxf import dynblkhelper as dbh
from common import roundtrip, result

doc = ezdxf.new("R2018")
doc.header["$INSUNITS"] = 4
for appid in (dbh.AcDbDynamicBlockGUID, dbh.AcDbBlockRepBTag, "AcDbDynamicBlockTrueName"):
    if appid not in doc.appids:
        doc.appids.add(appid)

# dynamic block definition
dyn = doc.blocks.new("LIGHT_DYN_A")
dyn.add_circle((0, 0), 100)
dyn.block_record.set_xdata(dbh.AcDbDynamicBlockGUID, [(1000, "{11111111-2222-3333-4444-555555555555}")])
def_handle = dyn.block_record.dxf.handle

# resolvable anonymous block (as produced when a dynamic block is modified in a drawing)
u1 = doc.blocks.new_anonymous_block("U")
u1.add_circle((0, 0), 120)
u1.block_record.set_xdata(dbh.AcDbBlockRepBTag, [(1005, def_handle)])
# alternative marker some tools use: true name stored as plain string xdata
u1.block_record.set_xdata("AcDbDynamicBlockTrueName", [(1000, "LIGHT_DYN_A")])

# unresolvable anonymous block: tag missing (e.g. definition purged / stripped by a converter)
u2 = doc.blocks.new_anonymous_block("U")
u2.add_circle((0, 0), 130)
# unresolvable: tag points to a handle that does not exist
u3 = doc.blocks.new_anonymous_block("U")
u3.add_circle((0, 0), 140)
u3.block_record.set_xdata(dbh.AcDbBlockRepBTag, [(1005, "FFFF")])

msp = doc.modelspace()
for i, blk in enumerate([dyn, u1, u2, u3]):
    msp.add_blockref(blk.name, (i * 1000, 0))

path, doc2 = roundtrip(doc, "dyn.dxf")
print("file:", path)
for ins in doc2.modelspace().query("INSERT"):
    name = ins.dxf.name
    blk = doc2.blocks.get(name)
    d = dbh.get_dynamic_block_definition(ins, doc2)
    br = blk.block_record
    true_name = None
    if br.has_xdata("AcDbDynamicBlockTrueName"):
        true_name = br.get_xdata("AcDbDynamicBlockTrueName").get_first_value(1000)
    print(f"INSERT {ins.dxf.handle} name={name!r} anonymous={blk.block.is_anonymous} "
          f"is_dyn_def={dbh.is_dynamic_block_definition(br)} "
          f"resolved_def={d.name if d else None!r} trueName_xdata={true_name!r}")

# extension dictionary route: ezdxf can read/write one, real AutoCAD stores ACAD_ENHANCEDBLOCK there.
print("block_record.has_extension_dict (synthetic, none created):", u1.block_record.has_extension_dict)
print("AcDbDynamicBlockPurgePreventer: no ezdxf support; only appears as a REAL-FILE xdata/appid,"
      " cannot be exercised without a real AutoCAD file ->", "UNVERIFIED")

resolved = [i for i in doc2.modelspace().query("INSERT")
            if dbh.get_dynamic_block_definition(i, doc2) is not None]
names = [dbh.get_dynamic_block_definition(i, doc2).name for i in resolved]
ok = names.count("LIGHT_DYN_A") == 2 and len(resolved) == 2   # dyn itself + u1
result("a", "PARTIAL", f"resolved {len(resolved)}/4 inserts via AcDbBlockRepBTag -> {names}; "
       "unresolvable *U (no tag / dangling tag) correctly return None (-> DYNAMIC_UNRESOLVED). "
       "Real-AutoCAD marker shape UNVERIFIED (synthetic markers).")
assert ok
