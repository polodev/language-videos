# Captioned video compilations

Shared settings for all languages are in [settings.json](settings.json). Sources are numbered MP4s with matching lesson JSON files in `<locale>/caption-videos/`.

| Output folder | Source clips per video | Hindi outputs from 250 clips |
| --- | --- | --- |
| caption-videos-small | 3 | 84; last contains 1 clip |
| caption-videos-medium | 15 | 17; last contains 10 clips |
| caption-videos-large | 30 | 9; last contains 10 clips |

Groups are sequential and do not overlap within a size: small `[1,2,3]`, `[4,5,6]`, etc. Every source is included once per size. Full Hindi groups run 30 seconds, 150 seconds, and 300 seconds. Partial groups retain their actual duration. Originals remain in place.

The video stamp displays **Hindi Pathshala Bd**, using `{locale} Pathshala Bd` for other languages. The matching handle is **@HindiPathshalaBd**, using `@{language}PathshalaBd`. The stamp uses the English language name, not an ISO locale code. It is white with a dark outline, no background, at the top right. Existing three-line sentence captions are preserved. Display names, handles and hashtags are separate fields; hashtags never contain spaces.

## Render a language

Run from the repository root with Python 3.11+, FFmpeg/ffprobe, Node.js, Chrome, and HyperFrames available:

```sh
python3 scripts/prepare_video_delivery.py --locale hindi
npx hyperframes check hindi/.local/video-delivery/stamp-project
npx hyperframes render hindi/.local/video-delivery/stamp-project --format png-sequence --fps 1 --output hindi/.local/video-delivery/stamp-png
python3 scripts/render_video_delivery.py --locale hindi
python3 scripts/verify_video_delivery.py --locale hindi
```

Replace `hindi` in all commands with the source directory, e.g. `german`, `japanese`, or `malaysian`. Settings cover English and all existing language directories. Rendering requires that language's actual captioned sources and lesson sidecars; no other language's videos are substituted. Sources must share resolution, frame rate and audio format; preparation rejects mixed formats.

HyperFrames renders the transparent stamp once. FFmpeg applies it to each source once, preserving the encoded source audio at this stage. The three compilation sizes reuse those stamped video streams without another picture encode. Compilation audio is re-encoded to AAC to align it across cuts. No transitions, music, word highlighting or extra narration are added.

Rendering resumes from source/output hashes. Compilation exports are checked for exact video frame count, duration, audio presence/duration, dimensions, and successful full decoding. The final verifier compares non-keyframe packet hashes to the stamped source clips in order, checks source checksums, and refreshes public and internal titles from the current settings. Local caches and exports are ignored by Git.

## Upload metadata

Each output folder contains one `content.json`. Paths in it are relative to that same folder; move the folder and JSON together.

Until the requested example file can be read, the JSON uses an explicit provisional schema (`schema_status: provisional_awaiting_uploader_example`). Do not assume that an unknown uploader accepts it. Once an accessible example is supplied, adapt the export shape while retaining source IDs and segment timing in the local manifest.

Each video entry has an internal `project_title`, for example `Hindi small 001 — merged from video IDs 1, 2, 3`. This is for identifying the source clips in the uploader; `title` remains the public SEO title. Each video entry also contains a Bengali topic-based title, description, short social caption, tags, hashtags, source lesson numbers, original sentences, segment times, stamp text, checksum and verification result. Platform-specific text is grouped under `platforms`. The full description lists lesson times; these are plain timestamps, not a claim of automatic platform chapters.

Titles reflect actual topics and sentence counts. Each has a part number, with the learning topic before it. Description and keyword guidance: [channel research](../channel%20informations/keyword-research.md). These are relevant search phrases, not measured search volumes or a ranking guarantee.

For additional topic categories, add Bengali names to `topic_names_bn` in settings; unknown categories use a generic language-conversation label. Platform publishing, scheduling and account selection are left to the upload software.
