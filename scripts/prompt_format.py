"""Shared concise 10-second speech-only prompt format."""

import json


def write_prompt_batches(folder, prompts):
    """Export five JSON objects of 50 prompts without renumbering their keys."""
    assert list(prompts) == [f"prompt_{i}" for i in range(1, 251)]
    destination = folder / "json-prompts"
    destination.mkdir(exist_ok=True)
    items = list(prompts.items())
    for start in range(0, 250, 50):
        batch = dict(items[start:start + 50])
        path = destination / f"prompts-{start + 1:03d}-{start + 50:03d}.json"
        path.write_text(json.dumps(batch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        assert json.loads(path.read_text(encoding="utf-8")) == batch
    merged = {}
    files = sorted(destination.glob("prompts-*.json"))
    assert len(files) == 5
    for path in files:
        batch = json.loads(path.read_text(encoding="utf-8"))
        assert len(batch) == 50 and not (merged.keys() & batch.keys())
        merged.update(batch)
    assert merged == prompts, "Split JSON must exactly match the main prompt collection"



def full_prompt(lesson, language, field):
    beats = []
    for index, sentence in enumerate(lesson["sentences"]):
        speech = f"Say {language} once: “{sentence[field]}”"
        if field == "hindi":
            speech += f" Then say its Bangla meaning once: “{sentence['bangla_meaning']}”"
        beats.append(f"{index * 5:02d}–{(index + 1) * 5:02d}s — AUDIO: {speech}")
    audio = f"Speak clear, accurate {language}, once per sentence."
    if field == "hindi":
        audio = "Speak clear Hindi followed by natural Bangladeshi Bangla meaning for each sentence. Say each quoted utterance once, in order; do not repeat the Hindi as a separate pronunciation demonstration."
    return f"""Create a standalone 9:16 {language} lesson, maximum 10 seconds. One very beautiful, smart, confident adult female teacher (25–35), photorealistic and elegantly dressed, teaches directly to camera in a bright, quiet studio, with warm eye contact and natural lip sync.
SPEECH ONLY: No captions, subtitles, on-screen text, letters, labels, title cards or text overlays anywhere in the video. Use a plain background without signs or writing.
{audio} No extra speech, music, intro or outro.
Upload title (creator metadata only; never show or speak it): {lesson['upload_title']}

{chr(10).join(beats)}

Complete the specified speech and end by 10 seconds. Keep the picture text-free throughout."""
