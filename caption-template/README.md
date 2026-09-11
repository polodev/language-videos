# Preferred caption template — Variant 4

This is the first-choice template for future captioned lessons. `template.json` records the styling and timing rules. `variants.json` contains all ten outlined-only presets. Variant 4 is the preferred default; the user may select multiple variants. Pass `--variant 6` (or another number) to build a different preset.

Each sentence shows exactly three unlabeled lines:

1. Hindi — white
2. Hindi pronunciation in Bengali script — warm yellow
3. Bangla meaning — mint green

Every line has a dark outline. **Never add a caption background, box, band, panel or scrim.** No word highlighting, animation or browser preview. Keep the entire block visible through the Hindi sentence and its Bangla meaning; replace it when the next Hindi sentence starts.

Build a HyperFrames project from the existing numbered video and reviewed lesson text:

```sh
python3 caption-template/build.py --number 1 --switch 4.94 --output hindi/.local/selected-caption
npx hyperframes@0.8.34 check hindi/.local/selected-caption
npx hyperframes@0.8.34 render hindi/.local/selected-caption --quality high --output hindi/caption-videos/1.mp4
```

`--switch` must come from reviewed audio timing for that particular video; it is rounded to a source frame. Do not assume every video changes at five seconds. Run the text-fit checks for each lesson: longer sentences may require size or layout adjustment before rendering. Never truncate the Hindi, pronunciation or meaning to fit.

Local fonts and GSAP are included in `assets/`, along with font licenses. The builder preserves the original source, its dimensions, frame rate and audio. Videos and SQLite remain excluded from Git. Deliver MP4 files directly.

Additional samples: 6 = mint pronunciation, 7 = gold Hindi with sky-blue pronunciation, 8 = left-aligned colors, 9 = bold three colors, 10 = spaced white with gold meaning.
