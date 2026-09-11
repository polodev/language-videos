# Approved caption templates

**Default: original Variant 4 — individual backgrounds for all three lines.** The user also approved the current Variant 9 (bold outlined three-color text) as an alternative. The entire Hindi collection uses Variant 4.

| Line | Text | Variant 4 appearance |
| --- | --- | --- |
| 1 | Hindi sentence | White text on a dark teal background |
| 2 | Hindi pronunciation in Bengali script | Dark text on a warm yellow background |
| 3 | Bangla meaning | Dark text on an ivory background |

Each background fits its own line. There is no enclosing panel. All three lines stay together through the Hindi speech and its Bangla meaning, then switch as one block at the next Hindi sentence. No word highlighting or animation. Deliver exported MP4s directly; do not open browser previews.

`template.json` saves the selection, colors and layout. `variants.json` saves all presets. The approved reference MP4s are in the ignored `samples/` folder: `variant-4.mp4` and `variant-9.mp4`.

For one video:

```sh
python3 caption-template/build.py --number 1 --switch 4.94 --output hindi/.local/selected-caption
npx hyperframes@0.8.34 check hindi/.local/selected-caption
npx hyperframes@0.8.34 render hindi/.local/selected-caption --quality high --output hindi/caption-videos/1.mp4
```

Pass `--variant 9` to use the approved alternative. The switch time must come from that video's audio and is rounded to the source frame rate. Long lines need a text-fit check; never truncate the lesson. Batch rendering fits the fonts individually while preserving exactly three lines.

## The 250-video batch

The caption layers are rendered by HyperFrames as 500 transparent PNGs, one per sentence. FFmpeg holds each layer over the original video at the reviewed switch time and copies the original audio stream. This is equivalent to a static HyperFrames caption composition without rendering each unchanged caption 240 times.

1. `scripts/plan_caption_batch.py` matches second-sentence text to the existing offline Whisper-small timings. Inspect its output before rendering. `hindi-timing-overrides.json` preserves the reviewed corrections and applies them only to the matching source checksum.
2. `scripts/measure_caption_text.cjs` measures text with the actual local Hindi/Bengali fonts in headless Chromium.
3. `scripts/build_caption_layers.py` builds `hindi/.local/caption-layers/`, fitting every line to its individual background.
4. HyperFrames checks and renders the layers as a PNG sequence at 1 fps.
5. `scripts/audit_caption_layers.cjs` checks all 1,500 text lines for clipping.
6. `scripts/render_caption_batch.py` exports numbered videos and JSON sidecars to `hindi/caption-videos/` and tracks completed exports in `hindi/library.sqlite3`.

The batch is resumable: source checksums, caption PNGs and switch times form its cache key. Raw source videos remain in `hindi/Videos/`. Videos, samples, SQLite and intermediate rendering data are excluded from Git. Local font licenses accompany the fonts in `assets/`.


Production render commands (after reviewing the timing plan and measuring text):

```sh
python3 scripts/build_caption_layers.py
npx hyperframes@0.8.34 check hindi/.local/caption-layers
npx hyperframes@0.8.34 render hindi/.local/caption-layers --format png-sequence --fps 1 --workers 2 --output hindi/.local/caption-pngs
node scripts/audit_caption_layers.cjs
python3 scripts/render_caption_batch.py --workers 3
python3 scripts/verify_caption_batch.py
```

The verification decodes every output, compares both caption layers before and at the sentence-switch frame, checks output/source SHA-256, and compares the original and exported compressed audio streams. Failed outputs can be repaired with `--numbers 8,35 --force`, then checked using `verify_caption_batch.py --numbers 8,35`. Intermediate data and full verification reports live under `hindi/.local/`.
