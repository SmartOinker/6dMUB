#!/usr/bin/env python3
"""Mutation test harness for the OpenAI MUB-6 saved-run checker (check_records.py).

Usage (run from outside the downloaded directory):
    python3 mutate.py BASE_EXEC_DIR CHECKER_PY WORK_DIR OUT_JSON

BASE_EXEC_DIR : untouched copy of saved-run/execution (data/, results/, commands.json)
CHECKER_PY    : copy of the downloaded check_records.py (run with `python3 -I`)
WORK_DIR      : scratch dir (must be under /home/claude/oai_cert); one hard-link
                copy of BASE_EXEC_DIR per mutant is made, and ONLY the mutated
                file is replaced by a fresh inode (os.replace), so the base is
                never modified.
The downloaded checker is only run as a subprocess reading the mutated copy.

Each mutation is a function (root: Path) -> description-dict. The harness runs the
checker, records exit code + the "error" message, and writes OUT_JSON.
"""
import json, os, shutil, struct, subprocess, sys, time
from pathlib import Path

BASE, CHECKER, WORK, OUT = map(Path, sys.argv[1:5])


# ---------- low level helpers -------------------------------------------------
def rewrite(path: Path, data: bytes):
    """Replace file content with a NEW inode (hard-linked base stays intact)."""
    tmp = path.with_name(path.name + ".tmpmut")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def records(path: Path):
    """Parse a record file -> (header_count, [bytes of each record])."""
    d = path.read_bytes()
    n = struct.unpack("<Q", d[:8])[0]
    off, recs = 8, []
    for _ in range(n):
        k = struct.unpack("<i", d[off:off + 4])[0]
        size = 356 + 288 * k
        recs.append(d[off:off + size])
        off += size
    assert off == len(d)
    return n, recs


def write_records(path: Path, recs, count=None):
    rewrite(path, struct.pack("<Q", len(recs) if count is None else count) + b"".join(recs))


# field layout inside one record: int k | p[36] | T[k][36] | C n0 id ort hor mnorm froot r
SCALARS = ["C", "n0", "id", "ort", "hor", "mnorm", "froot", "r"]


def scalar_off(rec, name):
    k = struct.unpack("<i", rec[:4])[0]
    return 4 + 8 * (36 + 36 * k) + 8 * SCALARS.index(name)


def get_d(rec, off): return struct.unpack("<d", rec[off:off + 8])[0]


def set_d(rec, off, v): return rec[:off] + struct.pack("<d", v) + rec[off + 8:]


def sub_text(path: Path, old: str, new: str, count=1):
    t = path.read_text()
    assert old in t, (path, old)
    rewrite(path, t.replace(old, new, count).encode())


def edit_json(root, fn):
    p = root / "commands.json"
    doc = json.loads(p.read_text())
    fn(doc["children"])
    rewrite(p, (json.dumps(doc, indent=2) + "\n").encode())


# ---------- mutations ---------------------------------------------------------
M = []  # (id, category, function)


def mut(mid, cat):
    def deco(f):
        M.append((mid, cat, f)); return f
    return deco


@mut("M01", "delete one record (header fixed)")
def _(r):
    p = r / "data/fine.bin"; n, recs = records(p); i = 10000
    write_records(p, recs[:i] + recs[i + 1:])
    return dict(file="data/fine.bin", change=f"deleted record #{i}, header {n}->{n-1}")


@mut("M02", "delete one record (header NOT fixed)")
def _(r):
    p = r / "data/coarse2.bin"; n, recs = records(p); i = 100
    write_records(p, recs[:i] + recs[i + 1:], count=n)
    return dict(file="data/coarse2.bin", change=f"deleted record #{i}, header left at {n}")


@mut("M03", "duplicate one record (header fixed)")
def _(r):
    p = r / "data/batches/f5.bin"; n, recs = records(p); i = 7
    write_records(p, recs[:i + 1] + [recs[i]] + recs[i + 1:])
    return dict(file="data/batches/f5.bin", change=f"record #{i} duplicated, header {n}->{n+1}")


