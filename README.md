# বাংলা ভাষাভাষীদের জন্য ভাষা শেখার ভিডিও

**হিন্দি ও জার্মান—প্রতিটিতে ৫০০ বাক্য এবং ২৫০টি সম্পূর্ণ প্রম্পট। প্রতিটি ভিডিও সর্বোচ্চ ১০ সেকেন্ড।**

একজন অত্যন্ত সুন্দরী, স্মার্ট, আত্মবিশ্বাসী প্রাপ্তবয়স্ক নারী উপস্থাপক দুটি বাক্য শেখাবেন। প্রথম বাক্য ০–৫ সেকেন্ডে, দ্বিতীয়টি ৫–১০ সেকেন্ডে। তিনি শুধু মূল ভাষার বাক্য বলবেন; একই সময়ে ক্যাপশনে মূল বাক্য, বাংলা উচ্চারণ ও বাংলা অর্থ দেখা যাবে। দর্শকের ইংরেজি বা নতুন ভাষার অক্ষর জানার দরকার নেই।

## Markdown না JSON?

**নিজে পড়ে কপি করতে Markdown; এক্সটেনশনের জন্য JSON।** দুই ফরম্যাটে একই প্রম্পট আছে। Markdown-এ `# Prompt 1`, তারপর আপলোড শিরোনাম এবং সম্পূর্ণ প্রম্পটের কোড ব্লক। শুধু সাবটাইটেল দেখতে `captions.md` খুলুন; সেখানেও একই প্রম্পট নম্বর আছে।

| কাজ | হিন্দি | জার্মান |
| --- | --- | --- |
| প্রম্পট ১–২৫০, JSON | [flow-prompts.json](hindi/flow-prompts.json) | [flow-prompts.json](german/flow-prompts.json) |
| প্রম্পট ১–১২৫, Markdown | [flow-prompts-01.md](hindi/flow-prompts-01.md) | [flow-prompts-01.md](german/flow-prompts-01.md) |
| প্রম্পট ১২৬–২৫০, Markdown | [flow-prompts-02.md](hindi/flow-prompts-02.md) | [flow-prompts-02.md](german/flow-prompts-02.md) |
| মূল ভাষা ও বাংলা ক্যাপশন | [captions.md](hindi/captions.md) | [captions.md](german/captions.md) |
| শুধু ৫০০ বাক্যের JSON array | [sentences.json](hindi/sentences.json) | [sentences.json](german/sentences.json) |
| শিরোনাম, বাক্য, অর্থ ও উচ্চারণ | [videos.json](hindi/videos.json) | [videos.json](german/videos.json) |
| সম্পাদনাযোগ্য ভাষা সহায়িকা | [bangla-support.txt](hindi/bangla-support.txt) | [bangla-support.txt](german/bangla-support.txt) |

JSON keys are exactly `"prompt 1"` through `"prompt 250"`, each with a complete prompt string. Decode the value before pasting into Flow; do not paste the key, surrounding JSON quotes or literal newline escapes. Markdown code blocks already contain decoded text.

```python
import json
from pathlib import Path
prompts = json.loads(Path("hindi/flow-prompts.json").read_text())
print(prompts["prompt 1"])
```

Use the supplied Bangla upload title on YouTube Shorts, Instagram Reels or Facebook Reels. It is creator metadata, not extra spoken content. Every prompt contains its own presenter, duration, two sentences and exact captions; no previous prompt is required.

## ক্যাপশন কেমন হবে

Hindi Prompt 1, 00–05 seconds:

```text
मेरा नाम आशा है।
উচ্চারণ: মেরা নাম আশা হ্যায়।
অর্থ: আমার নাম আশা।
```

At 05–10 seconds, replace that group with:

```text
तुम्हारा नाम क्या है?
উচ্চারণ: তুমহারা নাম ক্যা হ্যায়?
অর্থ: তোমার নাম কী?
```

Show all three lines together in large, high-contrast text below the face and clear of bottom/right platform controls. Wrap long lines neatly. Preserve Devanagari vowel signs and conjuncts, German special letters and Bangla glyphs. Pronunciation guides are visual support: audio models the original language, not a literal reading of Bangla transliteration. Caption windows are planned; review actual speech, spelling and readability before upload. Videos have not been generated, timed or visually verified.

## Content notes

Videos 001–100 are mainly A1 everyday situations; 101–200 mainly A2; 201–250 form an easy B1 bridge. These are editorial difficulty bands, not certified CEFR labels or a statistical frequency ranking. Every set contains 500 unique original sentences. Video N uses human sentence numbers `2*N - 1` and `2*N`, or array indices `2*N - 2` and `2*N - 1`.

Hindi uses standard Devanagari. Gender-dependent first-person examples generally use female forms, such as `रहती हूँ` and `चाहती हूँ`. Other speakers may need different endings. The example `कैसी हो` addresses a female listener; `रहते हो` addresses a male listener. Formal `आप` and informal `तुम` follow the situation. The presenter teaches example sentences, including other people's names, rather than claiming every example as her own biography.

Bangla pronunciation guides are approximate, especially Hindi nasal vowels, vowel length and some consonants, and German ü/ö, ch and r. These authored learning aids have not undergone independent native-speaker review. The presenter is specified as a photorealistic generated human character; no filmed human footage is supplied.

## Source and language coverage

Inspected source: `/Users/polodev/sites/language-ebooks-standalone`. Its root AGENTS.md and README describe ten independent language repositories registered as Git submodules, each with Foundation, Intermediate, Advanced and Vocabulary plans. The German book metadata showed planned practical topics. The video sets are newly authored, not extracted finished ebook prose. Source repositories were not modified.

[All language metadata](languages.json) records variety, audience, captions, the ten-second maximum and content status. Hindi follows the practical topic order of German, with suitable changes to names, places, currency and wording.

| Directory | Language | Status |
| --- | --- | --- |
| `arabic/` | Modern Standard Arabic | Metadata; content planned |
| `chinese/` | Mandarin, simplified script | Metadata; content planned |
| `french/` | Standard French, France | Metadata; content planned |
| `german/` | Standard German, Germany | 500 sentences; 250 prompts and caption groups |
| `hindi/` | Standard Hindi, Devanagari | 500 sentences; 250 prompts and caption groups |
| `japanese/` | Standard Japanese | Metadata; content planned |
| `korean/` | Standard South Korean | Metadata; content planned |
| `malaysian/` | Standard Malay, Malaysia, Rumi script | Metadata; content planned |
| `russian/` | Standard Russian | Metadata; content planned |
| `spanish/` | Standard Spanish, Spain | Metadata; content planned |

The remaining eight language folders contain metadata, not completed sentence sets.

## Edit and rebuild

Edit Bangla titles, meanings and pronunciation in the language's `bangla-support.txt`. If an original sentence changes, update it in both `bangla-support.txt` and `authoring.txt`; the build checks agreement. The common concise prompt and subtitle format lives in `scripts/prompt_format.py`.

```sh
python3 scripts/build_hindi.py
python3 scripts/build_german.py
```

The scripts regenerate the sentence array, video records, JSON prompts, two Markdown prompt batches and `captions.md`. Validation covers unique sentences, counts, sequential keys, source agreement and caption coverage. The two five-second periods are teaching beats within a single complete video; all prompts request a maximum of ten seconds.
