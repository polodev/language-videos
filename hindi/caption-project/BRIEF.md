---
workflow: embedded-captions
flow: automation
storyboard: no
language: Hindi and Bengali
aspect: 9:16
---

The user approved the ORIGINAL Variant 4 with an individual background behind each of the three lines, and current outlined Variant 9 as an alternative. Use original Variant 4 for all 250 Hindi videos. Save both selections in root `caption-template/`.

Each sentence shows Hindi, Hindi pronunciation in Bengali script, and Bangla meaning, without labels. Original Variant 4 uses white Hindi on dark teal, dark pronunciation on warm yellow, and dark meaning on ivory. The three backgrounds fit their own lines. No enclosing panel. All three lines switch together at the next Hindi sentence, holding through the Bangla meaning. No word highlighting or animation.

The full 250-video production batch is explicitly authorized. HyperFrames renders 500 transparent sentence-caption PNGs; FFmpeg holds those layers over original footage at reviewed per-video timings while copying original audio. Production outputs are `hindi/caption-videos/1.mp4` through `250.mp4`, with matching JSON sidecars. Preserve raw sources in `hindi/Videos/`. The old sample outputs have been removed from the production folder and preserved in ignored local storage.

No browser previews. Deliver exported video files directly. Native video is 720×1280, 24 fps, 10 seconds. Use local Noto Sans Devanagari and Noto Sans Bengali. Fit longer lines without truncating text or adding extra lines. Verify every sentence switch and audio stream before completion.
