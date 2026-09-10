#!/usr/bin/env python3
"""Build the Hindi sentence array and paste-ready Flow prompt collections."""

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HINDI = ROOT / "hindi"


def rows(path):
    return [line for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")]


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_lessons():
    topics = []
    originals = []
    topic = None
    for line in (HINDI / "authoring.txt").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        if line.startswith("# "):
            name, level, scene = [part.strip() for part in line[2:].split("|")]
            topic = {"topic": name, "approximate_level": level, "setting": scene}
            topics.append(topic)
        else:
            assert topic is not None
            title, first, second = line.split("|")
            originals.append({**topic, "editorial_title_en": title, "originals": [first, second]})

    supports = [line.split("|") for line in rows(HINDI / "bangla-support.txt")]
    assert len(originals) == len(supports) == 250
    assert len(topics) == 25
    lessons = []
    for number, (original, support) in enumerate(zip(originals, supports), 1):
        assert len(support) == 7, (number, "Expected title and two sets of three text fields")
        title, de1, bn1, pron1, de2, bn2, pron2 = support
        assert [de1, de2] == original.pop("originals"), (number, "Hindi source mismatch")
        assert all(re.search(r"[\u0980-\u09ff]", text) for text in (title, bn1, pron1, bn2, pron2))
        sentences = []
        for position, (de, bn, pron) in enumerate(((de1, bn1, pron1), (de2, bn2, pron2))):
            assert de[-1] in "।?!" and len(re.findall(r"[।!?]", de)) == 1
            assert re.search(r"[\u0900-\u097f]", de) and not re.search(r"[A-Za-z]", de)
            sentences.append({
                "sentence_number": (number - 1) * 2 + position + 1,
                "hindi": de,
                "bangla_meaning": bn,
                "bangla_pronunciation": pron,
            })
        full_title = f"হিন্দি শিখুন: {title}"
        assert len(full_title) <= 100
        lessons.append({"video_number": number, "upload_title": full_title,
                        "duration_seconds": 10, **original, "sentences": sentences})
    all_sentences = [s["hindi"] for lesson in lessons for s in lesson["sentences"]]
    assert len(all_sentences) == len(set(all_sentences)) == 500
    assert len({lesson["upload_title"] for lesson in lessons}) == 250
    return lessons, all_sentences


from prompt_format import full_prompt as format_prompt, captions_markdown


def full_prompt(lesson):
    return format_prompt(lesson, "Hindi", "hindi")


def main():
    lessons, sentences = load_lessons()
    prompts = {f"prompt {v['video_number']}": full_prompt(v) for v in lessons}

    write_json(HINDI / "sentences.json", sentences)
    write_json(HINDI / "videos.json", lessons)
    write_json(HINDI / "flow-prompts.json", prompts)

    for batch, start in enumerate((0, 125), 1):
        subset = lessons[start:start + 125]
        text = [f"# হিন্দি ভিডিও {start + 1:03d}–{start + 125:03d}",
                "প্রতিটি ভিডিও আলাদা ১০ সেকেন্ডের পাঠ: দুটি হিন্দি বাক্য, বাংলা অর্থ ও বাংলা উচ্চারণ।",
                "নিচের শিরোনামটি আপলোডের জন্য। কোড ব্লকের সম্পূর্ণ লেখাটি প্রম্পট।",
                "প্রতিটি প্রম্পট একটি সম্পূর্ণ ১০ সেকেন্ডের ভিডিওর জন্য।"]
        for lesson in subset:
            number = lesson["video_number"]
            text.extend([f"# Prompt {number}", f"**আপলোড শিরোনাম:** {lesson['upload_title']}",
                         f"**JSON key:** `prompt {number}`",
                         "```text\n" + prompts[f"prompt {number}"] + "\n```"])
        (HINDI / f"flow-prompts-{batch:02d}.md").write_text("\n\n".join(text) + "\n", encoding="utf-8")

    (HINDI / "captions.md").write_text(captions_markdown(lessons, "হিন্দি", "hindi"), encoding="utf-8")

    # Check the actual written files, including Unicode and prompt coverage.
    actual = json.loads((HINDI / "flow-prompts.json").read_text(encoding="utf-8"))
    assert list(actual) == [f"prompt {i}" for i in range(1, 251)]
    for lesson in lessons:
        prompt = actual[f"prompt {lesson['video_number']}"]
        assert lesson["upload_title"] in prompt
        assert prompt.count("display all three caption lines:") == 2
        for sentence in lesson["sentences"]:
            assert sentence["hindi"] in prompt
            assert sentence["bangla_meaning"] in prompt
            assert sentence["bangla_pronunciation"] in prompt
            assert f"উচ্চারণ: {sentence['bangla_pronunciation']}" in prompt
            assert f"অর্থ: {sentence['bangla_meaning']}" in prompt
    for path in HINDI.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    for part in (1, 2):
        md = (HINDI / f"flow-prompts-{part:02d}.md").read_text(encoding="utf-8")
        assert md.count("```text\n") == 125
        assert md.count("\n```\n") == 125

    levels = Counter(v["approximate_level"] for v in lessons)
    print(f"Validated {len(sentences)} unique Hindi sentences, {len(prompts)} complete prompts, "
          "two Markdown batches, all specifying complete 10-second videos.")
    print("Approximate level distribution by video:", dict(levels))
    print("Longest complete lesson speech:", max(
        sum(len(s['hindi'].split()) for s in v['sentences'])
        for v in lessons), "space-delimited target-language words.")


if __name__ == "__main__":
    main()
