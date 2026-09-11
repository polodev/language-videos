---
workflow: embedded-captions
flow: automation
storyboard: no
language: Hindi and Bengali
aspect: 9:16
---

Create only five rendered style variants of prompt 1 for user selection. Use the same original footage and audio, and three unlabeled lines per sentence: Hindi, Hindi pronunciation in Bengali script, Bangla meaning. No word highlighting, animation, subject matting or embedded text. Switch the entire block at the second Hindi sentence, using the existing offline Whisper-small transcript for timing. The explicit three-line, sentence-only brief overrides the workflow's two-line and animated verbatim defaults. User explicitly authorized five test renders; full-collection rendering awaits their chosen variant.

The original remains in Videos; the five samples go to caption-videos. Typography uses local Noto Sans Devanagari and Noto Sans Bengali. Five static treatments: dark card, light card, outlined, line bands, left panel. Native 720×1280, 24fps, 10 seconds. All font files and GSAP are local at render time.
