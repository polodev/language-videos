# Hindi caption sample project

The approved template is saved at `../../caption-template/`. Original Variant 4 (individual backgrounds behind the three lines) is the default for all 250 videos. Current Variant 9 (bold outlined text) is saved as an alternative.

This project preserves the sample composition sources. Approved sample MP4s live in the ignored `../../caption-template/samples/` folder. Production outputs are the numbered MP4s and JSON sidecars in `../caption-videos/`.

Each sentence has exactly three unlabeled lines: Hindi, Hindi pronunciation in Bengali script, and Bangla meaning. The text comes from `../videos.json`, not ASR spelling. All three lines switch together at the next Hindi sentence. No word highlighting or animation. Original audio is preserved.

The sample uses prompt 1 at native 720×1280, 24 fps, 10 seconds, switching at frame 119 (4.958333 seconds). The production batch uses separately reviewed timings and fitted text sizes for every video.

Do not open browser previews. Deliver MP4 files directly. Full batch implementation and rerun instructions are in `../../caption-template/README.md`.
