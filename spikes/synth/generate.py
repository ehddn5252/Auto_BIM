"""F-012 synthetic DXF generator (SPIKE, provisional formats - D-012 item 3).

Rules (D-012 / F-012):
  * Lives in spikes/, never in src/.  Imports NO takeoff/aggregation code (static test enforces it).
  * Ground truth ("expected") is computed from the generation parameters (what we placed,
    where, on which layer), never by re-reading the DXF with an aggregator.
  * Deterministic: same seed -> byte-identical expected JSON and DXF (ezdxf fixed metadata).
  * Every artefact carries "self-consistency check - NOT real accuracy" (D-004).

Output formats here are PROVISIONAL until the Gate 2 ADR is approved.

Usage:  python generate.py [--seed 20261109] [--out <dir>]
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import random
import shutil
import sys
from pathlib import Path

import ezdxf
from ezdxf import dynblkhelper as dbh
from ezdxf.lldxf import const

SCHEMA = "synth-expected/0-provisional"
DISCLAIMER = "자기 일관성 검증 — 실제 정확도 아님 (D-004). 형식은 Gate 2 ADR 전까지 잠정."
DEFAULT_SEED = 20261109
REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "data" / "drawings" / "samples" / "synth"

# block -> (home layer, synthetic item id).  Items are "합성용" (F-008): not real catalogue entries.
FIX = {
    "LIGHT_A": ("E-LIGHT", "SYN-LIGHT-A"),
    "OUTLET_2P": ("E-POWER", "SYN-OUTLET-2P"),
    "SWITCH_1G": ("E-SWITCH", "SYN-SWITCH-1G"),
    "PANEL_DB": ("E-PANEL", "SYN-PANEL-DB"),
}
UNIT_NAMES = {4: "mm", 6: "m", 5: "cm"}

# Provisional rule dictionary.  Per-case "rules_active" selects ids; scenario "config" may override.
RULES = [
    {"id": "R01", "block": "LIGHT_A", "result": "SYN-LIGHT-A", "priority": 10},
    {"id": "R02", "block": "OUTLET_2P", "result": "SYN-OUTLET-2P", "priority": 10},
    {"id": "R03", "block": "SWITCH_1G", "result": "SYN-SWITCH-1G", "priority": 10},
    {"id": "R04", "block": "PANEL_DB", "result": "SYN-PANEL-DB", "priority": 10, "descend": False},
    {"id": "R05", "block": "BREAKER", "result": "SYN-BREAKER", "priority": 10},
    {"id": "R06", "block": "WRAP_IGN", "result": "IGNORE", "reason": "synthetic wrapper", "priority": 10,
     "descend": False},
    {"id": "R07", "block": "LIGHT_DYN", "result": "SYN-LIGHT-DYN", "priority": 10,
     "note": "matched by ORIGINAL name of dynamic block"},
    {"id": "R08", "block": "LIGHT_W", "attrib": {"WATT": "20"}, "result": "SYN-LIGHT-20W", "priority": 10},
    {"id": "R09", "block": "LIGHT_W", "attrib": {"WATT": "40"}, "result": "SYN-LIGHT-40W", "priority": 10},
    {"id": "R10", "block": "LIGHT_A", "effective_layer": "E-LIGHT-EM", "result": "SYN-LIGHT-EM", "priority": 20},
    {"id": "R11", "block": "SWITCH_2G", "result": "SYN-SWITCH-2G", "priority": 10},
    {"id": "R12", "block": "SWITCH_2G", "effective_layer": "E-SWITCH-X", "result": "SYN-SWITCH-ALT",
     "priority": 10},
]


def jdump(obj) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


class Case:
    """One DXF file + its parameter-derived ground truth."""

    def __init__(self, cid, tids, seed, insunits=4, version="R2018", scenarios=("default",),
                 rules_active=(), title=""):
        self.cid, self.tids, self.seed, self.title = cid, list(tids), seed, title
        self.rng = random.Random(f"{seed}:{cid}")
        self.version = version
        self.doc = ezdxf.new(version, setup=False)
        if insunits is None:
            if "$INSUNITS" in self.doc.header:
                del self.doc.header["$INSUNITS"]
        else:
            self.doc.header["$INSUNITS"] = insunits
        self.insunits = insunits
        self.msp = self.doc.modelspace()
        self.rules_active = list(rules_active)
        self.instances: list[dict] = []
        self.containers: list[dict] = []
        self.warnings: list[dict] = []          # scenario independent
        self.notes: list[str] = []
        self.other = collections.Counter()      # non-INSERT entities (type, layer)
        self.scen = {s: {"config": {}, "fates": {}, "warnings": [], "emit": True,
                         "file_status": "OK"} for s in scenarios}
        self.children_of: dict[str, list] = {}  # block name -> child INSERT entities (definition contents)
        self.layer_state: dict[str, str] = {}   # layer -> "frozen" | "off"
        slots = list(range(20 * 15))
        self.rng.shuffle(slots)
        self._slots = slots
        self.extra: dict = {}
        self.blocks_used: set[str] = set()
        for ln in ("E-LIGHT", "E-POWER", "E-SWITCH", "E-PANEL", "E-ANNO", "A-WALL", "E-MISC", "E-UNIT"):
            self.layer(ln)

    # ---- construction helpers -------------------------------------------------------
    def layer(self, name, state=None):
        if name not in self.doc.layers:
            l = self.doc.layers.add(name)
            if state == "frozen":
                l.freeze()
            elif state == "off":
                l.off()
        if state:
            self.layer_state[name] = state

    def take(self, n):
        out = []
        for _ in range(n):
            s = self._slots.pop()
            out.append((float((s % 20) * 1500), float((s // 20) * 1500 + 1000)))
        return out

    def fixture(self, name):
        if name in self.doc.blocks:
            return self.doc.blocks.get(name)
        blk = self.doc.blocks.new(name)
        r = {"LIGHT_A": 150, "OUTLET_2P": 80, "SWITCH_1G": 60, "PANEL_DB": 250}.get(name, 100)
        blk.add_circle((0, 0), r, dxfattribs={"layer": "0"})
        blk.add_line((-r, 0), (r, 0), dxfattribs={"layer": "0"})
        blk.add_line((0, -r), (0, r), dxfattribs={"layer": "0"})
        return blk

    def put(self, layout, block, pos, layer, **attr):
        """INSERT into a layout or block definition."""
        a = {"layer": layer}
        a.update(attr)
        self.blocks_used.add(block)
        return layout.add_blockref(block, pos, dxfattribs=a)

    def defchild(self, container_block, block, pos, layer="0", **attr):
        lay = self.doc.blocks.get(container_block)
        e = self.put(lay, block, pos, layer, **attr)
        self.children_of.setdefault(container_block, []).append(e)
        return e

    def noise(self, kind, layer, ent):
        self.other[(kind, layer)] += 1
        return ent

    def inst(self, ent, path=(), space="Model", eff=None, tags=None, grid=None):
        d = ent.dxf
        key = "/".join(list(path) + [d.handle]) + (f"#{grid[0]},{grid[1]}" if grid else "")
        rec = {
            "key": key, "handle": d.handle, "insert_path": list(path), "block": d.name,
            "layer": d.layer, "effective_layer": eff or d.layer, "space": space,
            "insert": [round(c, 6) for c in d.insert], "rotation": round(d.get("rotation", 0.0), 6),
            "scale": [d.get("xscale", 1.0), d.get("yscale", 1.0), d.get("zscale", 1.0)],
            "attribs": {a.dxf.tag: a.dxf.text for a in ent.attribs}, "grid": list(grid) if grid else None,
            "tags": tags or {},
        }
        self.instances.append(rec)
        return rec

    def container(self, ent, path=(), space="Model"):
        self.containers.append({"handle": ent.dxf.handle, "insert_path": list(path), "block": ent.dxf.name,
                                "space": space})

    def fate(self, rec, status, detail=None, scen=None):
        names = self.scen.keys() if scen is None else ([scen] if isinstance(scen, str) else scen)
        for s in names:
            self.scen[s]["fates"][rec["key"]] = [status, detail]

    def warn(self, code, scen=None, **kw):
        w = {"code": code}
        w.update(kw)
        (self.warnings if scen is None else self.scen[scen]["warnings"]).append(w)

    def walk(self, top, stop_blocks=(), space="Model", on_leaf=None, on_container=None,
             path=(), parent_eff="0", parent_causes=frozenset()):
        """Expand structure from the *placement parameters* (children_of registry).
        Leaf = block in stop_blocks or block with no registered children."""
        layer = top.dxf.layer
        eff = layer if layer != "0" else parent_eff
        causes = set(parent_causes)
        if self.layer_state.get(eff):
            causes.add(self.layer_state[eff])
        blk = top.dxf.name
        if blk not in stop_blocks and blk in self.children_of:
            if on_container:
                on_container(top, path, space)
            for ch in self.children_of[blk]:
                self.walk(ch, stop_blocks, space, on_leaf, on_container, path + (top.dxf.handle,), eff,
                          frozenset(causes))
            return
        rec = self.inst(top, path, space, eff)
        if on_leaf:
            on_leaf(rec, causes)

    # ---- output ---------------------------------------------------------------------
    def finalize_scenarios(self):
        out = {}
        for name, sc in self.scen.items():
            fates = sc["fates"]
            qty, exc, unm, con, uns = collections.Counter(), collections.defaultdict(list), [], [], []
            for k, (st, det) in sorted(fates.items()):
                if st == "MAPPED":
                    qty[det] += 1
                elif st == "EXCLUDED":
                    exc[det].append(k)
                elif st == "UNMAPPED":
                    unm.append(k)
                elif st == "CONFLICT":
                    con.append(k)
                else:
                    uns.append([k, st, det])
            attr = {"total": len(fates), "mapped": sum(qty.values()),
                    "excluded": sum(len(v) for v in exc.values()), "unmapped": len(unm),
                    "conflict": len(con), "unclassified": len(uns)}
            attr["equation_holds"] = attr["total"] == sum(v for k, v in attr.items() if k != "total")
            assert attr["equation_holds"], (self.cid, name, attr)
            res = {"config": sc["config"], "file_status": sc["file_status"], "emit_quantities": sc["emit"],
                   "quantities": dict(sorted(qty.items())) if sc["emit"] else {},
                   "excluded": {k: v for k, v in sorted(exc.items())},
                   "unmapped": unm, "conflict": con, "unclassified_by_spec": uns,
                   "attribution": attr,
                   "warnings": sorted(self.warnings + sc["warnings"],
                                      key=lambda w: json.dumps(w, sort_keys=True, ensure_ascii=False))}
            hidden = sum(len(exc.get(r, [])) for r in ("LAYER_FROZEN", "LAYER_OFF"))
            res["hidden_layer_excluded"] = {"LAYER_FROZEN": len(exc.get("LAYER_FROZEN", [])),
                                            "LAYER_OFF": len(exc.get("LAYER_OFF", [])), "total": hidden}
            out[name] = res
        return out

    def expected(self, filename):
        unit = UNIT_NAMES.get(self.insunits, "UNIT_UNKNOWN") if self.insunits else "UNIT_UNKNOWN"
        return {
            "schema": SCHEMA, "disclaimer": DISCLAIMER, "case": self.cid, "t_ids": self.tids,
            "title": self.title, "seed": self.seed, "file": filename, "dxf_version": self.version,
            "units": {"insunits": self.insunits, "expected_unit": unit},
            "rules_active": self.rules_active,
            "instances": sorted(self.instances, key=lambda r: r["key"]),
            "container_instances": sorted(self.containers, key=lambda r: (r["insert_path"], r["handle"])),
            "non_insert_entities": [{"type": k[0], "layer": k[1], "count": v}
                                    for k, v in sorted(self.other.items())],
            "scenarios": self.finalize_scenarios(),
            "notes": self.notes, "extra": self.extra,
        }

    def save(self, outdir: Path):
        fn = f"{self.cid}.dxf"
        self.doc.saveas(outdir / fn)
        (outdir / f"{self.cid}.expected.json").write_bytes(jdump(self.expected(fn)))
        return fn


# =============================================================================== cases
def mapped_by_block(c, rec, scen=None):
    c.fate(rec, "MAPPED", FIX[rec["block"]][1], scen)


def case_t01(seed):
    c = Case("t01_basic", ["T-01"], seed, rules_active=["R01", "R02", "R03", "R04"],
             title="four fixture types, plain insertion")
    for b in FIX:
        c.fixture(b)
    counts = {b: c.rng.randint(4, 9) for b in FIX}
    counts["PANEL_DB"] = c.rng.randint(1, 2)
    c.extra["generation_counts"] = counts
    for b, n in counts.items():
        for p in c.take(n):
            e = c.put(c.msp, b, p, FIX[b][0])
            mapped_by_block(c, c.inst(e))
    for i in range(3):
        c.noise("LINE", "A-WALL", c.msp.add_line((0, i * 7000), (30000, i * 7000), dxfattribs={"layer": "A-WALL"}))
    c.noise("TEXT", "E-ANNO", c.msp.add_text("NOTE", dxfattribs={"layer": "E-ANNO", "height": 200,
                                                                 "insert": (0, -500)}))
    return [c]


def case_t02(seed):
    c = Case("t02_nested", ["T-02"], seed, rules_active=["R01", "R02", "R03"],
             title="unmapped wrapper blocks, 2 and 3 levels")
    for b in ("LIGHT_A", "OUTLET_2P", "SWITCH_1G"):
        c.fixture(b)
    unit = c.doc.blocks.new("UNIT_2L")
    unit.add_lwpolyline([(0, 0), (1500, 0), (1500, 1000), (0, 1000)], close=True, dxfattribs={"layer": "0"})
    c.defchild("UNIT_2L", "LIGHT_A", (300, 500))
    c.defchild("UNIT_2L", "LIGHT_A", (900, 500))
    c.defchild("UNIT_2L", "OUTLET_2P", (1300, 200))
    floor = c.doc.blocks.new("FLOOR_3L")
    c.defchild("FLOOR_3L", "UNIT_2L", (0, 0))
    c.defchild("FLOOR_3L", "UNIT_2L", (2000, 0))
    c.defchild("FLOOR_3L", "SWITCH_1G", (1000, 1500))
    p, q = c.rng.randint(2, 4), c.rng.randint(2, 3)
    c.extra["generation"] = {"UNIT_2L_top": p, "FLOOR_3L_top": q, "UNIT_2L_per_floor": 2,
                             "lights_per_unit": 2, "outlets_per_unit": 1, "switches_per_floor": 1}
    c.extra["formula"] = {"LIGHT_A": "2*(p+2q)", "OUTLET_2P": "1*(p+2q)", "SWITCH_1G": "q"}

    def leaf(rec, causes):
        mapped_by_block(c, rec)

    pos = c.take(p + q)
    for i in range(p):
        c.walk(c.put(c.msp, "UNIT_2L", pos[i], "E-UNIT"), on_leaf=leaf, on_container=lambda e, pa, sp: c.container(e, pa, sp))
    for i in range(q):
        c.walk(c.put(c.msp, "FLOOR_3L", pos[p + i], "E-UNIT"), on_leaf=leaf, on_container=lambda e, pa, sp: c.container(e, pa, sp))
    c.notes.append("wrappers carry own polyline geometry; spec F-005/F-009 does not say whether such a wrapper "
                   "counts as UNMAPPED. Truth treats descended wrappers as containers (not attributed).")
    c.notes.append("children are on layer '0' -> effective layer = wrapper top INSERT layer (E-UNIT)")
    return [c]


def case_t03(seed):
    c = Case("t03_nested_match_hidden", ["T-03"], seed, scenarios=("default", "descend_all"),
             rules_active=["R01", "R02", "R04", "R05", "R06"], title="matched parent hides matched children")
    c.scen["default"]["config"] = {"descend": []}
    c.scen["descend_all"]["config"] = {"descend": ["R04", "R06"]}
    for b in ("LIGHT_A", "OUTLET_2P", "PANEL_DB"):
        c.fixture(b)
    c.fixture("BREAKER")
    c.fixture("PLATE_X")
    c.fixture("WRAP_IGN")
    k, m = c.rng.randint(2, 4), c.rng.randint(2, 3)
    na, nb, nd = c.rng.randint(1, 3), c.rng.randint(2, 3), c.rng.randint(1, 3)
    for _ in range(k):
        c.defchild("PANEL_DB", "BREAKER", (0, 0))
    for _ in range(m):
        c.defchild("WRAP_IGN", "LIGHT_A", (0, 0))
    c.defchild("OUTLET_2P", "PLATE_X", (0, 0))
    c.extra["generation"] = {"panels": na, "breakers_per_panel": k, "wrappers": nb, "lights_per_wrapper": m,
                             "outlets_with_unmatched_child": nd}
    pos = c.take(na + nb + nd)
    for i in range(na):                                                    # (a) matched parent, matched child
        P = c.put(c.msp, "PANEL_DB", pos[i], "E-PANEL")
        rp = c.inst(P)
        c.fate(rp, "MAPPED", "SYN-PANEL-DB")
        for ch in c.children_of["PANEL_DB"]:
            rc = c.inst(ch, [P.dxf.handle], eff="E-PANEL", tags={"hidden_by_stop": True})
            c.fate(rc, "MAPPED", "SYN-BREAKER", scen="descend_all")
        c.warn("NESTED_MATCH_HIDDEN", scen="default", handle=P.dxf.handle, insert_path=[], parent_block="PANEL_DB",
               parent_rule="R04", parent_result="SYN-PANEL-DB", hidden_children=k, hidden_by_result="item",
               hidden_child_rules=["R05"])
    for i in range(nb):                                                    # (b) IGNORE wrapper with fixtures
        W = c.put(c.msp, "WRAP_IGN", pos[na + i], "E-LIGHT")
        rw = c.inst(W)
        c.fate(rw, "EXCLUDED", "RULE_IGNORE")
        for ch in c.children_of["WRAP_IGN"]:
            rc = c.inst(ch, [W.dxf.handle], eff="E-LIGHT", tags={"hidden_by_stop": True})
            c.fate(rc, "MAPPED", "SYN-LIGHT-A", scen="descend_all")
        c.warn("NESTED_MATCH_HIDDEN", scen="default", handle=W.dxf.handle, insert_path=[], parent_block="WRAP_IGN",
               parent_rule="R06", parent_result="IGNORE", hidden_children=m, hidden_by_result="item",
               hidden_child_rules=["R01"])
    for i in range(nd):                                                    # (d) child matches no rule: no warning
        O = c.put(c.msp, "OUTLET_2P", pos[na + nb + i], "E-POWER")
        c.fate(c.inst(O), "MAPPED", "SYN-OUTLET-2P")
    c.notes.append("PLATE_X child of OUTLET_2P matches no rule -> must NOT raise NESTED_MATCH_HIDDEN (false-alarm check)")
    c.notes.append("scenario descend_all: descend=true on R04 and R06 -> 0 NESTED_MATCH_HIDDEN, children counted")
    return [c]


def case_t04(seed):
    c = Case("t04_dynamic", ["T-04"], seed, rules_active=["R07"],
             title="dynamic blocks: resolvable and unresolvable *U")
    for a in (dbh.AcDbDynamicBlockGUID, dbh.AcDbBlockRepBTag):
        if a not in c.doc.appids:
            c.doc.appids.add(a)
    dyn = c.doc.blocks.new("LIGHT_DYN")
    dyn.add_circle((0, 0), 150, dxfattribs={"layer": "0"})
    dyn.block_record.set_xdata(dbh.AcDbDynamicBlockGUID, [(1000, "{00000000-0000-4000-8000-000000000001}")])
    u = []
    for r in (160, 170):
        b = c.doc.blocks.new_anonymous_block("U")
        b.add_circle((0, 0), r, dxfattribs={"layer": "0"})
        b.block_record.set_xdata(dbh.AcDbBlockRepBTag, [(1005, dyn.block_record.dxf.handle)])
        u.append(b)
    bad = c.doc.blocks.new_anonymous_block("U")                       # tag missing -> unresolvable
    bad.add_circle((0, 0), 180, dxfattribs={"layer": "0"})
    na = [c.rng.randint(2, 4), c.rng.randint(1, 3)]
    nd, nb = c.rng.randint(1, 3), c.rng.randint(2, 4)
    c.extra["generation"] = {"resolvable_star_u": {u[0].name: na[0], u[1].name: na[1]}, "direct_reference": nd,
                             "unresolvable_star_u": {bad.name: nb}, "original_name": "LIGHT_DYN"}
    pos = c.take(sum(na) + nd + nb)
    i = 0
    for blk, n in ((u[0], na[0]), (u[1], na[1])):                    # (a)
        for _ in range(n):
            e = c.put(c.msp, blk.name, pos[i], "E-LIGHT"); i += 1
            r = c.inst(e, tags={"dynamic": "resolved", "original_name": "LIGHT_DYN",
                                "synthetic_marker": "AcDbBlockRepBTag"})
            c.fate(r, "MAPPED", "SYN-LIGHT-DYN")
    for _ in range(nd):
        e = c.put(c.msp, "LIGHT_DYN", pos[i], "E-LIGHT"); i += 1
        c.fate(c.inst(e, tags={"dynamic": "direct_definition_reference", "original_name": "LIGHT_DYN"}),
               "MAPPED", "SYN-LIGHT-DYN")
    for _ in range(nb):                                              # (b)
        e = c.put(c.msp, bad.name, pos[i], "E-LIGHT"); i += 1
        r = c.inst(e, tags={"dynamic": "unresolved"})
        c.fate(r, "UNMAPPED", None)
        c.warn("DYNAMIC_UNRESOLVED", handle=r["handle"], block=bad.name, insert_path=[])
    c.notes.append("T-04a PARTIAL: resolvability markers are SYNTHETIC (ezdxf-documented AcDbBlockRepBTag/"
                   "AcDbDynamicBlockGUID). Shape in real AutoCAD output is unverified.")
    return [c]


def case_t05(seed):
    c = Case("t05_attrib", ["T-05"], seed, rules_active=["R08", "R09"],
             title="same block, ATTRIB WATT selects item")
    blk = c.doc.blocks.new("LIGHT_W")
    blk.add_circle((0, 0), 150, dxfattribs={"layer": "0"})
    blk.add_attdef("WATT", (200, 0), "0", dxfattribs={"height": 50, "layer": "0"})
    n = {"20": c.rng.randint(2, 5), "40": c.rng.randint(2, 5), "60": c.rng.randint(1, 2)}
    c.extra["generation"] = {"WATT_counts": n}
    pos = c.take(sum(n.values()))
    i = 0
    for w, cnt in n.items():
        for _ in range(cnt):
            e = c.msp.add_auto_blockref("LIGHT_W", pos[i], {"WATT": w}, dxfattribs={"layer": "E-LIGHT"}); i += 1
            r = c.inst(e)
            if w == "60":
                c.fate(r, "UNMAPPED", None)
            else:
                c.fate(r, "MAPPED", f"SYN-LIGHT-{w}W")
    c.notes.append("WATT=60 has no rule -> UNMAPPED")
    return [c]


def _unit_case(cid, tid, insunits, seed, scale, block_units=None, rules=("R01", "R02", "R03", "R04")):
    c = Case(cid, [tid], seed, insunits=insunits, rules_active=list(rules))
    for b in FIX:
        blk = c.fixture(b)
        if block_units is not None:
            blk.block_record.dxf.units = block_units
    n = {b: c.rng.randint(2, 4) for b in FIX}
    c.extra["generation_counts"] = n
    c.extra["coordinate_scale_to_model_unit"] = scale
    for b, k in n.items():
        for p in c.take(k):
            e = c.put(c.msp, b, (p[0] * scale, p[1] * scale), FIX[b][0])
            mapped_by_block(c, c.inst(e))
    return c


def case_t06(seed):
    a = _unit_case("t06_mm_file", "T-06", 4, seed, 1.0, block_units=4)
    b = _unit_case("t06_m_file", "T-06", 6, seed, 0.001, block_units=4)
    b.warn("BLOCK_UNIT_DIFF", blocks=sorted(FIX), block_units=4, file_units=6,
           note="block record units (mm) differ from $INSUNITS (m); counts unaffected")
    a.scen["user_override_m"] = {"config": {"user_unit": "m", "decision_source": "user"}, "fates": {},
                                 "warnings": [{"code": "UNIT_OVERRIDE", "header_insunits": 4, "user_unit": "m"}],
                                 "emit": True, "file_status": "OK"}
    a.scen["user_override_m"]["fates"] = dict(a.scen["default"]["fates"])
    a.notes.append("scenario user_override_m: user unit differs from header value 4 -> UNIT_OVERRIDE (D-014 Q13); "
                   "counts unchanged")
    a.notes.append("set pair: t06_mm_file + t06_m_file -> SET_UNIT_DIFF in t06_set.expected.json")
    return [a, b]


def case_t07(seed):
    out = []
    for cid, ins in (("t07_insunits_missing", None), ("t07_insunits_zero", 0)):
        c = Case(cid, ["T-07"], seed, insunits=ins, scenarios=("default", "user_mm"),
                 rules_active=["R01", "R02", "R03", "R04"])
        c.scen["default"]["emit"] = False
        c.scen["default"]["file_status"] = "UNIT_UNKNOWN"
        c.scen["user_mm"]["config"] = {"user_unit": "mm", "decision_source": "user",
                                       "expect_warning": "UNIT_USER_SET"}
        # D-014 Q13: header absent/0 + user unit -> UNIT_USER_SET (UNIT_OVERRIDE only if it differs from a header value)
        c.warn("UNIT_USER_SET", scen="user_mm", header_insunits=ins, user_unit="mm")
        for b in FIX:
            c.fixture(b)
        for b in FIX:
            for p in c.take(c.rng.randint(2, 4)):
                r = c.inst(c.put(c.msp, b, p, FIX[b][0]))
                c.fate(r, "MAPPED", FIX[b][1], scen="user_mm")
        c.notes.append("default: quantities must NOT be emitted (UNIT_UNKNOWN). user_mm: user-declared unit "
                       "(D-010) -> counts below. Absence of $INSUNITS for 'missing' file verified by test.")
        out.append(c)
    return out


def case_t08(seed):
    c = Case("t08_scale_rot_mirror", ["T-08"], seed, rules_active=["R01"],
             title="scale 2x, non-uniform, mirror, rotation, zero scale")
    c.fixture("LIGHT_A")
    variants = [("scale2x", dict(xscale=2.0, yscale=2.0, zscale=2.0)),
                ("nonuniform", dict(xscale=2.0, yscale=0.5, zscale=1.0)),
                ("mirror_x", dict(xscale=-1.0)),
                ("mirror_xy", dict(xscale=-1.0, yscale=-1.0)),
                ("rot37", dict(rotation=37.0)),
                ("zero_scale", dict(xscale=0.0))]
    gen = {}
    for name, attr in variants:
        n = c.rng.randint(1, 3)
        gen[name] = n
        for p in c.take(n):
            r = c.inst(c.put(c.msp, "LIGHT_A", p, "E-LIGHT", **attr), tags={"variant": name})
            if name == "zero_scale":
                c.fate(r, "EXCLUDED", "ZERO_SCALE")
            else:
                c.fate(r, "MAPPED", "SYN-LIGHT-A")
    c.extra["generation"] = gen
    return [c]


def case_t09(seed):
    c = Case("t09_hidden_layers", ["T-09"], seed, scenarios=("default", "include_hidden"),
             rules_active=["R01"], title="frozen/off layers, direct and via nested parents")
    c.scen["default"]["config"] = {"include_hidden": False}
    c.scen["include_hidden"]["config"] = {"include_hidden": True}
    c.layer("E-FROZEN", "frozen")
    c.layer("E-OFF", "off")
    c.fixture("LIGHT_A")
    # wrappers
    c.doc.blocks.new("ROOM_W")                  # visible wrapper, child on frozen layer
    c.defchild("ROOM_W", "LIGHT_A", (0, 0), layer="E-FROZEN")
    c.doc.blocks.new("ROOM_W2")                 # wrapper placed on frozen layer, child on visible layer
    c.defchild("ROOM_W2", "LIGHT_A", (0, 0), layer="E-LIGHT")
    c.doc.blocks.new("ROOM_W3")                 # wrapper placed on off layer; one visible-layer child, one layer-0 child
    c.defchild("ROOM_W3", "LIGHT_A", (0, 0), layer="E-LIGHT")
    c.defchild("ROOM_W3", "LIGHT_A", (400, 0), layer="0")
    plan = [("direct_visible", "LIGHT_A", "E-LIGHT"), ("direct_frozen", "LIGHT_A", "E-FROZEN"),
            ("direct_off", "LIGHT_A", "E-OFF"), ("wrap_child_frozen", "ROOM_W", "E-LIGHT"),
            ("wrap_on_frozen", "ROOM_W2", "E-FROZEN"), ("wrap_on_off", "ROOM_W3", "E-OFF")]
    gen = {}

    def leaf(rec, causes):
        c.fate(rec, "MAPPED", "SYN-LIGHT-A", scen="include_hidden")
        if "frozen" in causes:
            c.fate(rec, "EXCLUDED", "LAYER_FROZEN", scen="default")
        elif "off" in causes:
            c.fate(rec, "EXCLUDED", "LAYER_OFF", scen="default")
        else:
            c.fate(rec, "MAPPED", "SYN-LIGHT-A", scen="default")

    for name, blk, lay in plan:
        n = c.rng.randint(1, 3)
        gen[name] = n
        for p in c.take(n):
            c.walk(c.put(c.msp, blk, p, lay), on_leaf=leaf, on_container=lambda e, pa, sp: c.container(e, pa, sp))
    c.extra["generation"] = gen
    c.notes.append("wrap_on_off / wrap_on_frozen: truth follows AutoCAD display (a hidden parent INSERT hides all "
                   "children). Spec F-006 words LAYER_OFF as 'effective layer off' only -> gap, see report. "
                   "AutoCAD behaviour NOT verified here (no CAD available).")
    c.notes.append("precedence: LAYER_FROZEN before LAYER_OFF (F-006 order)")
    return [c]


def case_t10(seed):
    c = Case("t10_paper_space", ["T-10"], seed, rules_active=["R01", "R02"], title="symbols placed in layouts")
    c.fixture("LIGHT_A")
    c.fixture("OUTLET_2P")
    nm = c.rng.randint(3, 6)
    for p in c.take(nm):
        mapped_by_block(c, c.inst(c.put(c.msp, "LIGHT_A", p, "E-LIGHT")))
    gen = {"model_lights": nm}
    for lname in ("Layout1", "Layout2"):
        lay = c.doc.layouts.get(lname) if lname in c.doc.layouts else c.doc.layouts.new(lname)
        n = c.rng.randint(1, 3)
        gen[lname] = n
        for j in range(n):
            blk = ("LIGHT_A", "OUTLET_2P")[j % 2]
            r = c.inst(c.put(lay, blk, (50 + 30 * j, 50), FIX[blk][0]), space=f"Paper:{lname}")
            c.fate(r, "EXCLUDED", "PAPER_SPACE")
    c.extra["generation"] = gen
    return [c]


def case_t11(seed):
    c = Case("t11_duplicates", ["T-11"], seed, rules_active=["R01"], title="duplicate insertions")
    c.fixture("LIGHT_A")
    base = []
    for p in c.take(c.rng.randint(5, 7)):
        e = c.put(c.msp, "LIGHT_A", p, "E-LIGHT")
        r = c.inst(e)
        c.fate(r, "MAPPED", "SYN-LIGHT-A")
        base.append((p, r))
    gen = {"base": len(base)}
    kinds = [("exact_same_pos", (0.0, 0.0), 0.0, True), ("within_0p5mm", (0.5, 0.0), 0.0, True),
             ("same_pos_rot90", (0.0, 0.0), 90.0, True), ("apart_50mm", (50.0, 0.0), 0.0, False)]
    for idx, (name, off, rot, is_dup) in enumerate(kinds):
        p, first = base[idx]
        e = c.put(c.msp, "LIGHT_A", (p[0] + off[0], p[1] + off[1]), "E-LIGHT", rotation=rot)
        r = c.inst(e, tags={"variant": name, "pair": first["key"]})
        if is_dup:
            c.fate(r, "EXCLUDED", "DUPLICATE")
            r["tags"]["pair_handle"] = first["handle"]
            r["tags"]["rotation_differs"] = rot != 0.0
        else:
            c.fate(r, "MAPPED", "SYN-LIGHT-A")
        gen[name] = 1
    c.extra["generation"] = gen
    c.extra["tolerance_mm"] = 1.0
    return [c]


def case_t12(seed):
    c = Case("t12_legend", ["T-12"], seed, scenarios=("no_legend_rule", "legend_rule"),
             rules_active=["R01", "R02", "R03", "R04"], title="legend symbols + 범례 text")
    area = [40000.0, 0.0, 43000.0, 3000.0]
    c.scen["legend_rule"]["config"] = {"legend_area": area}
    for b in FIX:
        c.fixture(b)
    n = {b: c.rng.randint(2, 4) for b in FIX}
    for b, k in n.items():
        for p in c.take(k):
            mapped_by_block(c, c.inst(c.put(c.msp, b, p, FIX[b][0])))
    t = c.noise("TEXT", "E-ANNO", c.msp.add_text("범례 (LEGEND)", dxfattribs={
        "layer": "E-ANNO", "height": 200, "insert": (40000, 2700)}))
    leg = []
    for i, b in enumerate(FIX):
        r = c.inst(c.put(c.msp, b, (40500 + i * 600, 1200), FIX[b][0]), tags={"legend": True})
        c.fate(r, "MAPPED", FIX[b][1], scen="no_legend_rule")
        c.fate(r, "EXCLUDED", "LEGEND_AREA", scen="legend_rule")
        leg.append(r["handle"])
    c.warn("LEGEND_SUSPECT", scen="no_legend_rule", text_handle=t.dxf.handle, text="범례 (LEGEND)",
           region_candidate=area, handles=sorted(leg))
    c.extra["generation"] = {"real_counts": n, "legend_symbols_one_per_type": 4}
    c.notes.append("legend symbols deliberately sit on the same fixture layers as real ones")
    return [c]


def case_t13(seed):
    c = Case("t13_xref", ["T-13"], seed, rules_active=["R01", "R02"], title="XREF to a file that does not exist")
    c.fixture("LIGHT_A")
    c.doc.add_xref_def("missing_ref_plan.dxf", "XR_PLAN")
    defh = c.doc.blocks.get("XR_PLAN").block_record.dxf.handle
    n = c.rng.randint(2, 4)
    for p in c.take(n):
        mapped_by_block(c, c.inst(c.put(c.msp, "LIGHT_A", p, "E-LIGHT")))
    c.warn("XREF", target="block_definition", block="XR_PLAN", handle=defh, xref_path="missing_ref_plan.dxf")
    nx = c.rng.randint(1, 2)
    for p in c.take(nx):
        e = c.put(c.msp, "XR_PLAN", p, "A-WALL")
        r = c.inst(e, tags={"xref": True})
        c.fate(r, "UNCLASSIFIED_BY_SPEC", "XREF_INSERT")
        c.warn("XREF", target="insert", block="XR_PLAN", handle=r["handle"], insert_path=[])
    c.scen["default"]["file_status"] = "INCOMPLETE"
    c.extra["generation"] = {"lights": n, "xref_inserts": nx}
    c.notes.append("spec gap: F-009 attribution has no bucket for XREF INSERT instances -> 'unclassified_by_spec'")
    return [c]


def case_t14(seed):
    c = Case("t14_minsert", ["T-14"], seed, rules_active=["R02"], title="MINSERT arrays")
    c.fixture("OUTLET_2P")
    pos = c.take(2)
    specs = [("3x4", pos[0], 3, 4, 500.0, 800.0, 0.0), ("2x5_rot90", pos[1], 2, 5, 400.0, 600.0, 90.0)]
    for name, p, rows, cols, rsp, csp, rot in specs:
        e = c.put(c.msp, "OUTLET_2P", p, "E-POWER", row_count=rows, column_count=cols, row_spacing=rsp,
                  column_spacing=csp, rotation=rot)
        for rr in range(rows):
            for cc in range(cols):
                r = c.inst(e, grid=(rr, cc), tags={"minsert": name})
                c.fate(r, "MAPPED", "SYN-OUTLET-2P")
    c.extra["generation"] = {"3x4": 12, "2x5_rot90": 10}
    return [c]


def case_t14b(seed):
    c = Case("t14b_minsert_zero_spacing", ["T-14"], seed, rules_active=["R02"],
             title="MINSERT rows=3 cols=4 with row_spacing=0 (truth NOT settled)")
    c.fixture("OUTLET_2P")
    e = c.put(c.msp, "OUTLET_2P", c.take(1)[0], "E-POWER", row_count=3, column_count=4, row_spacing=0.0,
              column_spacing=800.0)
    c.extra["ambiguity"] = {
        "declared_rows_x_cols": 12, "ezdxf_mcount": 4, "insert_handle": e.dxf.handle,
        "status": "NO TRUTH ASSIGNED - needs real AutoCAD behaviour; if 12 stacked copies exist they are "
                  "also DUPLICATE candidates (F-006 rank 7)"}
    c.notes.append("deliberately has no scenario fates: ezdxf mcount treats spacing 0 as 1 in that direction")
    return [c]


def case_t15(seed):
    c = Case("t15_layer0_inherit", ["T-15"], seed, rules_active=["R01", "R10"],
             title="layer-0 INSERT inside wrapper inherits wrapper layer; layer-conditional rule")
    c.layer("E-LIGHT-EM")
    c.fixture("LIGHT_A")
    c.doc.blocks.new("EM_WRAP")
    c.defchild("EM_WRAP", "LIGHT_A", (0, 0), layer="0")
    x, y, z = c.rng.randint(1, 3), c.rng.randint(1, 3), c.rng.randint(1, 2)

    def leaf(rec, causes):
        c.fate(rec, "MAPPED", "SYN-LIGHT-EM" if rec["effective_layer"] == "E-LIGHT-EM" else "SYN-LIGHT-A")

    pos = c.take(x + y + z)
    for i in range(x):
        c.walk(c.put(c.msp, "EM_WRAP", pos[i], "E-LIGHT-EM"), on_leaf=leaf, on_container=lambda e, pa, sp: c.container(e, pa, sp))
    for i in range(y):
        c.walk(c.put(c.msp, "EM_WRAP", pos[x + i], "E-LIGHT"), on_leaf=leaf, on_container=lambda e, pa, sp: c.container(e, pa, sp))
    for i in range(z):
        c.walk(c.put(c.msp, "LIGHT_A", pos[x + y + i], "0"), on_leaf=leaf)
    c.extra["generation"] = {"wrapper_on_E-LIGHT-EM": x, "wrapper_on_E-LIGHT": y, "direct_on_layer_0": z}
    return [c]


def case_t16(seed):
    c = Case("t16_non_block_symbols", ["T-16"], seed, rules_active=["R01"],
             title="fixture layer carries CIRCLE / closed polyline symbols")
    c.fixture("LIGHT_A")
    nb = c.rng.randint(2, 4)
    for p in c.take(nb):
        mapped_by_block(c, c.inst(c.put(c.msp, "LIGHT_A", p, "E-LIGHT")))
    ncirc, npoly, nctl = c.rng.randint(2, 3), c.rng.randint(1, 2), 2
    hs = []
    for p in c.take(ncirc):
        e = c.noise("CIRCLE", "E-LIGHT", c.msp.add_circle(p, 150, dxfattribs={"layer": "E-LIGHT"}))
        hs.append((e.dxf.handle, "CIRCLE"))
    for p in c.take(npoly):
        e = c.noise("LWPOLYLINE", "E-LIGHT", c.msp.add_lwpolyline(
            [(p[0] - 100, p[1] - 100), (p[0] + 100, p[1] - 100), (p[0] + 100, p[1] + 100), (p[0] - 100, p[1] + 100)],
            close=True, dxfattribs={"layer": "E-LIGHT"}))
        hs.append((e.dxf.handle, "LWPOLYLINE"))
    for p in c.take(nctl):                                     # negative control: not on a rule layer
        c.noise("CIRCLE", "E-MISC", c.msp.add_circle(p, 150, dxfattribs={"layer": "E-MISC"}))
    for h, t in sorted(hs):
        c.warn("NON_BLOCK_SYMBOL", handle=h, entity_type=t, layer="E-LIGHT")
    c.extra["generation"] = {"blocks": nb, "circles": ncirc, "closed_polylines": npoly,
                             "control_circles_on_E-MISC (no warning expected)": nctl}
    return [c]


def case_t17(seed):
    c = Case("t17_acis_proxy_underlay", ["T-17"], seed, version="R2010", rules_active=["R01"],
             title="ACIS / PROXY / UNDERLAY / IMAGE stubs")
    c.fixture("LIGHT_A")
    for p in c.take(c.rng.randint(2, 3)):
        mapped_by_block(c, c.inst(c.put(c.msp, "LIGHT_A", p, "E-LIGHT")))
    pos = c.take(10)
    synth_fail = []
    items = []                        # (code, entity type, entity)
    s = c.msp.add_3dsolid(dxfattribs={"layer": "E-MISC"}); s.sat = ["400 0 1 0", "FAKE-SAT"]; items.append(("ACIS", s))
    r = c.msp.add_region(dxfattribs={"layer": "E-MISC"}); r.sat = ["400 0 1 0", "FAKE-SAT"]; items.append(("ACIS", r))
    b = c.msp.add_body(dxfattribs={"layer": "E-MISC"}); b.sat = ["400 0 1 0", "FAKE-SAT"]; items.append(("ACIS", b))
    from ezdxf.lldxf.tags import Tags
    from ezdxf.lldxf.types import DXFTag
    pe = c.msp.new_entity("ACAD_PROXY_ENTITY", {"layer": "E-MISC"})
    pe.acdb_proxy_entity = Tags([DXFTag(100, "AcDbProxyEntity"), DXFTag(90, 498), DXFTag(91, 500),
                                 DXFTag(92, 0), DXFTag(93, 0), DXFTag(95, 0), DXFTag(70, 1)])
    items.append(("PROXY", pe))
    for fmt in ("pdf", "dwf", "dgn"):
        try:
            d = c.doc.add_underlay_def(f"fake_plan.{fmt}", fmt=fmt, name="1" if fmt == "pdf" else "default")
            items.append(("UNDERLAY", c.msp.add_underlay(d, insert=pos[len(items)], dxfattribs={"layer": "E-MISC"})))
        except Exception as ex:                                   # recorded, not hidden
            synth_fail.append(f"{fmt}: {type(ex).__name__}: {ex}")
    try:
        d = c.doc.add_image_def("fake_image.png", (100, 100))
        items.append(("UNDERLAY", c.msp.add_image(d, insert=pos[9], size_in_units=(10, 10),
                                                  dxfattribs={"layer": "E-MISC"})))
    except Exception as ex:
        synth_fail.append(f"image: {type(ex).__name__}: {ex}")
    for code, e in items:
        c.warn(code, handle=e.dxf.handle, entity_type=e.dxftype(), layer="E-MISC")
    c.scen["default"]["file_status"] = "INCOMPLETE"
    c.extra["generation"] = {"entities": [(code, e.dxftype()) for code, e in items], "synthesis_failures": synth_fail}
    c.notes.append("ACIS bodies carry FAKE payload (no geometry); PROXY has no proxy graphic; SAB (R2013+) not "
                   "synthesised. These test warning detection only.")
    return [c]


def case_t18(seed):
    c = Case("t18_conflict", ["T-18"], seed, rules_active=["R11", "R12"], title="two equal-priority rules match")
    c.layer("E-SWITCH-X")
    c.fixture("SWITCH_2G")
    na, nc = c.rng.randint(2, 4), c.rng.randint(2, 3)
    pos = c.take(na + nc)
    for i in range(na):
        c.fate(c.inst(c.put(c.msp, "SWITCH_2G", pos[i], "E-SWITCH")), "MAPPED", "SYN-SWITCH-2G")
    for i in range(nc):
        c.fate(c.inst(c.put(c.msp, "SWITCH_2G", pos[na + i], "E-SWITCH-X"), eff=None), "CONFLICT", None)
    c.extra["generation"] = {"single_match_R11": na, "double_match_R11_R12": nc}
    return [c]


def case_t19(seed):
    out = []
    for fl in (1, 2, 3):
        c = Case(f"t19_floor{fl}", ["T-19"], seed, rules_active=["R01", "R02", "R03", "R04"])
        for b in FIX:
            c.fixture(b)
        for b in FIX:
            for p in c.take(c.rng.randint(1, 5)):
                mapped_by_block(c, c.inst(c.put(c.msp, b, p, FIX[b][0])))
        out.append(c)
    return out


def case_t21(seed):
    c = Case("t21_unused_definitions", ["T-21"], seed, rules_active=["R01", "R03", "R04"],
             title="block definitions never inserted")
    for b in ("LIGHT_A", "SWITCH_1G", "PANEL_DB"):
        c.fixture(b)
    c.fixture("UNUSED_BOX")
    n = c.rng.randint(2, 3)
    for p in c.take(n):
        mapped_by_block(c, c.inst(c.put(c.msp, "SWITCH_1G", p, "E-SWITCH")))
    c.extra["generation"] = {"inserted": {"SWITCH_1G": n},
                             "defined_but_not_inserted": ["LIGHT_A", "PANEL_DB", "UNUSED_BOX"]}
    c.notes.append("expected: LIGHT_A, PANEL_DB quantity 0 (not listed), UNUSED_BOX not UNMAPPED")
    return [c]


def case_t20_empty(seed):
    c = Case("t20_empty", ["T-20"], seed, title="valid but empty drawing")
    c.extra["generation"] = {"entities": 0}
    c.notes.append("empty drawing reads fine; zero quantities, not a read failure")
    return [c]


CASE_FUNCS = [case_t01, case_t02, case_t03, case_t04, case_t05, case_t06, case_t07, case_t08, case_t09,
              case_t10, case_t11, case_t12, case_t13, case_t14, case_t14b, case_t15, case_t16, case_t17,
              case_t18, case_t19, case_t21, case_t20_empty]

COVERAGE = {
    "T-01": ("SYNTHESIZED", "t01_basic", ""),
    "T-02": ("SYNTHESIZED", "t02_nested", "2- and 3-level wrappers"),
    "T-03": ("SYNTHESIZED", "t03_nested_match_hidden", "scenarios default/descend_all; incl. false-alarm control"),
    "T-04": ("PARTIAL", "t04_dynamic",
             "(b) unresolvable *U fully synthesised. (a) resolvable *U uses SYNTHETIC ezdxf-documented markers; "
             "real AutoCAD marker shape unverified -> real-drawing stage must confirm"),
    "T-05": ("SYNTHESIZED", "t05_attrib", ""),
    "T-06": ("SYNTHESIZED", "t06_mm_file+t06_m_file+t06_set", "SET_UNIT_DIFF, BLOCK_UNIT_DIFF"),
    "T-07": ("SYNTHESIZED", "t07_insunits_missing+t07_insunits_zero", ""),
    "T-08": ("SYNTHESIZED", "t08_scale_rot_mirror", ""),
    "T-09": ("PARTIAL", "t09_hidden_layers",
             "files synthesised; truth for parent-hidden children follows AutoCAD display rule which could not "
             "be verified without a CAD program; viewport-level VP freeze not synthesised"),
    "T-10": ("SYNTHESIZED", "t10_paper_space", "viewport layer overrides not covered"),
    "T-11": ("SYNTHESIZED", "t11_duplicates", ""),
    "T-12": ("SYNTHESIZED", "t12_legend", ""),
    "T-13": ("SYNTHESIZED", "t13_xref", "target file intentionally absent; attribution bucket for XREF INSERT unspecified"),
    "T-14": ("PARTIAL", "t14_minsert+t14b_minsert_zero_spacing",
             "3x4 and rotated 2x5 synthesised with truth; spacing-0 case has NO truth (behaviour ambiguous)"),
    "T-15": ("SYNTHESIZED", "t15_layer0_inherit", ""),
    "T-16": ("SYNTHESIZED", "t16_non_block_symbols", ""),
    "T-17": ("PARTIAL", "t17_acis_proxy_underlay",
             "type-level stubs only (fake ACIS payload, empty proxy, nonexistent underlay files); real ACIS/SAB, "
             "real proxy graphics not synthesisable -> real-drawing stage"),
    "T-18": ("SYNTHESIZED", "t18_conflict", ""),
    "T-19": ("SYNTHESIZED", "t19_floor1..3+t19_set (+ identical-copy negative set)", ""),
    "T-20": ("SYNTHESIZED", "t20_corrupt+t20_empty", "corrupt file is hand-built bytes; read failure verified by test"),
    "T-21": ("SYNTHESIZED", "t21_unused_definitions", ""),
}

CORRUPT_BYTES = (b"  0\nSECTION\n  2\nHEADER\n  9\n$ACADVER\n  1\nAC1032\n  0\nENDSEC\n"
                 b"  0\nSECTION\n  2\nENTITIES\n  0\nINSERT\n  2\nLIGHT_A\n 10\n")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_set(outdir, name, tids, cases, extra):
    tot = collections.Counter()
    for c in cases:
        for item, n in c.finalize_scenarios()["default"]["quantities"].items():
            tot[item] += n
    obj = {"schema": SCHEMA, "disclaimer": DISCLAIMER, "set": name, "t_ids": tids,
           "files": [f"{c.cid}.dxf" for c in cases], "set_quantities": dict(sorted(tot.items()))}
    obj.update(extra)
    (outdir / f"{name}.expected.json").write_bytes(jdump(obj))


def generate(outdir: Path, seed: int = DEFAULT_SEED) -> dict:
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for old in list(outdir.glob("*.dxf")) + list(outdir.glob("*.json")):
        old.unlink()
    saved = ezdxf.options.write_fixed_meta_data_for_testing
    ezdxf.options.write_fixed_meta_data_for_testing = True
    try:
        all_cases = []
        for fn in CASE_FUNCS:
            cs = fn(seed)
            for c in cs:
                c.save(outdir)
            all_cases.extend(cs)
            if fn is case_t06:
                write_set(outdir, "t06_set", ["T-06"], cs, {"set_warnings": [
                    {"code": "SET_UNIT_DIFF", "files": {"t06_mm_file.dxf": 4, "t06_m_file.dxf": 6}}]})
            if fn is case_t19:
                write_set(outdir, "t19_set", ["T-19"], cs, {"set_warnings": []})
        # T-19 negative set: byte-identical copy -> F-001 must abort the run
        shutil.copyfile(outdir / "t19_floor1.dxf", outdir / "t19_floor1_copy.dxf")
        (outdir / "t19_dup_hash.expected.json").write_bytes(jdump({
            "schema": SCHEMA, "disclaimer": DISCLAIMER, "set": "t19_dup_hash", "t_ids": ["T-19"],
            "files": ["t19_floor1.dxf", "t19_floor1_copy.dxf"],
            "expected": "RUN_ABORTED (identical SHA-256 in one set, F-001)"}))
        # T-20 corrupt
        (outdir / "t20_corrupt.dxf").write_bytes(CORRUPT_BYTES)
        (outdir / "t20_corrupt.expected.json").write_bytes(jdump({
            "schema": SCHEMA, "disclaimer": DISCLAIMER, "case": "t20_corrupt", "t_ids": ["T-20"],
            "file": "t20_corrupt.dxf", "expected": {"read_status": "READ_FAILED", "quantity_rows": 0,
                                                    "set_total_rows": 0}}))
    finally:
        ezdxf.options.write_fixed_meta_data_for_testing = saved
    files = sorted(p.name for p in outdir.glob("*.dxf"))
    manifest = {"schema": SCHEMA, "disclaimer": DISCLAIMER, "seed": seed, "ezdxf": ezdxf.__version__,
                "python": sys.version.split()[0],
                "files": {f: sha(outdir / f) for f in files},
                "coverage": {t: {"status": s, "cases": cs, "note": n} for t, (s, cs, n) in sorted(COVERAGE.items())},
                "items_synthetic": {k: v[1] for k, v in FIX.items()} | {
                    "BREAKER": "SYN-BREAKER", "LIGHT_DYN": "SYN-LIGHT-DYN"},
                "rules": RULES}
    (outdir / "manifest.json").write_bytes(jdump(manifest))
    return manifest


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    a = ap.parse_args()
    m = generate(a.out, a.seed)
    print(f"wrote {len(m['files'])} DXF files to {a.out}")
    for t, v in m["coverage"].items():
        print(f"  {t}: {v['status']}")
