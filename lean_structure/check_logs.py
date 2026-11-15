#!/usr/bin/env python3
"""Check the stored build records of the structure Lean project against its sources (no Lean needed).

1. every source file has the SHA-256 recorded in hash-manifest.json;
2. logs/build-final.log ends with a successful build;
3. logs/axioms-all.log lists every audited theorem with axioms inside {propext, Classical.choice, Quot.sound};
4. every audited theorem name occurs as a declaration in the sources;
5. the sources contain no `sorry`, `admit`, `native_decide` or `axiom` declaration outside comments.
A full rebuild is `lake build` in this directory (Lean v4.35.0, Mathlib pinned in lake-manifest.json).
"""
import hashlib, json, pathlib, re, sys
D = pathlib.Path(__file__).resolve().parent
ok = True
def check(name, cond, detail=""):
    global ok
    print(("[PASS] " if cond else "[FAIL] ") + name + (": " + detail if detail else ""))
    ok = ok and bool(cond)
man = json.loads((D / "hash-manifest.json").read_text())["files"]
# The two provenance JSON files are excluded: local user paths were removed from them for the submission.
REDACTED = {"integration-provenance.json", "verification.json"}
man = {f: h for f, h in man.items() if f not in REDACTED}
bad = [f for f, h in man.items() if not (D / f).is_file() or hashlib.sha256((D / f).read_bytes()).hexdigest() != h]
check("source hashes match hash-manifest.json", not bad, f"{len(man)} files, {sum(f.endswith('.lean') for f in man)} Lean files" + (f", mismatches {bad}" if bad else ""))
build = (D / "logs/build-final.log").read_text()
m = re.search(r"Build completed successfully \((\d+) jobs\)", build)
check("build log reports success", m is not None and "error:" not in build, m.group(0) if m else "no success line")
allowed = {"propext", "Classical.choice", "Quot.sound"}
names, used = [], set()
axlog = (D / "logs/axioms-all.log").read_text()
for m in re.finditer(r"'([^']+)' depends on axioms: \[([^\]]*)\]", axlog):
    names.append(m.group(1)); used |= {a.strip() for a in m.group(2).split(",") if a.strip()}
names += re.findall(r"'([^']+)' does not depend on any axioms", axlog)
check("axiom log: audited theorems", len(names) == 394, f"{len(names)} theorems")
check("axiom log: only standard axioms", used <= allowed, ", ".join(sorted(used)))
def strip_comments(s):
    s = re.sub(r"/-.*?-/", " ", s, flags=re.S)
    return re.sub(r"--.*", " ", s)
src = {p.name: strip_comments(p.read_text()) for p in D.glob("*.lean")}
alltext = "\n".join(src.values())
decl = set(re.findall(r"(?:theorem|lemma)\s+([A-Za-z0-9_.']+)", alltext))
missing = [n for n in names if n.split(".")[-1] not in decl and n not in decl]
check("every audited theorem is declared in the sources", not missing, f"{len(decl)} declarations found" + (f", missing {missing[:5]}" if missing else ""))
hits = [(f, w) for f, t in src.items() for w in ("sorry", "admit", "native_decide") if re.search(r"\b" + w + r"\b", t)]
hits += [(f, "axiom") for f, t in src.items() if re.search(r"^\s*axiom\s", t, flags=re.M)]
check("no sorry / admit / native_decide / axiom declarations in the sources", not hits, str(hits) if hits else f"{len(src)} files scanned")
# ---- second build (Open Math OS, Linux x86-64), logs/rebuild_openmathos/
R = D / "logs/rebuild_openmathos"
b2 = (R / "BUILD_LOG.txt").read_text()
m2 = re.search(r"Build completed successfully \((\d+) jobs\)", b2)
check("second build: log reports success", m2 is not None and "error:" not in b2, m2.group(0) if m2 else "no success line")
ax2 = (R / "AXIOMS_LOG.txt").read_text()
n2 = re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", ax2)
u2 = set()
for _, a_ in n2:
    u2 |= {x.strip() for x in a_.split(",") if x.strip()}
check("second build: audited theorems and axioms", len(n2) == 394 and u2 <= allowed and {x for x, _ in n2} == set(names), f"{len(n2)} theorems, axioms {', '.join(sorted(u2))}")
got = {}
for line in (R / "LEAN_SHA256.txt").read_text().splitlines():
    h, f = line.split(); got[f.lstrip("*").lstrip("./")] = h
full = json.loads((D / "hash-manifest.json").read_text())["files"]
bad2 = [f for f in got if full.get(f) != got[f]] + [f for f in full if f.endswith(".lean") and f not in got]
check("second build: the Lean files built there have the manifest hashes", not bad2, f"{len(got)} files" + (f", problems {bad2}" if bad2 else ""))
check("second build: sorry scan empty", (R / "SORRY_GREP.txt").read_text().strip() == "")
print("OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
