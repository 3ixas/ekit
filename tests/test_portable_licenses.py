"""Raw downloaded directories retain required offline licence terms."""
import json
import pathlib
import tarfile
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
APACHE_SECTIONS = (
    "1. Definitions.", "2. Grant of Copyright License.", "3. Grant of Patent License.",
    "4. Redistribution.", "5. Submission of Contributions.", "6. Trademarks.",
    "7. Disclaimer of Warranty.", "8. Limitation of Liability.",
    "9. Accepting Warranty or Additional Liability.", "END OF TERMS AND CONDITIONS")


class PortableLicenseTests(unittest.TestCase):
    def assert_apache_terms(self, text):
        for section in APACHE_SECTIONS:
            self.assertIn(section, text)
        self.assertIn("Derivative Works a copy of this License", text)

    def test_every_canonical_apache_family_has_complete_terms(self):
        for path in sorted((ROOT / "licenses").glob("apache-2.0-*.txt")):
            with self.subTest(licence=path.name):
                self.assert_apache_terms(path.read_text())

    def test_raw_humanlayer_directories_include_terms_and_the_actual_attribution(self):
        checked = set()
        for lifecycle in ("skills", "candidates", "paused"):
            for metadata in sorted((ROOT / lifecycle).glob("*/*/metadata.json")):
                data = json.loads(metadata.read_text())
                if not any(source["license"] == "apache-2.0-humanlayer" for source in data["sources"]):
                    continue
                with self.subTest(owner=data["id"]), tempfile.TemporaryDirectory() as temp:
                    directory = pathlib.Path(temp)
                    archive = directory / "raw-directory.tar"
                    with tarfile.open(archive, "w") as output:
                        output.add(metadata.parent, arcname=data["id"])
                    extracted = directory / "download"
                    with tarfile.open(archive) as downloaded:
                        downloaded.extractall(extracted, filter="data")
                    # No selective export helper or repository-root licences participate.
                    self.assertEqual([p.name for p in extracted.iterdir()], [data["id"]])
                    terms = (extracted / data["id"] / "references/licenses/apache-2.0-humanlayer.txt").read_text()
                    self.assert_apache_terms(terms)
                    self.assertIn("Copyright (c) 2024, humanlayer Authors", terms)
                    checked.add(data["id"])
        self.assertTrue({"handoff", "grill-with-docs"}.issubset(checked))
