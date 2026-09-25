"""One sweep across every repo, looking only for what can go.

The ladder normally runs on a change you are about to make. This runs it on
what is already there, because the failure being fixed is the opposite one:
things get added and nothing ever gets taken away, so the ladder never gets
asked about code that already exists.

Rung 1 is applied to the repos themselves before anything else: a repo that is
a copy of another repo is not swept, it is reported as the copy it is. No point
tidying two of something.

It prints. It does not delete. Deletion is the one move you cannot take back,
and a tool that guesses wrong at three in the morning across seventeen repos is
exactly the thing this skill exists to prevent. `--remove-exact-copies` acts on
one category only, the one where the bytes are provably still present under
another name in the same repo.

    python scripts/sweep.py                    every repo under the root
    python scripts/sweep.py --root F:/code     somewhere else
    python scripts/sweep.py --repo veskara     just one
    python scripts/sweep.py --remove-exact-copies    the only destructive flag
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist",
             "build", ".next", ".cache", "site-packages", ".pytest_cache",
             "staging", ".mypy_cache", ".tox", "target", "vendor"}
TEXT_SUFFIX = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".html",
               ".css", ".md", ".json", ".txt", ".ps1", ".sh", ".toml", ".yml",
               ".yaml", ".cfg", ".ini", ".rs", ".go", ".java", ".c", ".h"}
# Files whose whole job is to be found by name, so nothing has to mention them.
ENTRY = re.compile(
    r"^(index\.\w+|main\.\w+|__init__\.py|__main__\.py|conftest\.py|setup\.py|"
    r"README.*|LICENSE.*|AGENTS\.md|CLAUDE\.md|.*\.test\.\w+|test_.*\.py|"
    r"package(-lock)?\.json|requirements.*\.txt|pyproject\.toml|"
    r"tsconfig\.json|\..*|_headers|_redirects|robots\.txt|sitemap\.xml)$", re.I)
SCRATCH = re.compile(r"(\.bak\d*$|\.old$|\.orig$|~$|\.tmp$|\.swp$|"
                     r"[-_ ]copy(\s*\(\d+\))?\.|[-_ ]backup\.|\.rej$)", re.I)


def walk(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            yield Path(dirpath) / name


def digest(path: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def find_repos(root: Path) -> list[Path]:
    repos = []
    for dirpath, dirnames, _ in os.walk(root):
        if ".git" in dirnames:
            repos.append(Path(dirpath))
            dirnames[:] = []          # a repo inside a repo is its own problem
        else:
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    return sorted(repos)


def fingerprint(repo: Path, files: list[Path]) -> set[str]:
    """Content hashes of the tracked-looking source, for repo-vs-repo compare."""
    return {d for d in (digest(f) for f in files
                        if f.suffix.lower() in TEXT_SUFFIX
                        and f.stat().st_size < 2_000_000) if d}


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}GB"


class Repo:
    def __init__(self, path: Path):
        self.path = path
        self.files = [f for f in walk(path) if f.is_file()]
        self.bytes = sum(f.stat().st_size for f in self.files if f.exists())
        self.copy_of: Path | None = None

    @property
    def name(self) -> str:
        return self.path.name

    def text_blob(self) -> str:
        out = []
        for f in self.files:
            if f.suffix.lower() in TEXT_SUFFIX and f.stat().st_size < 1_500_000:
                try:
                    out.append(f.read_text(encoding="utf-8", errors="ignore"))
                except OSError:
                    pass
        return "\n".join(out)

    def scratch(self):
        return [f for f in self.files if SCRATCH.search(f.name)]

    def empties(self):
        return [f for f in self.files
                if f.stat().st_size == 0 and not ENTRY.match(f.name)]

    def exact_copies(self):
        """Same bytes, two names, one repo. The one category safe to remove."""
        by_hash = defaultdict(list)
        for f in self.files:
            if f.stat().st_size > 0 and f.suffix.lower() in TEXT_SUFFIX:
                d = digest(f)
                if d:
                    by_hash[d].append(f)
        return {d: sorted(v, key=lambda p: (len(p.parts), str(p)))
                for d, v in by_hash.items() if len(v) > 1}

    def unmentioned(self, blob: str):
        """Files whose own name appears nowhere else in the repo.

        A heuristic, and it is named as one in the output. Anything loaded by
        glob, by a build allowlist, or by a route the code never spells out
        will look unreferenced and is not. It is a place to look, not a verdict.
        """
        out = []
        for f in self.files:
            if ENTRY.match(f.name) or f.suffix.lower() not in TEXT_SUFFIX:
                continue
            stem = f.stem
            if len(stem) < 4:
                continue
            hits = blob.count(stem)
            if hits <= 1:                    # only its own definition, if that
                out.append(f)
        return out


def report(repos: list[Repo], root: Path) -> list[tuple[Repo, dict]]:
    findings = []
    for r in repos:
        if r.copy_of:
            findings.append((r, {}))
            continue
        blob = r.text_blob()
        findings.append((r, {
            "exact copies": r.exact_copies(),
            "scratch and backup files": r.scratch(),
            "empty files": r.empties(),
            "never mentioned by name": r.unmentioned(blob),
        }))
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=r"F:\code")
    ap.add_argument("--repo", help="only the repo whose folder is named this")
    ap.add_argument("--remove-exact-copies", action="store_true")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.is_dir():
        print(f"no such root: {root}")
        return 2

    print(f"sweeping {root}\n")
    paths = find_repos(root)
    if args.repo:
        paths = [p for p in paths if p.name == args.repo]
        if not paths:
            print(f"no repo named {args.repo}")
            return 2

    repos = []
    for p in paths:
        try:
            repos.append(Repo(p))
        except OSError as e:
            print(f"  skipped {p}: {e}")

    # Rung 1, applied to the repos. A near-copy of another repo does not need
    # tidying; it needs deciding which one is real.
    prints = {r.name: fingerprint(r.path, r.files) for r in repos}
    for i, a in enumerate(repos):
        for b in repos:
            if a is b or not prints[a.name] or a.copy_of:
                continue
            shared = len(prints[a.name] & prints[b.name])
            if shared and shared / len(prints[a.name]) > 0.7 and a.bytes <= b.bytes:
                a.copy_of = b.path

    total = 0
    for r, found in sorted(report(repos, root), key=lambda x: -x[0].bytes):
        rel = r.path.relative_to(root) if r.path.is_relative_to(root) else r.path
        if r.copy_of:
            other = (r.copy_of.relative_to(root)
                     if r.copy_of.is_relative_to(root) else r.copy_of)
            print(f"{rel}  {human(r.bytes)}  {len(r.files)} files")
            print(f"    NOT SWEPT. Over 70% of its source is byte-identical to "
                  f"{other}.")
            print(f"    Rung one: decide which of the two is real before "
                  f"tidying either.\n")
            continue

        lines, reclaim = [], 0
        for label, hits in found.items():
            if label == "exact copies":
                if not hits:
                    continue
                n = sum(len(v) - 1 for v in hits.values())
                b = sum(v[0].stat().st_size * (len(v) - 1) for v in hits.values())
                reclaim += b
                lines.append(f"    {n} exact copies, {human(b)}")
                for v in list(hits.values())[:3]:
                    keep = v[0].relative_to(r.path)
                    for dup in v[1:][:2]:
                        lines.append(f"        {dup.relative_to(r.path)}"
                                     f"  ==  {keep}")
            elif hits:
                b = sum(f.stat().st_size for f in hits)
                if label != "never mentioned by name":
                    reclaim += b
                lines.append(f"    {len(hits)} {label}, {human(b)}"
                             + ("  (heuristic, check before trusting)"
                                if label == "never mentioned by name" else ""))
                for f in sorted(hits, key=lambda p: -p.stat().st_size)[:4]:
                    lines.append(f"        {f.relative_to(r.path)}"
                                 f"  {human(f.stat().st_size)}")
        total += reclaim
        print(f"{rel}  {human(r.bytes)}  {len(r.files)} files"
              + (f"  ->  {human(reclaim)} removable" if reclaim else "  ->  nothing to take away"))
        print("\n".join(lines) + ("\n" if lines else ""))

    print(f"\n{human(total)} is removable across {len(repos)} repos without "
          f"deciding anything.")

    if args.remove_exact_copies:
        gone = 0
        for r in repos:
            if r.copy_of:
                continue
            for v in r.exact_copies().values():
                for dup in v[1:]:
                    try:
                        size = dup.stat().st_size
                        dup.unlink()
                        gone += size
                        print(f"  removed {dup}")
                    except OSError as e:
                        print(f"  could not remove {dup}: {e}")
        print(f"\nremoved {human(gone)}. Every byte is still present under the "
              f"name that was kept.")
    else:
        print("Nothing was deleted. --remove-exact-copies acts on the exact "
              "copies only.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
