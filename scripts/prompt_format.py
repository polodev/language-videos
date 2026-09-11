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


def full_prompt(lesson, language, field):
    caption_rules = ""
    if field == "hindi":
        caption_rules = "\nCAPTION RULES: Copy verbatim; never re-transliterate. Line 1: Devanagari only. Lines 2–3: Bangla script only; never insert Hindi characters into Bangla. Use clear Bengali lettering on a solid dark panel, generous spacing and no heavy outline. Keep each group static for five seconds."
    blocks = []
    for index, sentence in enumerate(lesson["sentences"]):
        speech = f"speak only this {language} sentence once"
        if field == "hindi":
            speech = f"say Hindi: “{sentence[field]}” THEN say its meaning in Bangla: “{sentence['bangla_meaning']}”"
        blocks.append(f"""{index * 5:02d}–{(index + 1) * 5:02d}s — {speech}; display all three caption lines:
{sentence[field]}
উচ্চারণ: {sentence['bangla_pronunciation']}
অর্থ: {sentence['bangla_meaning']}""")
    audio = f"Speak clear, accurate {language}."
    if field == "hindi":
        audio = "Speak Hindi 1 → Bangla meaning 1 → Hindi 2 → Bangla meaning 2. All four quoted lines must be audible, in clear Hindi and natural Bangladeshi Bangla. Do not read pronunciation guides or labels aloud."
    return f"""Create one standalone 9:16 {language} lesson, maximum 10 seconds. One very beautiful, smart, confident adult female teacher (25–35), photorealistic and elegantly dressed, teaches directly to camera with warm eye contact and natural lip sync.
Audience: Bangla-only beginners. {audio} Show original writing, Bangla pronunciation and Bangla meaning together: large, high-contrast, correctly shaped, neatly wrapped below her face, clear of bottom/right controls. Preserve text exactly. Bangla pronunciation is approximate; model the native sound. No extra speech, music, intro or outro.{caption_rules}
Upload title (not spoken): {lesson['upload_title']}

{chr(10).join(blocks)}

Switch captions at 5 seconds; finish both sentences and end by 10 seconds."""


def captions_markdown(lessons, language_bn, field):
    out = [f"মূল {language_bn}, বাংলা উচ্চারণ ও বাংলা অর্থ একসঙ্গে দেখাতে হবে। সময়গুলো পরিকল্পিত ক্যাপশন উইন্ডো; তৈরি ভিডিও শুনে মিলিয়ে নিন।"]
    for lesson in lessons:
        out.extend([f"# Prompt {lesson['video_number']}", f"**আপলোড শিরোনাম:** {lesson['upload_title']}"])
        for index, sentence in enumerate(lesson["sentences"]):
            out.append(f"**{index * 5:02d}–{(index + 1) * 5:02d} সেকেন্ড**\n\n```text\n"
                       f"{sentence[field]}\nউচ্চারণ: {sentence['bangla_pronunciation']}\n"
                       f"অর্থ: {sentence['bangla_meaning']}\n```")
    return "\n\n".join(out) + "\n"
