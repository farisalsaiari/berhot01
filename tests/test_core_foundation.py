"""Tests for shared paths and immutable local file publisher."""
import tempfile
import unittest
from pathlib import Path

from core import paths
from core.settings import load_settings
from core.storage import write_immutable_bytes


class FoundationTests(unittest.TestCase):
    def test_global_storage_paths_have_single_parent(self):
        self.assertEqual(paths.DATASETS_DIR, paths.STORAGE_DIR / "data" / "datasets")
        self.assertEqual(paths.MANIFESTS_DIR, paths.STORAGE_DIR / "data" / "manifests")
        self.assertEqual(paths.ARTIFACTS_DIR, paths.STORAGE_DIR / "artifacts")
        self.assertEqual(paths.RELEASES_DIR, paths.STORAGE_DIR / "releases")

    def test_default_settings_valid(self):
        self.assertIn(load_settings().environment, {"development", "test", "production"})

    def test_immutable_write_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "nested" / "object.txt"
            self.assertTrue(write_immutable_bytes(dest, b"first"))
            self.assertFalse(write_immutable_bytes(dest, b"first"))
            with self.assertRaises(ValueError):
                write_immutable_bytes(dest, b"changed")
            self.assertEqual(dest.read_bytes(), b"first")

    def test_repository_root_is_valid(self):
        self.assertTrue((paths.PROJECT_ROOT / ".gitignore").is_file())


if __name__ == "__main__":
    unittest.main()
