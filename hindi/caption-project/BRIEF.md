---
workflow: embedded-captions
flow: automation
storyboard: no
language: Hindi and Bengali
aspect: 9:16
---

Create only ten rendered style variants of prompt 1 for user selection. Use the same original footage and audio, and three unlabeled lines per sentence: Hindi, Hindi pronunciation in Bengali script, Bangla meaning. No word highlighting, animation, subject matting or embedded text. Switch the entire block at the second Hindi sentence, using the existing offline Whisper-small transcript for timing. The explicit three-line, sentence-only brief overrides the workflow's two-line and animated verbatim defaults. User authorized ten test renders and wants to select multiple variants. Variant 4 is the first choice, saved at root caption-template; full-collection rendering awaits the final style choices.

The original remains in Videos; the samples go to caption-videos. Typography uses local Noto Sans Devanagari and Noto Sans Bengali. Five outlined-text treatments: all white, yellow pronunciation, yellow Hindi, three colors, and bold white. Captions must NEVER have any background, box, panel, band or scrim. Only glyph outlines provide contrast. No browser previews; export MP4 files directly. Native 720×1280, 24fps, 10 seconds. All font files and GSAP are local at render time.
