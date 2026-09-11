# Hindi caption style samples

Ten HyperFrames samples use the same source (`../Videos/1.mp4`) so caption styles can be compared directly. The full 250-video batch is **waiting for the user's style selection**.

Each sentence has exactly three unlabeled lines: Hindi, Hindi pronunciation in Bengali script, and Bangla meaning. The text comes from `../videos.json`, not ASR spelling. Blocks are static: no word highlighting, fades, entrances, or text motion. The second block starts at frame 119 (4.958333 seconds), aligned to the reviewed offline Whisper-small transcript. The first block stays through its Hindi utterance and Bangla meaning.

| Variant | Style |
| --- | --- |
| 1 | White outline |
| 2 | Yellow pronunciation |
| 3 | Yellow Hindi |
| 4 | Three colors |
| 5 | Bold white |

Native output: 720×1280, 24 fps, 10 seconds, original audio. Captions avoid the face and bottom platform controls. Local Noto fonts preserve Hindi/Bengali shaping; their licenses are in `assets/`.

From the repository root:

```sh
python3 scripts/build_caption_samples.py
python3 scripts/render_caption_samples.py --end 10
```

Rendering runs HyperFrames checks on both caption blocks and around the switch before producing each MP4. Outputs and sidecars are in `../caption-videos/`, excluded from Git. Temporary projects, logs, and snapshots are in `../.local/`. Original videos stay in `../Videos/` while the user compares the samples.

Captions never have backgrounds, panels, bands or scrims. Every glyph has a dark outline. Do not open browser previews; deliver exported MP4s.

Presets and the preferred Variant 4 template live in `../../caption-template/`. Users can keep multiple styles. Additional sample variants 6–10 explore mint pronunciation, gold/sky colors, left alignment, bolder type, and wider spacing.
