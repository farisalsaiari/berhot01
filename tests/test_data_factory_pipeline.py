"""Local Data Factory tests: all writes stay in temporary directories."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from services.data_factory.src.cli import smoke_local
from services.data_factory.src.pipeline import run_local_pipeline


class DataFactoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="berhot-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.intake = self.root / "intake"
        self.intake.mkdir()
        self.storage = self.root / "storage"
        self.source = self.intake / "source.txt"
        self.source.write_text("The synthetic demo entity is assigned identifier azure.\n", encoding="utf-8")
        self.spec = {
            "schema_version": "1.0.0",
            "batch_id": "test-batch-001",
            "sources": [self._entry()],
        }
        self.manifest = self.root / "manifest.json"
        self._save()

    def _entry(self):
        return {
            "source_id": "source-001",
            "relative_path": "source.txt",
            "sha256": hashlib.sha256(self.source.read_bytes()).hexdigest(),
            "origin": {"uri": "fixture://example", "publisher": "BERHOT test"},
            "rights": {
                "retention_allowed": True,
                "analysis_allowed": True,
                "training_allowed": False,
            },
        }

    def _save(self):
        self.manifest.write_text(json.dumps(self.spec), encoding="utf-8")

    def _run(self, **kwargs):
        return run_local_pipeline(self.manifest, self.intake, self.storage, **kwargs)

    def test_complete_smoke(self):
        self.assertEqual(smoke_local()["result"], "passed")

    def test_end_to_end_replay_and_manifest(self):
        first = self._run()
        second = self._run()
        self.assertEqual(first["processed_objects_created"], 1)
        self.assertEqual(second["processed_objects_created"], 0)
        result = json.loads(Path(first["manifest_path"]).read_text(encoding="utf-8"))
        self.assertFalse(result["training_allowed"])
        self.assertFalse(result["sources"][0]["rights"]["training_allowed"])
        self.assertEqual(result["unique_processed_objects"], 1)

    def test_invalid_hash_prevents_publication(self):
        self.spec["sources"][0]["sha256"] = "0" * 64
        self._save()
        with self.assertRaises(ValueError):
            self._run()
        self.assertFalse((self.storage / "data").exists())

    def test_training_rights_cannot_be_self_approved(self):
        self.spec["sources"][0]["rights"]["training_allowed"] = True
        self._save()
        with self.assertRaises(PermissionError):
            self._run()
        self.assertFalse((self.storage / "data").exists())

    def test_retention_and_analysis_required(self):
        self.spec["sources"][0]["rights"]["analysis_allowed"] = False
        self._save()
        with self.assertRaises(PermissionError):
            self._run()

    def test_path_traversal_rejected(self):
        self.spec["sources"][0]["relative_path"] = "../source.txt"
        self._save()
        with self.assertRaises(ValueError):
            self._run()

    def test_symlink_rejected(self):
        alias = self.intake / "alias.txt"
        try:
            alias.symlink_to(self.source)
        except (NotImplementedError, OSError):
            self.skipTest("Symlink creation unavailable")
        self.spec["sources"][0]["relative_path"] = "alias.txt"
        self._save()
        with self.assertRaises(ValueError):
            self._run()

    def test_dry_run_writes_nothing(self):
        self.assertTrue(self._run(dry_run=True)["dry_run"])
        self.assertFalse((self.storage / "data").exists())

    def test_duplicate_bytes_stored_once(self):
        (self.intake / "second.txt").write_bytes(self.source.read_bytes())
        second = self._entry()
        second["source_id"] = "source-002"
        second["relative_path"] = "second.txt"
        self.spec["sources"].append(second)
        self._save()
        result = self._run()
        self.assertEqual(result["sources"], 2)
        self.assertEqual(result["processed_objects_created"], 1)
        self.assertEqual(result["exact_duplicates"], 1)

    def test_immutable_batch_id_rejects_changed_input(self):
        first = self._run()
        self.source.write_text(
            "Another fully different valid synthetic source with amber identifier.\n",
            encoding="utf-8",
        )
        self.spec["sources"][0] = self._entry()
        self._save()
        with self.assertRaises(ValueError):
            self._run()
        self.assertTrue(Path(first["manifest_path"]).exists())


if __name__ == "__main__":
    unittest.main()
