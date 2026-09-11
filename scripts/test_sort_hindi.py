import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from sort_hindi import Library, digest


class SortingSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "hindi"
        self.root.mkdir()
        real = Path(__file__).resolve().parents[1] / "hindi"
        for name in ("videos.json", "flow-prompts.json"):
            (self.root / name).write_bytes((real / name).read_bytes())
        self.library = Library(self.root)
        self.source = Path(self.temp.name) / "downloads"
        self.source.mkdir()
        self.probe = patch("sort_hindi.subprocess.run", return_value=subprocess.CompletedProcess([], 0, '{"format":{"duration":"10"}}', ""))
        self.probe.start()

    def tearDown(self):
        self.probe.stop()
        self.library.db.close()
        self.temp.cleanup()

    def add(self, name, contents):
        path = self.source / name
        path.write_bytes(contents)
        self.library.import_folder(self.source)
        return path

    def test_copy_is_verified_idempotent_and_original_is_untouched(self):
        source = self.add("download.mp4", b"test-video-content")
        asset = self.library.asset(1)
        self.assertEqual(digest(source), digest(self.library.path(asset)))
        self.assertEqual(self.library.import_folder(self.source)["imported"], 0)
        self.library.assign(1, 19)
        self.assertTrue(source.exists())
        self.assertEqual((self.library.media / "19.mp4").read_bytes(), source.read_bytes())
        sidecar = json.loads((self.library.media / "19.json").read_text())
        self.assertEqual(sidecar["prompt_key"], "prompt_19")
        self.assertEqual(len(sidecar["caption_lines"][0]), 3)

    def test_existing_numbered_video_is_never_overwritten(self):
        self.add("download.mp4", b"incoming-video")
        target = self.library.media / "1.mp4"
        target.write_bytes(b"existing-video")
        with self.assertRaises(ValueError):
            self.library.assign(1, 1)
        self.assertEqual(target.read_bytes(), b"existing-video")
        self.assertIsNone(self.library.asset(1)["prompt_id"])

    def test_deleted_video_keeps_identity_and_replacement_can_reuse_number(self):
        self.add("old.mp4", b"old")
        self.library.assign(1, 7)
        (self.library.media / "7.mp4").unlink()
        self.library.scan()
        self.assertEqual(self.library.asset(1)["prompt_id"], 7)
        queued = json.loads((self.library.local / "regeneration/prompts.json").read_text())
        self.assertEqual(list(queued), ["prompt_7"])
        self.add("new.mp4", b"new")
        self.library.assign(2, 7)
        self.assertEqual((self.library.media / "7.mp4").read_bytes(), b"new")
        self.assertEqual(json.loads((self.library.local / "regeneration/prompts.json").read_text()), {})

    def test_empty_library_does_not_claim_all_prompts_need_regeneration(self):
        summary = self.library.export()
        self.assertEqual(summary["unresolved_prompts"], 250)
        self.assertEqual(summary["regeneration_prompts"], 0)
        self.assertTrue((self.root / "library.sqlite3").exists())

    def test_exact_two_sentence_transcript_finds_expected_prompt(self):
        lesson = json.loads(self.library.db.execute("SELECT data FROM prompts WHERE id=19").fetchone()[0])
        transcript = " ".join(s["hindi"] for s in lesson["sentences"])
        self.assertEqual(self.library.rank(transcript)[0]["prompt_id"], 19)
        self.assertLess(self.library.rank("मुझे")[0]["score"], 92)


if __name__ == "__main__":
    unittest.main()
