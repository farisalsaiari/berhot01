"""Verify real Data Factory -> JSM Nano tokenizer connection, without training."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from io import StringIO

from services.data_factory.src.pipeline import run_local_pipeline
from models.jsm.src.tokenization.tokenizer import JSMByteTokenizer
from models.jsm.variants.nano.mvp.scripts.data_pipeline import main, _smoke
from models.jsm.variants.nano.mvp.src.data_factory_bridge import load_verified_candidate
from models.jsm.variants.nano.mvp.src.tokenization_preview import preview_candidate_batch


class TokenizerTests(unittest.TestCase):
    def test_arabic_english_emoji_exact_round_trip(self):
        tokenizer = JSMByteTokenizer()
        for text in ("Hello AI", "مرحباً بالعالم", "القهوة ☕ 123", "العربية English 😊\n"):
            ids = tokenizer.encode(text)
            self.assertEqual(ids[0], tokenizer.bos_token_id)
            self.assertEqual(ids[-1], tokenizer.eos_token_id)
            self.assertEqual(tokenizer.decode(ids), text)
            self.assertEqual(tokenizer.decode(tokenizer.encode(text, add_special_tokens=False)), text)

    def test_tokenizer_is_deterministic_and_has_fixed_vocab(self):
        tok = JSMByteTokenizer()
        self.assertEqual(tok.vocab_size, 259)
        self.assertEqual(tok.encode("A"), [257, 66, 258])
        self.assertEqual(tok.encode("A"), tok.encode("A"))
        with self.assertRaises(ValueError):
            tok.decode([257, 0, 258])
        with self.assertRaises(TypeError):
            tok.encode(b"not text")

    def test_real_smoke_from_cli(self):
        out = StringIO()
        with patch("sys.stdout", out):
            main(["smoke"])
        log = out.getvalue()
        self.assertIn("[PASS] JSM tokenizer: jsm-byte-utf8-v0", log)
        self.assertIn("[BLOCKED] Training-ready publication", log)
        self.assertIn("[SKIP] No JSM dataset shard", log)

    def test_smoke_uses_real_factory(self):
        result = _smoke()
        self.assertEqual(result["factory"]["sources"], 2)
        self.assertFalse(result["factory"]["training_allowed"])
        self.assertEqual(result["preview"]["verified_sources"], 2)
        self.assertFalse(result["preview"]["model_training_started"])
        self.assertEqual(result["preview"]["files_written_by_jsm"], 0)


class CandidateBridgeTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="nano-bridge-test-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.input = self.root / "input"
        self.input.mkdir()
        self.storage = self.root / "storage"
        self.text_path = self.input / "source.txt"
        self.text_path.write_text("نص عربي تجريبي صالح، ومثال باللغة الإنجليزية لاختبار التوصيل.\n", encoding="utf-8")
        raw = self.text_path.read_bytes()
        input_manifest = {
            "schema_version": "1.0.0", "batch_id": "nano-test-001",
            "sources": [{
                "source_id": "source-ar",
                "relative_path": "source.txt",
                "sha256": hashlib.sha256(raw).hexdigest(),
                "origin": {"uri": "fixture://nano", "publisher": "Synthetic fixture"},
                "rights": {
                    "retention_allowed": True,
                    "analysis_allowed": True,
                    "training_allowed": False,
                },
            }],
        }
        self.inpath = self.root / "source-manifest.json"
        self.inpath.write_text(json.dumps(input_manifest), encoding="utf-8")
        result = run_local_pipeline(self.inpath, self.input, self.storage)
        self.manifest = Path(result["manifest_path"])

    def _tamper_manifest(self, change):
        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))
        change(manifest)
        self.manifest.write_text(json.dumps(manifest), encoding="utf-8")

    def test_verified_bridge_preview_and_no_train_ready_output(self):
        result = preview_candidate_batch(self.manifest, self.storage)
        self.assertEqual(result["verified_sources"], 1)
        self.assertEqual(result["unique_processed_objects"], 1)
        self.assertGreater(result["total_preview_tokens"], 30)
        self.assertTrue(result["records"][0]["round_trip_ok"])
        self.assertEqual(result["train_ready_export"], "BLOCKED_NO_INDEPENDENT_RIGHTS_APPROVAL")
        self.assertFalse((self.storage / "data" / "datasets").exists())
        self.assertFalse((self.storage / "artifacts").exists())

    def test_cli_paths_are_derived_from_common_root(self):
        output = StringIO()
        with patch("sys.stdout", output):
            main(["paths", "--storage-root", str(self.storage)])
        paths = json.loads(output.getvalue())
        self.assertEqual(
            paths["jsm_training_datasets_dir"],
            str(self.storage / "data" / "datasets" / "jsm"),
        )

    def test_manifests_outside_canonical_directory_rejected(self):
        with self.assertRaises(ValueError):
            load_verified_candidate(self.inpath, self.storage)

    def test_source_training_permission_must_remain_false(self):
        self._tamper_manifest(lambda m: m["sources"][0]["rights"].update(training_allowed=True))
        with self.assertRaises(PermissionError):
            preview_candidate_batch(self.manifest, self.storage)

    def test_batch_training_permission_must_remain_false(self):
        self._tamper_manifest(lambda m: m.update(training_allowed=True))
        with self.assertRaises(PermissionError):
            preview_candidate_batch(self.manifest, self.storage)

    def test_out_of_root_path_rejected(self):
        self._tamper_manifest(lambda m: m["sources"][0].update(processed_relative_path="../untrusted.txt"))
        with self.assertRaises(ValueError):
            preview_candidate_batch(self.manifest, self.storage)

    def test_tampered_processed_object_rejected(self):
        source = json.loads(self.manifest.read_text(encoding="utf-8"))["sources"][0]
        path = self.storage / "data" / "processed" / source["processed_relative_path"]
        path.write_text("Malicious replacement content which is not the same SHA-256.\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            preview_candidate_batch(self.manifest, self.storage)

    def test_missing_processed_object_rejected(self):
        source = json.loads(self.manifest.read_text(encoding="utf-8"))["sources"][0]
        (self.storage / "data" / "processed" / source["processed_relative_path"]).unlink()
        with self.assertRaises(ValueError):
            preview_candidate_batch(self.manifest, self.storage)

    def test_object_count_mismatch_rejected(self):
        self._tamper_manifest(lambda m: m.update(unique_processed_objects=500))
        with self.assertRaises(ValueError):
            preview_candidate_batch(self.manifest, self.storage)

    def test_unexpected_manifest_status_rejected(self):
        self._tamper_manifest(lambda m: m.update(status="train_ready"))
        with self.assertRaises(ValueError):
            preview_candidate_batch(self.manifest, self.storage)

    def test_missing_or_unverified_provenance_rejected(self):
        self._tamper_manifest(lambda m: m["sources"][0]["origin"].update(verification="trusted"))
        with self.assertRaises(ValueError):
            preview_candidate_batch(self.manifest, self.storage)

    def test_preview_limited_token_output(self):
        result = preview_candidate_batch(self.manifest, self.storage, show_tokens=4)
        self.assertEqual(len(result["records"][0]["token_preview"]), 4)
        with self.assertRaises(ValueError):
            preview_candidate_batch(self.manifest, self.storage, show_tokens=101)


if __name__ == "__main__":
    unittest.main()