@mut("M04", "small numeric change to a phase p[0] in a record, one file only (fine.bin)")
def _(r):
    p = r / "data/fine.bin"; n, recs = records(p); i = 5000
    o = 4; before = get_d(recs[i], o); recs[i] = set_d(recs[i], o, before + 1e-6)
    write_records(p, recs)
    return dict(file="data/fine.bin", change=f"record #{i} p[0] {before!r} -> {before+1e-6!r}")


@mut("M05", "small numeric change to p[0] in coarse0.bin record (upstream, no consistency partner stored downstream)")
def _(r):
    p = r / "data/coarse0.bin"; n, recs = records(p); i = 300
    o = 4; before = get_d(recs[i], o); recs[i] = set_d(recs[i], o, before + 0.05)
    write_records(p, recs)
    return dict(file="data/coarse0.bin", change=f"record #{i} p[0] {before!r} -> {before+0.05!r} (shift 0.05 rad)")


@mut("M06", "same small change to a record applied consistently in fine.bin AND its batch copy")
def _(r):
    pf = r / "data/fine.bin"; n, recs = records(pf); i = 5000   # batch 19, index 136
    o = 4; before = get_d(recs[i], o); recs[i] = set_d(recs[i], o, before + 0.01); write_records(pf, recs)
    pb = r / "data/batches/f19.bin"; nb, rb = records(pb); j = i - 256 * 19
    rb[j] = set_d(rb[j], o, get_d(rb[j], o) + 0.01); write_records(pb, rb)
    return dict(file="data/fine.bin + data/batches/f19.bin", change=f"record fine#{i} (batch19#{j}) p[0] shifted by +0.01 rad in both")


@mut("M07", "change a record inside a saved C-failure file")
def _(r):
    p = r / "data/batches/bad3.bin"; n, recs = records(p)
    o = 4; before = get_d(recs[0], o); recs[0] = set_d(recs[0], o, before + 1e-12); write_records(p, recs)
    return dict(file="data/batches/bad3.bin", change=f"record #0 p[0] {before!r} -> +1e-12 (failure no longer equals its input record)")


@mut("M08", "swap two records (fine.bin only)")
def _(r):
    p = r / "data/fine.bin"; n, recs = records(p); a, b = 100, 200
    recs[a], recs[b] = recs[b], recs[a]; write_records(p, recs)
    return dict(file="data/fine.bin", change=f"swapped records #{a} and #{b} (same batch 0)")


@mut("M09", "swap two records consistently in fine.bin and batch f0.bin")
def _(r):
    a, b = 100, 200
    for name in ("data/fine.bin", "data/batches/f0.bin"):
        p = r / name; n, recs = records(p); recs[a], recs[b] = recs[b], recs[a]; write_records(p, recs)
    return dict(file="data/fine.bin + data/batches/f0.bin", change=f"swapped records #{a},#{b} in both (batch 0 has initial-C failures? bad0 is empty)")


@mut("M10", "truncate a record file")
def _(r):
    p = r / "data/coarse1.bin"; d = p.read_bytes(); rewrite(p, d[:-100])
    return dict(file="data/coarse1.bin", change="removed last 100 bytes")


@mut("M11", "truncate the centers file (drop last row, count header kept)")
def _(r):
    p = r / "data/centers.txt"; L = p.read_text().splitlines(); rewrite(p, ("\n".join(L[:-1]) + "\n").encode())
    return dict(file="data/centers.txt", change="last center row removed, header still 249878")


@mut("M12", "remove a seed centre consistently (header decremented) - leaves a seed region uncovered")
def _(r):
    p = r / "data/centers.txt"; L = p.read_text().splitlines(); h = L[0].split(); i = 5000
    row = L[1 + i]; del L[1 + i]; L[0] = f"{h[0]} {int(h[1]) - 1}"
    rewrite(p, ("\n".join(L) + "\n").encode())
    return dict(file="data/centers.txt", change=f"deleted center row #{i} ({row}); header -> {int(h[1])-1}")


