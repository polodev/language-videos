#!/usr/bin/env python3
"""Local-only Hindi video import, Whisper matching, review and regeneration queue."""
import argparse
import dataclasses
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import unicodedata

DEFAULT = Path(__file__).resolve().parents[1] / "hindi"
EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm"}


def dump(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def normalize(text):
    text = unicodedata.normalize("NFC", text).lower()
    return " ".join("".join(c if unicodedata.category(c)[0] in "LMN" else " " for c in text).split())


class Library:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.media = self.root / "Videos"
        self.local = self.root / ".local"
        (self.media / "incoming").mkdir(parents=True, exist_ok=True)
        self.local.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.root / "library.sqlite3")
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS prompts (
          id INTEGER PRIMARY KEY, data TEXT NOT NULL, prompt TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS assets (
          id INTEGER PRIMARY KEY, source TEXT NOT NULL, original_name TEXT NOT NULL,
          sha256 TEXT NOT NULL, path TEXT NOT NULL, probe TEXT NOT NULL,
          transcript TEXT, model TEXT, candidates TEXT,
          prompt_id INTEGER REFERENCES prompts(id), match_method TEXT,
          review TEXT NOT NULL DEFAULT 'pending', note TEXT NOT NULL DEFAULT '',
          present INTEGER NOT NULL DEFAULT 1,
          UNIQUE(source, sha256));
        CREATE TABLE IF NOT EXISTS events (
          id INTEGER PRIMARY KEY, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
          asset_id INTEGER REFERENCES assets(id), action TEXT NOT NULL, detail TEXT NOT NULL);
        """)
        videos = json.loads((self.root / "videos.json").read_text())
        prompts = json.loads((self.root / "flow-prompts.json").read_text())
        for video in videos:
            number = video["video_number"]
            self.db.execute("INSERT INTO prompts VALUES (?,?,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data,prompt=excluded.prompt",
                            (number, json.dumps(video, ensure_ascii=False), prompts[f"prompt_{number}"]))
        self.db.commit()

    def event(self, asset, action, detail):
        self.db.execute("INSERT INTO events(asset_id,action,detail) VALUES (?,?,?)", (asset, action, detail))

    def asset(self, number):
        asset = self.db.execute("SELECT * FROM assets WHERE id=?", (number,)).fetchone()
        if asset is None:
            raise ValueError(f"Unknown asset {number}")
        return asset

    def path(self, asset):
        return self.root / asset["path"]

    def import_folder(self, source):
        source = Path(source).expanduser().resolve()
        # os.walk must not silently turn a macOS permission denial into an empty import.
        found = []
        def fail(error):
            raise error
        for parent, dirs, files in os.walk(source, onerror=fail):
            dirs[:] = [d for d in dirs if d not in (".local", "incoming")]
            for name in files:
                path = Path(parent) / name
                if path.suffix.lower() in EXTENSIONS:
                    found.append(path)
        if not source.is_dir():
            raise ValueError(f"Source directory does not exist: {source}")
        imported = skipped = 0
        known_paths = {self.path(a).resolve() for a in self.db.execute("SELECT * FROM assets")}
        for source_file in sorted(found):
            if source_file.resolve() in known_paths:
                skipped += 1
                continue
            checksum = digest(source_file)
            if self.db.execute("SELECT 1 FROM assets WHERE source=? AND sha256=?", (str(source_file), checksum)).fetchone():
                skipped += 1
                continue
            # Include the source path hash so identically named downloads never overwrite each other.
            source_key = hashlib.sha256(str(source_file).encode()).hexdigest()[:12]
            target = self.media / "incoming" / f"{source_key}-{checksum[:12]}{source_file.suffix.lower()}"
            if target.exists() and digest(target) != checksum:
                raise ValueError(f"Destination collision: {target}")
            if not target.exists():
                temporary = target.with_suffix(target.suffix + ".copying")
                shutil.copy2(source_file, temporary)
                if digest(temporary) != checksum:
                    raise ValueError(f"Copy verification failed: {source_file}")
                temporary.replace(target)
            result = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(target)], capture_output=True, text=True)
            probe = json.loads(result.stdout) if result.returncode == 0 else {"error": result.stderr.strip()}
            cursor = self.db.execute("INSERT INTO assets(source,original_name,sha256,path,probe) VALUES (?,?,?,?,?)",
                                     (str(source_file), source_file.name, checksum, str(target.relative_to(self.root)), json.dumps(probe)))
            self.event(cursor.lastrowid, "import", str(source_file))
            self.db.commit()
            imported += 1
            print(f"Imported asset {cursor.lastrowid}: {source_file.name}", flush=True)
        self.export()
        return {"discovered": len(found), "imported": imported, "skipped": skipped}

    def transcribe(self, model_name="small", limit=None, start_asset=1, end_asset=2147483647):
        # Never upload audio, fetch weights or silently select an English-only model.
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
        from faster_whisper import WhisperModel
        pending = list(self.db.execute("SELECT * FROM assets WHERE transcript IS NULL AND present=1 AND id BETWEEN ? AND ? ORDER BY id", (start_asset, end_asset)))
        if limit is not None:
            pending = pending[:limit]
        if not pending:
            return {"transcribed": 0}
        model = WhisperModel(model_name, device="cpu", compute_type="int8", cpu_threads=4, local_files_only=True)
        count = 0
        for asset in pending:
            if not self.path(asset).exists():
                continue
            print(f"Transcribing asset {asset['id']} with offline {model_name}…", flush=True)
            try:
                segments, info = model.transcribe(str(self.path(asset)), language="hi", task="transcribe",
                                                 beam_size=5, temperature=0, word_timestamps=True,
                                                 condition_on_previous_text=False, vad_filter=False)
                segments = [dataclasses.asdict(segment) if dataclasses.is_dataclass(segment)
                            else segment._asdict() for segment in segments]
                for segment in segments:
                    segment["words"] = [word if isinstance(word, dict) else
                                        dataclasses.asdict(word) if dataclasses.is_dataclass(word) else word._asdict()
                                        for word in segment.get("words") or []]
                payload = {"text": " ".join(s["text"].strip() for s in segments), "segments": segments,
                           "language": info.language, "model": model_name, "offline": True}
                self.db.execute("UPDATE assets SET transcript=?,model=?,candidates=NULL WHERE id=?",
                                (json.dumps(payload, ensure_ascii=False), model_name, asset["id"]))
                dump(self.local / "transcripts" / f"asset-{asset['id']}.json", payload)
                self.event(asset["id"], "transcribe", model_name)
                self.db.commit()
                count += 1
            except Exception as error:
                self.event(asset["id"], "transcription_error", str(error))
                self.db.commit()
                print(f"Asset {asset['id']} failed: {error}", flush=True)
        self.export()
        return {"transcribed": count}

    def rank(self, transcript):
        from rapidfuzz.fuzz import partial_ratio
        heard = normalize(transcript)
        rankings = []
        for prompt in self.db.execute("SELECT * FROM prompts ORDER BY id"):
            lesson = json.loads(prompt["data"])
            lines = [normalize(s["hindi"]) for s in lesson["sentences"]]
            scores = [partial_ratio(line, heard) if heard else 0 for line in lines]
            # Both Hindi sentences must match; a generic single phrase cannot dominate.
            score = 0.6 * min(scores) + 0.4 * (sum(scores) / len(scores))
            if len(heard.replace(" ", "")) < max(len(s.replace(" ", "")) for s in lines):
                score *= 0.5
            rankings.append({"prompt_id": prompt["id"], "score": round(score, 2), "sentence_scores": scores})
        return sorted(rankings, key=lambda row: (-row["score"], row["prompt_id"]))[:5]

    def match(self, apply_confident=False):
        proposals = []
        for asset in list(self.db.execute("SELECT * FROM assets WHERE transcript IS NOT NULL AND prompt_id IS NULL AND present=1")):
            ranked = self.rank(json.loads(asset["transcript"])["text"])
            self.db.execute("UPDATE assets SET candidates=? WHERE id=?", (json.dumps(ranked), asset["id"]))
            if len(ranked) >= 2 and ranked[0]["score"] >= 92 and min(ranked[0]["sentence_scores"]) >= 88 and ranked[0]["score"] - ranked[1]["score"] >= 12:
                proposals.append((asset["id"], ranked[0]["prompt_id"]))
        self.db.commit()
        assigned = 0
        if apply_confident:
            for asset_id, prompt_id in proposals:
                # Competing takes stay unresolved rather than arbitrarily choosing a winner.
                if sum(p == prompt_id for _, p in proposals) != 1:
                    continue
                if self.db.execute("SELECT 1 FROM assets WHERE prompt_id=? AND present=1 AND review NOT IN ('captioned','bad-audio')", (prompt_id,)).fetchone():
                    continue
                self.assign(asset_id, prompt_id, method="high-confidence-heuristic", refresh=False)
                assigned += 1
        self.export()
        return {"high_confidence_proposals": len(proposals), "assigned": assigned,
                "note": "Scores are fuzzy similarity, not calibrated probabilities; visual/audio review remains required."}

    def assign(self, asset_id, prompt_id, method="manual", refresh=True):
        asset = self.asset(asset_id)
        if not self.db.execute("SELECT 1 FROM prompts WHERE id=?", (prompt_id,)).fetchone():
            raise ValueError(f"Unknown prompt {prompt_id}")
        if asset["prompt_id"] not in (None, prompt_id):
            raise ValueError("Already assigned to a different prompt; inspect the mapping before changing it")
        source = self.path(asset)
        if not source.exists():
            raise ValueError(f"Missing file: {source}")
        destination = self.media / f"{prompt_id}{source.suffix.lower()}"
        conflict = self.db.execute("SELECT id FROM assets WHERE prompt_id=? AND id<>? AND present=1 AND review NOT IN ('captioned','bad-audio')", (prompt_id, asset_id)).fetchone()
        if conflict:
            raise ValueError(f"Prompt {prompt_id} already has asset {conflict['id']}")
        if source != destination:
            if destination.exists():
                raise ValueError(f"Refusing to overwrite {destination}; remove or archive the old take first")
            # Exclusive creation: os.link fails if the destination exists, never overwrites.
            os.link(source, destination)
            source.unlink()
        self.db.execute("UPDATE assets SET path=?,prompt_id=?,match_method=?,present=1 WHERE id=?",
                        (str(destination.relative_to(self.root)), prompt_id, method, asset_id))
        self.event(asset_id, "assign", f"prompt_{prompt_id}: {method}")
        self.db.commit()
        if refresh:
            self.export()

    def review(self, asset_id, state, note=""):
        self.asset(asset_id)
        self.db.execute("UPDATE assets SET review=?,note=? WHERE id=?", (state, note, asset_id))
        self.event(asset_id, "review", f"{state}: {note}")
        self.db.commit()
        self.export()

    def scan(self):
        for asset in list(self.db.execute("SELECT * FROM assets")):
            present = int(self.path(asset).is_file())
            if present != asset["present"]:
                self.event(asset["id"], "found" if present else "missing", asset["path"])
                self.db.execute("UPDATE assets SET present=? WHERE id=?", (present, asset["id"]))
        self.db.commit()
        self.export()

    def export(self, include_unmatched=False):
        assets = [dict(row) for row in self.db.execute("SELECT * FROM assets ORDER BY id")]
        for asset in assets:
            for key in ("probe", "transcript", "candidates"):
                asset[key] = json.loads(asset[key]) if asset[key] else None
        prompts = []
        regeneration = {}
        for row in self.db.execute("SELECT * FROM prompts ORDER BY id"):
            linked = [asset for asset in assets if asset["prompt_id"] == row["id"]]
            usable = [a for a in linked if a["present"] and a["review"] not in ("captioned", "bad-audio")]
            state = "present" if usable else "needs_regeneration" if linked else "unresolved"
            lesson = json.loads(row["data"])
            entry = {"prompt_id": row["id"], "prompt_key": f"prompt_{row['id']}", "state": state,
                     "expected_filename": f"{row['id']}.mp4", "assets": [a["id"] for a in linked],
                     "lesson": lesson}
            prompts.append(entry)
            if state == "needs_regeneration" or (include_unmatched and state == "unresolved"):
                regeneration[entry["prompt_key"]] = row["prompt"]
            if any(a["present"] for a in linked):
                dump(self.media / f"{row['id']}.json", {**entry, "assets": linked,
                     "caption_text_source": "Reviewed lesson text, not Whisper transcription",
                     "caption_lines": [[s["hindi"], s["bangla_pronunciation"], s["bangla_meaning"]] for s in lesson["sentences"]]})
            elif linked:
                (self.media / f"{row['id']}.json").unlink(missing_ok=True)
        inventory = {"prompts": prompts, "assets": assets,
                     "unmatched_asset_ids": [a["id"] for a in assets if a["prompt_id"] is None],
                     "summary": {"assets": len(assets), "present_assets": sum(a["present"] for a in assets),
                                 "matched_assets": sum(a["prompt_id"] is not None for a in assets),
                                 "regeneration_prompts": len(regeneration),
                                 "unresolved_prompts": sum(p["state"] == "unresolved" for p in prompts)}}
        dump(self.local / "inventory.json", inventory)
        destination = self.local / "regeneration"
        dump(destination / "prompts.json", regeneration)
        # This directory is tool-owned; only remove previously generated batch files.
        for path in destination.glob("batch-*.json"):
            path.unlink()
        items = list(regeneration.items())
        for start in range(0, len(items), 50):
            dump(destination / f"batch-{start // 50 + 1:02d}.json", dict(items[start:start + 50]))
        self.write_report(assets)
        return inventory["summary"]

    def write_report(self, assets):
        cards = []
        for asset in assets:
            candidates = ", ".join(f"prompt_{x['prompt_id']} ({x['score']:.1f})" for x in asset["candidates"] or [])
            url = Path(os.path.relpath(self.root / asset["path"], self.local)).as_posix()
            transcript = (asset["transcript"] or {}).get("text", "Not transcribed")
            cards.append(f"""<article><h2>Asset {asset['id']} → {('Prompt ' + str(asset['prompt_id'])) if asset['prompt_id'] else 'UNMATCHED'}</h2>
<video controls preload="none" src="{html.escape(url, quote=True)}"></video>
<p>{html.escape(asset['original_name'])}</p><p>Review: {html.escape(asset['review'])} · Present: {bool(asset['present'])}</p>
<p>{html.escape(candidates)}</p><p>{html.escape(transcript)}</p>
<code>python3 scripts/sort_hindi.py review {asset['id']} --state captioned</code></article>""")
        (self.local / "review.html").write_text("""<!doctype html><meta charset="utf-8"><title>Hindi video review</title>
<style>body{font:16px system-ui;background:#eee;padding:24px}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:20px}article{background:white;padding:16px;border-radius:12px;overflow-wrap:anywhere}video{width:100%;height:380px;background:#111}h2{font-size:19px}code{display:block;background:#eee;padding:8px}</style>
<h1>Hindi video matching and review</h1><p>Review the actual video for embedded text. Candidate scores are suggestions. Mark captioned takes with the command shown, or delete the numbered file yourself and run scan. Videos are never automatically deleted; JSON sidecars for missing videos are removed during scan/export.</p><main>""" + "\n".join(cards) + "</main>", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init")
    importer = commands.add_parser("import"); importer.add_argument("source", type=Path)
    transcription = commands.add_parser("transcribe")
    transcription.add_argument("--model", choices=("small", "medium"), default="small")
    transcription.add_argument("--limit", type=int)
    transcription.add_argument("--start-asset", type=int, default=1)
    transcription.add_argument("--end-asset", type=int, default=2147483647)
    matcher = commands.add_parser("match"); matcher.add_argument("--apply-confident", action="store_true")
    assigner = commands.add_parser("assign"); assigner.add_argument("asset", type=int); assigner.add_argument("prompt", type=int)
    reviewer = commands.add_parser("review"); reviewer.add_argument("asset", type=int)
    reviewer.add_argument("--state", choices=("pending", "clean", "captioned", "bad-audio"), required=True)
    reviewer.add_argument("--note", default="")
    commands.add_parser("scan")
    commands.add_parser("status")
    exporter = commands.add_parser("export"); exporter.add_argument("--include-unmatched", action="store_true")
    args = parser.parse_args()
    try:
        library = Library(args.root)
        if args.command == "import": result = library.import_folder(args.source)
        elif args.command == "transcribe": result = library.transcribe(args.model, args.limit, args.start_asset, args.end_asset)
        elif args.command == "match": result = library.match(args.apply_confident)
        elif args.command == "assign": result = library.assign(args.asset, args.prompt)
        elif args.command == "review": result = library.review(args.asset, args.state, args.note)
        elif args.command == "scan": result = library.scan()
        elif args.command == "export": result = library.export(args.include_unmatched)
        else: result = library.export()
        print(json.dumps(result or library.export(), ensure_ascii=False, indent=2))
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
