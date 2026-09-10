"""Shared concise 10-second prompt and caption format."""


def full_prompt(lesson, language, field):
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
            out.append(f"**{index * 5:02d}–{(index + 1) * 5:02d} সেকেন্ড**\n\n```text\n"
                       f"{sentence[field]}\nউচ্চারণ: {sentence['bangla_pronunciation']}\n"
                       f"অর্থ: {sentence['bangla_meaning']}\n```")
    return "\n\n".join(out) + "\n"