@mut("M13", "alter one coordinate of a seed centre (still in range) - shifts a seed cell")
def _(r):
    p = r / "data/centers.txt"; L = p.read_text().splitlines(); i = 5000
    f = L[1 + i].split(); old = f[0]; f[0] = str((int(f[0]) + 1) % 112); L[1 + i] = " ".join(f)
    rewrite(p, ("\n".join(L) + "\n").encode())
    return dict(file="data/centers.txt", change=f"center row #{i} column 0: {old}->{f[0]}")


@mut("M14", "inflate a stored radius within the global cap (coarse0 rec -> 0.126)")
def _(r):
    p = r / "data/coarse0.bin"; n, recs = records(p); i = 300; o = scalar_off(recs[i], "r")
    before = get_d(recs[i], o); recs[i] = set_d(recs[i], o, 0.126); write_records(p, recs)
    return dict(file="data/coarse0.bin", change=f"record #{i} radius {before!r} -> 0.126")


@mut("M15", "radius over cap (fine.bin rec radius 0.0161 > .016)")
def _(r):
    p = r / "data/fine.bin"; n, recs = records(p); i = 5000; o = scalar_off(recs[i], "r")
    before = get_d(recs[i], o); recs[i] = set_d(recs[i], o, 0.0161); write_records(p, recs)
    return dict(file="data/fine.bin", change=f"record #{i} radius {before!r} -> 0.0161")


@mut("M16", "weaken a stored bound within the checker's cap: Root residual froot -> 9e-7 (coarse0 rec)")
def _(r):
    p = r / "data/coarse0.bin"; n, recs = records(p); i = 300; o = scalar_off(recs[i], "froot")
    before = get_d(recs[i], o); recs[i] = set_d(recs[i], o, 9e-7); write_records(p, recs)
    return dict(file="data/coarse0.bin", change=f"record #{i} froot {before!r} -> 9e-7 (checker cap 1e-6)")


@mut("M17", "stored bound beyond cap: orthogonality residual ort -> 1e-3")
def _(r):
    p = r / "data/coarse0.bin"; n, recs = records(p); i = 300; o = scalar_off(recs[i], "ort")
    before = get_d(recs[i], o); recs[i] = set_d(recs[i], o, 1e-3); write_records(p, recs)
    return dict(file="data/coarse0.bin", change=f"record #{i} ort {before!r} -> 1e-3 (cap 1e-5)")


@mut("M18", "forge verdict: C.batch3 failures hidden (bad file emptied, log, exit code all rewritten)")
def _(r):
    rewrite(r / "data/batches/bad3.bin", struct.pack("<Q", 0))
    sub_text(r / "results/C.batch3.txt", "result done256 bad2 (graph0 cap2 over0 cluster0)",
             "result done256 bad0 (graph0 cap0 over0 cluster0)")
    edit_json(r, lambda c: c["C.batch3"].__setitem__("returncode", 0))
    return dict(file="data/batches/bad3.bin, results/C.batch3.txt, commands.json", change="2 cap failures removed consistently; fallback input list unchanged-by-hand")


@mut("M19", "flip exit status in commands.json only (C.batch3 returncode 1 -> 0)")
def _(r):
    edit_json(r, lambda c: c["C.batch3"].__setitem__("returncode", 0))
    return dict(file="commands.json", change="C.batch3 returncode 1->0")


@mut("M20", "recategorise failures in log (cap2 -> cluster2) only")
def _(r):
    sub_text(r / "results/C.batch3.txt", "bad2 (graph0 cap2 over0 cluster0)", "bad2 (graph0 cap0 over0 cluster2)")
    return dict(file="results/C.batch3.txt", change="2 'graph step cap' failures relabelled as 'clustering failure'")


@mut("M21", "make a final-C failure file nonempty")
def _(r):
    n, recs = records(r / "data/fb1.bin")
    write_records(r / "data/fb1cbad0.bin", [recs[0]])
    return dict(file="data/fb1cbad0.bin", change="inserted 1 record (copy of fb1 #0) into final-C0 failure file")


