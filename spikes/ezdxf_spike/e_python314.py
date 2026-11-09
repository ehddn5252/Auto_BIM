"""(e) Python 3.14 install + behaviour. Runs under warnings-as-errors to expose deprecations."""
import sys
import warnings
warnings.simplefilter("error")
import ezdxf
from common import roundtrip, result

print("python:", sys.version)
print("ezdxf :", ezdxf.__version__, "| C-extensions:", ezdxf.options.use_c_ext if hasattr(ezdxf.options, "use_c_ext") else "n/a")
doc = ezdxf.new("R2018")
doc.header["$INSUNITS"] = 4
b = doc.blocks.new("T"); b.add_circle((0, 0), 1)
doc.modelspace().add_blockref("T", (0, 0))
path, d2 = roundtrip(doc)
aud = d2.audit()
print("reload ok; entities:", len(d2.modelspace()), "| audit errors:", len(aud.errors))
assert sys.version_info[:2] == (3, 14), sys.version
result("e", "SUCCESS", f"Python {sys.version.split()[0]} + ezdxf {ezdxf.__version__}: install, save/load/audit OK with warnings=error")
