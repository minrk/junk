import tempfile
import lzma
from pathlib import Path

with tempfile.TemporaryDirectory() as td:
    path = Path(td) / "test.bz2"
    with lzma.open(path, mode="wt") as f:
        f.write("testdata")
    with lzma.open(path, mode="rt") as f:
        assert f.read().strip() == "testdata"

print("ok")