@mut("M22", "delete last fb1 record, consistently forging logs (fallback B + final C part 2)")
def _(r):
    p = r / "data/fb1.bin"; n, recs = records(p); assert n == 1127
    write_records(p, recs[:-1])
    # B fallback log: terminal output count + any '->' counts above new total
    f = r / "results/C.Bfallback.txt"; t = f.read_text()
    t = t.replace("result 1127 bad 0", "result 1126 bad 0").replace("->1127", "->1126")
    rewrite(f, t.encode())
    # record #1126 belongs to part 1126 % 4 == 2 -> final C part 2 now has 281
    f2 = r / "results/C.final2.txt"; sub_text(f2, "result done282", "result done281")
    return dict(file="data/fb1.bin, results/C.Bfallback.txt, results/C.final2.txt",
                change="dropped last Stage-B-fallback output record and edited the 3 count fields that mention it")


@mut("M23", "delete coarse0 record, A0 log edited consistently (G764->G763) - downstream B parent count unchanged")
def _(r):
    p = r / "data/coarse0.bin"; n, recs = records(p); write_records(p, recs[:-1])
    f = r / "results/A0.txt"; t = f.read_text()
    t = t.replace("G764 ", "G763 ").replace("global764", "global763"); rewrite(f, t.encode())
    return dict(file="data/coarse0.bin, results/A0.txt", change="last coarse0 record dropped; A0 log counts 764->763")


@mut("M24", "extra stray file in data/")
def _(r):
    (r / "data/extra.bin").write_bytes(struct.pack("<Q", 0))
    return dict(file="data/extra.bin", change="added empty-record file not named in the schedule")


@mut("M25", "phase value out of declared bound |p|<=4 (set p[3]=5 in mid.bin rec)")
def _(r):
    p = r / "data/mid.bin"; n, recs = records(p); i = 50; o = 4 + 8 * 3
    before = get_d(recs[i], o); recs[i] = set_d(recs[i], o, 5.0); write_records(p, recs)
    return dict(file="data/mid.bin", change=f"record #{i} p[3] {before!r} -> 5.0")


@mut("M26", "single bit flip in low mantissa bit of a p entry (mid.bin rec 50 p[3])")
def _(r):
    p = r / "data/mid.bin"; n, recs = records(p); i = 50; o = 4 + 8 * 3
    b = bytearray(recs[i]); b[o] ^= 1; recs[i] = bytes(b); write_records(p, recs)
    return dict(file="data/mid.bin", change=f"record #{i} p[3] lowest mantissa bit flipped")


# ---------- runner ------------------------------------------------------------
def run_checker(root):
    t = time.time()
    pr = subprocess.run(["python3", "-I", str(CHECKER), str(root)], cwd="/home",
                        capture_output=True, text=True, timeout=480)
    dt = time.time() - t
    try:
        doc = json.loads(pr.stdout)
    except Exception:
        doc = {"result": "UNPARSEABLE", "error": (pr.stdout + pr.stderr)[-400:]}
    return pr.returncode, doc.get("result"), doc.get("error"), round(dt, 1), pr.stderr[-300:]


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    out = []
    for mid, cat, fn in M:
        root = WORK / mid
        if root.exists(): shutil.rmtree(root)
        subprocess.run(["cp", "-al", str(BASE), str(root)], check=True)  # hard links
        try:
            desc = fn(root)
        except Exception as e:
            out.append(dict(id=mid, category=cat, error_in_harness=repr(e))); print(mid, "HARNESS ERROR", e); shutil.rmtree(root); continue
        rc, res, err, dt, se = run_checker(root)
        rec = dict(id=mid, category=cat, **desc, exit_code=rc, result=res, message=err, seconds=dt,
                   detected=(rc != 0), stderr=se)
        out.append(rec)
        print(f"{mid} rc={rc} {'CAUGHT' if rc else 'SURVIVED'} | {cat} | {err}")
        shutil.rmtree(root)
    OUT.write_text(json.dumps(out, indent=2))


main()
