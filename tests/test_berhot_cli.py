"""Integration tests for the one-entry-point CLI; no real data or model writes."""
import hashlib
import json
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from pathlib import Path

from berhot.cli import build_parser, main


class BERHOTCLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="berhot-cli-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.intake = self.root / "intake"
        self.intake.mkdir()
        self.storage = self.root / "storage"
        self.source = self.intake / "new-document.txt"
        self.source.write_text(
            "اختبار عربي English synthetic document for BERHOT Data Factory.\n",
            encoding="utf-8",
        )
        self.input_manifest = self.root / "batch.json"
        self._write_input("cli-test-batch")

    def _write_input(self, batch_id):
        doc = self.source.read_bytes()
        spec = {
            "schema_version": "1.0.0",
            "batch_id": batch_id,
            "sources": [{
                "source_id": "example001",
                "relative_path": "new-document.txt",
                "sha256": hashlib.sha256(doc).hexdigest(),
                "origin": {"uri": "fixture://company/document", "publisher": "BERHOT Synthetic"},
                "rights": {
                    "retention_allowed": True,
                    "analysis_allowed": True,
                    "training_allowed": False,
                },
            }],
        }
        self.input_manifest.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")

    def _invoke(self, *args):
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(list(args))
        return code, stdout.getvalue(), stderr.getvalue()

    def _factory_args(self):
        return (
            "--manifest", str(self.input_manifest),
            "--intake-root", str(self.intake),
            "--storage-root", str(self.storage),
        )

    def test_global_help_contains_groups(self):
        result = build_parser().format_help()
        for name in ("data", "tokenizer", "pipeline", "model"):
            self.assertIn(name, result)

    def test_factory_smoke_via_unified_cli(self):
        code, text, errors = self._invoke("data", "smoke")
        self.assertEqual((code, errors), (0, ""))
        self.assertEqual(json.loads(text)["result"], "passed")

    def test_data_inspect_is_read_only(self):
        code, text, errors = self._invoke("data", "inspect", *self._factory_args())
        self.assertEqual((code, errors), (0, ""))
        self.assertTrue(json.loads(text)["dry_run"])
        self.assertFalse((self.storage / "data").exists())

    def test_data_process_and_replay(self):
        args = ("data", "process", *self._factory_args())
        first = self._invoke(*args)
        second = self._invoke(*args)
        self.assertEqual(first[0], 0)
        self.assertEqual(second[0], 0)
        self.assertEqual(json.loads(first[1])["processed_objects_created"], 1)
        self.assertEqual(json.loads(second[1])["processed_objects_created"], 0)

    def test_data_process_dry_run(self):
        code, result, err = self._invoke(
            "data", "process", *self._factory_args(), "--dry-run"
        )
        self.assertEqual((code, err), (0, ""))
        self.assertTrue(json.loads(result)["dry_run"])
        self.assertFalse((self.storage / "data").exists())

    def test_pipeline_end_to_end_and_preview(self):
        code, output, errors = self._invoke(
            "pipeline", "run", *self._factory_args(),
            "--family", "jsm", "--variant", "nano", "--size", "mvp",
        )
        self.assertEqual((code, errors), (0, ""))
        self.assertIn("[PASS] Shared Data Factory published processed CANDIDATE text.", output)
        self.assertIn("[PASS] JSM tokenizer: jsm-byte-utf8-v0", output)
        self.assertIn("[BLOCKED] Training-ready publication", output)
        self.assertFalse((self.storage / "data" / "datasets" / "jsm").exists())

    def test_tokenizer_preview_read_only(self):
        self._invoke("data", "process", *self._factory_args())
        manifest = self.storage / "data" / "manifests" / "local-text" / "cli-test-batch.json"
        code, output, errors = self._invoke(
            "tokenizer", "preview", "--manifest", str(manifest),
            "--storage-root", str(self.storage)
        )
        self.assertEqual((code, errors), (0, ""))
        self.assertIn("[PASS] JSM tokenizer:", output)
        self.assertIn("[SKIP] No JSM dataset shard", output)

    def test_tokenizer_inspect_and_encode(self):
        code, meta, err = self._invoke("tokenizer", "inspect", "--family", "jsm")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(json.loads(meta)["vocab_size"], 259)
        code, output, err = self._invoke(
            "tokenizer", "encode", "--family", "jsm",
            "--text", "أهلاً AI ☕", "--show-tokens", "5",
        )
        self.assertEqual((code, err), (0, ""))
        obj = json.loads(output)
        self.assertEqual(len(obj["first_token_ids"]), 5)
        self.assertTrue(obj["decode_round_trip_ok"])
        self.assertFalse(obj["data_written"])

    def test_pipeline_smoke_synthetic_only(self):
        code, text, errors = self._invoke("pipeline", "smoke")
        self.assertEqual((code, errors), (0, ""))
        self.assertEqual(json.loads(text)["verified_records"], 2)
        self.assertFalse(json.loads(text)["training_ready_export"])

    def test_eligibility_displays_blocked_status(self):
        self._invoke("data", "process", *self._factory_args())
        published = self.storage / "data" / "manifests" / "local-text" / "cli-test-batch.json"
        code, text, errors = self._invoke(
            "data", "eligibility", "--manifest", str(published),
            "--storage-root", str(self.storage), "--family", "jsm"
        )
        self.assertEqual((code, errors), (0, ""))
        obj = json.loads(text)
        self.assertEqual(obj["status"], "BLOCKED_NOT_TRAIN_READY")
        self.assertFalse(obj["training_allowed"])

    def test_factory_rejects_unapproved_training(self):
        self._write_input("new-batch")
        spec = json.loads(self.input_manifest.read_text(encoding="utf-8"))
        spec["sources"][0]["rights"]["training_allowed"] = True
        self.input_manifest.write_text(json.dumps(spec), encoding="utf-8")
        code, output, errors = self._invoke("data", "process", *self._factory_args())
        self.assertEqual(code, 2)
        self.assertIn("training_allowed", errors)
        self.assertFalse((self.storage / "data").exists())

    def test_fann_pipeline_blocked_without_side_effects(self):
        code, output, errors = self._invoke(
            "pipeline", "run", *self._factory_args(),
            "--family", "fann", "--variant", "base", "--size", "mvp",
        )
        self.assertEqual((code, errors), (2, ""))
        self.assertEqual(json.loads(output)["status"], "NOT_IMPLEMENTED")
        self.assertFalse((self.storage / "data").exists())

    def test_future_data_publish_does_not_publish(self):
        code, output, errors = self._invoke(
            "data", "publish", "--batch", "cli-test-batch", "--family", "jsm",
        )
        self.assertEqual((code, errors), (2, ""))
        self.assertFalse(json.loads(output)["executed"])
        self.assertFalse((self.storage / "data").exists())

    def test_future_tokenizer_train_not_implemented(self):
        code, text, err = self._invoke(
            "tokenizer", "train", "--family", "jsm", "--dataset", "jsm-batch-001",
        )
        self.assertEqual((code, err), (2, ""))
        self.assertEqual(json.loads(text)["status"], "NOT_IMPLEMENTED")

    def test_future_model_operations_all_fail_closed(self):
        all_commands = [
            ("train", "--model", "jsm/lara/30b", "--config", "lara-30b.yaml",
             "--dataset", "jsm-batch-001", "--tokenizer", "jsm-v1"),
            ("evaluate", "--run", "run-001"),
            ("infer", "--model", "jsm/lara/30b", "--prompt", "Hi"),
            ("posttrain", "--model", "jsm/lara/30b", "--config", "sft.yaml"),
            ("register", "--run", "run-001"),
        ]
        for args in all_commands:
            with self.subTest(operation=args[0]):
                code, output, errors = self._invoke("model", *args)
                self.assertEqual((code, errors), (2, ""))
                self.assertFalse(json.loads(output)["model_weights_changed"])
        self.assertFalse((self.storage / "artifacts").exists())

    def test_model_list_is_not_an_availability_claim(self):
        code, text, err = self._invoke("model", "list")
        self.assertEqual((code, err), (0, ""))
        obj = json.loads(text)
        self.assertEqual(obj["status"], "ARCHITECTURE_ONLY")
        self.assertEqual(obj["available_trained_models"], [])


if __name__ == "__main__":
    unittest.main()
