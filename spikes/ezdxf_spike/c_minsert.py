"""(c) MINSERT expansion."""
import math
import ezdxf
from common import roundtrip, result

doc = ezdxf.new("R2018")
doc.header["$INSUNITS"] = 4
b = doc.blocks.new("SOCKET")
b.add_circle((0, 0), 30)
msp = doc.modelspace()
m1 = msp.add_blockref("SOCKET", (0, 0), dxfattribs={
    "row_count": 3, "column_count": 4, "row_spacing": 500, "column_spacing": 800})
m2 = msp.add_blockref("SOCKET", (0, 5000), dxfattribs={   # rotated array: grid rotates with insert
    "row_count": 3, "column_count": 4, "row_spacing": 500, "column_spacing": 800, "rotation": 90})
# TRAP: counts set but spacing 0 -> ezdxf mcount (and AutoCAD) treat as 1 in that direction
m3 = msp.add_blockref("SOCKET", (0, 9000), dxfattribs={
    "row_count": 3, "column_count": 4, "row_spacing": 0, "column_spacing": 800})
# plain INSERT
msp.add_blockref("SOCKET", (0, 12000))

path, d2 = roundtrip(doc, "minsert.dxf")
total = 0
for ins in d2.modelspace().query("INSERT"):
    pts = [tuple(round(c, 3) for c in v.dxf.insert) for v in ins.multi_insert()]
    print(f"INSERT {ins.dxf.handle} rows={ins.dxf.row_count} cols={ins.dxf.column_count} "
          f"row_sp={ins.dxf.row_spacing} col_sp={ins.dxf.column_spacing} mcount={ins.mcount} "
          f"expanded={len(pts)}")
    print("   first/last:", pts[0], pts[-1])
    total += len(pts)
print("total instances:", total)
exp = 12 + 12 + 4 + 1
print("naive INSERT count:", len(list(d2.modelspace().query('INSERT'))), "(row*col would say 12+12+12+1=37)")
assert total == exp
# rotation check: first row of rotated array runs along +Y
r = [v.dxf.insert for v in list(d2.modelspace().query("INSERT"))[1].multi_insert()]
assert math.isclose(r[1].x, 0, abs_tol=1e-6) and math.isclose(abs(r[1].y - 5000), 800, abs_tol=1e-6), r[:2]
result("c", "SUCCESS", f"MINSERT 3x4 -> 12 via Insert.multi_insert(); rotated grid correct; "
       "trap: row_spacing 0 collapses that direction (3x4 declared -> 4 instances, mcount=4) - "
       "parser must use Insert.mcount/multi_insert, not row_count*column_count")
