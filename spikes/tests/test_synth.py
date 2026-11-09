"""Tests for the F-012 synthetic generator (spike). Self-consistency only - not real accuracy (D-004)."""
import ast
import json
from pathlib import Path

import ezdxf
import pytest
from ezdxf import recover

import generate as G

SEED = 20261109


@pytest.fixture(scope="module")
def out(tmp_path_factory):
    d = tmp_path_factory.mktemp("synth")
    G.generate(d, SEED)
    return d


def test_deterministic_same_seed(out, tmp_path):
    G.generate(tmp_path, SEED)
    names = sorted(p.name for p in out.iterdir())
    assert names == sorted(p.name for p in tmp_path.iterdir())
    for n in names:
        assert (out / n).read_bytes() == (tmp_path / n).read_bytes(), n


def test_different_seed_changes_truth(out, tmp_path):
    G.generate(tmp_path, SEED + 1)
    a = json.loads((out / "t01_basic.expected.json").read_text(encoding="utf-8"))
    b = json.loads((tmp_path / "t01_basic.expected.json").read_text(encoding="utf-8"))
    assert a["instances"] != b["instances"]


def test_every_dxf_reopens_and_audits_clean(out):
    checked = 0
    for p in sorted(out.glob("*.dxf")):
        if p.name == "t20_corrupt.dxf":
            continue
        doc = ezdxf.readfile(p)
        aud = doc.audit()
        assert not aud.errors, (p.name, [e.message for e in aud.errors])
        checked += 1
    assert checked >= 25


def test_corrupt_file_fails_to_read(out):
    with pytest.raises(Exception):
        ezdxf.readfile(out / "t20_corrupt.dxf")


def test_insunits_missing_and_zero(out):
    miss = ezdxf.readfile(out / "t07_insunits_missing.dxf")
    zero = ezdxf.readfile(out / "t07_insunits_zero.dxf")
    assert "$INSUNITS" not in miss.header
    assert zero.header["$INSUNITS"] == 0
    assert ezdxf.readfile(out / "t06_m_file.dxf").header["$INSUNITS"] == 6


def test_expected_attribution_and_handles(out):
    """Every expected instance handle exists in the DXF, and every scenario's equation holds."""
    n_checked = 0
    for ep in sorted(out.glob("*.expected.json")):
        e = json.loads(ep.read_text(encoding="utf-8"))
        assert "자기 일관성" in e["disclaimer"]
        if "instances" not in e:
            continue
        doc = ezdxf.readfile(out / e["file"])
        for inst in e["instances"]:
            ent = doc.entitydb.get(inst["handle"])
            assert ent is not None and ent.dxftype() == "INSERT" and ent.dxf.name == inst["block"], (ep.name, inst["key"])
            for h in inst["insert_path"]:
                assert doc.entitydb.get(h).dxftype() == "INSERT"
            n_checked += 1
        for name, sc in e["scenarios"].items():
            assert sc["attribution"]["equation_holds"], (ep.name, name)
            for w in sc["warnings"]:
                if "handle" in w:
                    assert doc.entitydb.get(w["handle"]) is not None, (ep.name, w)
    assert n_checked > 100


def test_independent_insert_count_matches_truth_t01(out):
    """Cross-check with a trivially independent count (INSERTs in modelspace) - flat case only."""
    e = json.loads((out / "t01_basic.expected.json").read_text(encoding="utf-8"))
    doc = ezdxf.readfile(out / "t01_basic.dxf")
    assert len(list(doc.modelspace().query("INSERT"))) == len(e["instances"])
    gen = e["extra"]["generation_counts"]
    assert sum(gen.values()) == sum(e["scenarios"]["default"]["quantities"].values())
    assert e["scenarios"]["default"]["warnings"] == []


def test_nested_formula_t02(out):
    e = json.loads((out / "t02_nested.expected.json").read_text(encoding="utf-8"))
    g = e["extra"]["generation"]
    p, q = g["UNIT_2L_top"], g["FLOOR_3L_top"]
    qty = e["scenarios"]["default"]["quantities"]
    assert qty["SYN-LIGHT-A"] == 2 * (p + 2 * q)
    assert qty["SYN-OUTLET-2P"] == p + 2 * q
    assert qty["SYN-SWITCH-1G"] == q


def test_t03_warning_counts(out):
    e = json.loads((out / "t03_nested_match_hidden.expected.json").read_text(encoding="utf-8"))
    g = e["extra"]["generation"]
    d = e["scenarios"]["default"]
    assert len([w for w in d["warnings"] if w["code"] == "NESTED_MATCH_HIDDEN"]) == g["panels"] + g["wrappers"]
    assert e["scenarios"]["descend_all"]["warnings"] == []
    assert "SYN-LIGHT-A" not in d["quantities"]
    assert e["scenarios"]["descend_all"]["quantities"]["SYN-LIGHT-A"] == g["wrappers"] * g["lights_per_wrapper"]


def test_t14_minsert_12(out):
    e = json.loads((out / "t14_minsert.expected.json").read_text(encoding="utf-8"))
    assert e["scenarios"]["default"]["quantities"]["SYN-OUTLET-2P"] == 22
    doc = ezdxf.readfile(out / "t14_minsert.dxf")
    total = sum(len(list(i.multi_insert())) for i in doc.modelspace().query("INSERT"))
    assert total == 22


def test_dynamic_resolution_matches_truth(out):
    from ezdxf import dynblkhelper as dbh
    e = json.loads((out / "t04_dynamic.expected.json").read_text(encoding="utf-8"))
    doc = ezdxf.readfile(out / "t04_dynamic.dxf")
    for inst in e["instances"]:
        d = dbh.get_dynamic_block_definition(doc.entitydb.get(inst["handle"]), doc)
        want = inst["tags"].get("original_name")
        assert (d.name if d else None) == want, inst["key"]


def test_all_t_ids_covered(out):
    m = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    for i in range(1, 22):
        assert f"T-{i:02d}" in m["coverage"], i
    assert all(v["status"] in ("SYNTHESIZED", "PARTIAL", "NOT_SYNTHESIZABLE") for v in m["coverage"].values())


def test_generator_imports_no_aggregation_code():
    src = Path(G.__file__).read_text(encoding="utf-8")
    mods = set()
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.Import):
            mods |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom):
            mods.add((n.module or "").split(".")[0])
    assert "auto_bim" not in mods
    assert not any("takeoff" in m or "parsing" in m for m in mods), mods


def test_unit_warning_codes_d014(out):
    for n in ("t07_insunits_missing", "t07_insunits_zero"):
        e = json.loads((out / f"{n}.expected.json").read_text(encoding="utf-8"))
        codes = [w["code"] for w in e["scenarios"]["user_mm"]["warnings"]]
        assert codes == ["UNIT_USER_SET"], codes
        assert e["scenarios"]["default"]["quantities"] == {}
        assert e["scenarios"]["default"]["file_status"] == "UNIT_UNKNOWN"
    e = json.loads((out / "t06_mm_file.expected.json").read_text(encoding="utf-8"))
    assert [w["code"] for w in e["scenarios"]["user_override_m"]["warnings"]] == ["UNIT_OVERRIDE"]
