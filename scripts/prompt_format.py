"""Shared concise 10-second prompt and caption format."""

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


def caption_lines(sentence, field):
    if field == "hindi":
        lines = [sentence[field], sentence["bangla_pronunciation"], sentence["bangla_meaning"]]
        assert len(set(lines)) == 3
        assert all(line and "\n" not in line and "\r" not in line for line in lines)
        return lines
    return [sentence[field], f"উচ্চারণ: {sentence['bangla_pronunciation']}", f"অর্থ: {sentence['bangla_meaning']}"]


def hindi_prompt(lesson):
    beats = []
    for index, sentence in enumerate(lesson["sentences"]):
        captions = "\n".join(caption_lines(sentence, "hindi"))
        beats.append(f"""{index * 5:02d}–{(index + 1) * 5:02d}s
AUDIO: Say Hindi once: “{sentence['hindi']}” Then say its Bangla meaning once: “{sentence['bangla_meaning']}”
EXACT ON-SCREEN CAPTION — only these three rows:
{captions}""")
    return f"""Create a standalone 9:16 Hindi lesson, maximum 10 seconds. A very beautiful, smart, confident adult female teacher (25–35), photorealistic and elegantly dressed, teaches to camera with natural lip sync.
Audio: clear Hindi followed by natural Bangladeshi Bangla meaning for each sentence. The pronunciation row is SILENT reading support: never speak or repeat it. No extra speech or music.
Captions: EXACTLY THREE single-line rows at a time: (1) original Hindi in Devanagari, (2) Hindi pronunciation written ONLY in Bangla, (3) meaning written ONLY in Bangla. Copy the supplied text character for character; do not translate or transliterate it again. Never duplicate a row, add a fourth row, or add automatic subtitles, labels, numbering or titles. Do not wrap rows. Fit each complete row within the safe width using clear, readable lettering. Use white text on a dark panel below her face, clear of bottom/right controls, with generous spacing and no heavy outline. Keep each group static; replace all three rows together at 5 seconds. Check for spelling errors, mixed scripts and duplicate rows before finalizing.
Upload title (metadata only, never on screen or spoken): {lesson['upload_title']}

{chr(10).join(beats)}

Only the exact caption blocks go on screen. Complete both Hindi → Bangla speech pairs and end by 10 seconds."""


def full_prompt(lesson, language, field):
    if field == "hindi":
        return hindi_prompt(lesson)
    blocks = []
    for index, sentence in enumerate(lesson["sentences"]):
        blocks.append(f"""{index * 5:02d}–{(index + 1) * 5:02d}s — speak only this {language} sentence once; display all three caption lines:
{sentence[field]}
উচ্চারণ: {sentence['bangla_pronunciation']}
অর্থ: {sentence['bangla_meaning']}""")
    return f"""Create one standalone 9:16 {language} lesson, maximum 10 seconds. One very beautiful, smart, confident adult female teacher (25–35), photorealistic and elegantly dressed, teaches directly to camera with warm eye contact and natural lip sync.
Audience: Bangla-only beginners. Speak clear, accurate {language}. Show original writing, Bangla pronunciation and Bangla meaning together: large, high-contrast, correctly shaped, neatly wrapped below her face, clear of bottom/right controls. Preserve text exactly. Bangla pronunciation is approximate; model the native sound. No extra speech, music, intro or outro.
Upload title (not spoken): {lesson['upload_title']}

{chr(10).join(blocks)}

Switch captions at 5 seconds; finish both sentences and end by 10 seconds."""


def captions_markdown(lessons, language_bn, field):
    out = [f"মূল {language_bn}, বাংলা উচ্চারণ ও বাংলা অর্থ একসঙ্গে দেখাতে হবে। সময়গুলো পরিকল্পিত ক্যাপশন উইন্ডো; তৈরি ভিডিও শুনে মিলিয়ে নিন।"]
    for lesson in lessons:
        out.extend([f"# Prompt {lesson['video_number']}", f"**আপলোড শিরোনাম:** {lesson['upload_title']}"])
        for index, sentence in enumerate(lesson["sentences"]):
            text = "\n".join(caption_lines(sentence, field))
            out.append(f"**{index * 5:02d}–{(index + 1) * 5:02d} সেকেন্ড**\n\n```text\n{text}\n```")
    return "\n\n".join(out) + "\n"
