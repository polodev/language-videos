# Hindi video sorting — local Whisper small

Current phase: copy, transcribe, identify and number the downloads. No HyperFrames work, automatic deletion or actual video regeneration runs during sorting.

Local layout (all excluded from Git):

```text
hindi/
  library.sqlite3        # Prompt/asset mappings and operation history
  Videos/
    incoming/            # Imported clips awaiting confident identification
    1.mp4                # Clip matched to prompt_1
    1.json               # Original name, hash, transcript and lesson data
    2.mp4
    2.json
  .local/
    inventory.json
    original_downloads/  # Preserved originals from the initial Finder import
    transcripts/
    review.html
```

Numbering is by **prompt identity**, not download order. A missing prompt leaves a gap; other videos are never renumbered to fill it. Duplicate or ambiguous takes remain in `incoming/` for review. The import command copies original downloads without modifying them. For the initial 250-video Finder import, the originals are preserved in `.local/original_downloads/`; `Videos/` contains the working copies. SHA-256 verifies copied bytes; the tool refuses to overwrite an existing numbered video.

## Import and identify

Run from the repository root:

```sh
python3 scripts/sort_hindi.py import '/Users/polodev/Downloads/Untitled collection'
python3 scripts/sort_hindi.py transcribe --model small
python3 scripts/sort_hindi.py match --apply-confident
python3 scripts/sort_hindi.py status
```

If macOS blocks Downloads with “Operation not permitted”, grant this app access or use Finder to copy the downloads into `hindi/Videos/`, then import that accessible folder:

```sh
python3 scripts/sort_hindi.py import hindi/Videos
```

The cached **multilingual Whisper small** model runs through `faster-whisper`, locally on CPU with INT8. Both offline environment settings and `local_files_only=True` prevent model downloads during transcription; no audio is sent to an API. The current machine has the small model cached. Hindi is specified for recognition to identify the Hindi sentences; mixed Bangla may be transcribed imperfectly. Do not use this transcript as the source of future caption spelling. The authoritative text remains `videos.json`.

Use `--limit 5` to try the first five pending clips. For separate workers, use nonoverlapping asset ranges such as `--start-asset 1 --end-asset 125` and `--start-asset 126 --end-asset 250`. Completed transcripts are persisted individually and skipped on subsequent runs. The model supports word timestamps, which are saved for later inspection. [Faster Whisper documentation](https://github.com/SYSTRAN/faster-whisper).

Both expected Hindi sentences contribute to matching. Automatic naming requires a high fuzzy similarity score, a clear lead over the next candidate, and no competing take. These conservative heuristic thresholds have not yet been calibrated on your downloads; they may leave many clips unresolved. This is preferable to giving a video the wrong prompt number.

Open `hindi/.local/review.html` to watch imported clips and inspect transcript candidates. Resolve uncertain matches with the **asset ID** displayed in the report:

```sh
python3 scripts/sort_hindi.py assign 12 37
```

This maps asset 12 to `prompt_37` and names its local video `37.mp4` (preserving another original extension if applicable). Its corresponding `37.json` contains the transcript, provenance, prompt identity and exact three-line Hindi/Bangla lesson text for future caption work. The database and sidecar preserve its identity even if the numbered video is later deleted.

## After you manually delete or regenerate clips

```sh
python3 scripts/sort_hindi.py scan
```

Scanning records missing numbered files; it never deletes videos. Import a regenerated download, transcribe it and match it again to recover the same number. The old mapping remains in SQLite's history.

Optional later review commands can mark an existing clip without deleting it:

```sh
python3 scripts/sort_hindi.py review 12 --state captioned
python3 scripts/sort_hindi.py review 12 --state clean
```

An auxiliary `.local/regeneration/prompts.json` and matching batches of up to 50 contain current text-free Flow prompts for **identified** clips marked captioned/bad-audio or found missing. These are prompt exports only, never actual regeneration. Unmatched prompts stay unresolved, not automatically declared missing. Only after reconciling the full collection, `export --include-unmatched` explicitly includes those unresolved slots in that export. Ordinary later scans/exports restore the conservative default.

Python dependencies: `faster-whisper`, `rapidfuzz`; `ffprobe` is used for media metadata. No transcription dependencies are installed or models fetched automatically by this tool.

Safety checks:

```sh
python3 -m unittest discover -s scripts -p 'test_sort_hindi.py'
git check-ignore hindi/Videos/1.mp4 hindi/Videos/1.json hindi/library.sqlite3
```
