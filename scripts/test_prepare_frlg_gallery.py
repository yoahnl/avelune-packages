import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SPEC = importlib.util.spec_from_file_location("gallery", HERE / "prepare-frlg-gallery.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SharedGalleryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source = self.root / "input"
        self.output = self.root / "output"
        self.source.mkdir()
        self.output.mkdir()
        for name in ["door.png", "facade.png", "assembled.png", "closed.png"]:
            (self.source / name).write_bytes(b"PNG-fixture-" + name.encode())
        self.manifest = {"version": "1.9.3", "archive": {"file": "FRLG-1.9.3.aveluneassets", "sha256": "a" * 64, "bytes": 100}, "counts": {"primaryResources": 7, "standardPaths": 2}}
        self.previews = []
        for identifier, name in [("door", "Porte — ouverture"), ("facade", "Façade — porte séparée")]:
            self.previews.append({"id": identifier + "-source", "packageId": identifier, "name": name, "description": name, "family": "Décors / Portes" if identifier == "door" else "Décors / Bâtiments", "placementContext": "exterior", "role": "standard", "preview": identifier + ".png", "previewSha256": MODULE.digest(self.source / (identifier + ".png")), "nativeDimensionsPx": [32, 64], "frameCount": 4 if identifier == "door" else 1})
        companion = {"id": "closed", "name": "Porte fermée", "role": "component", "frameCount": 1, "preview": "closed.png"}
        self.contract = {"doorGroups": [{"primaryId": "door", "companions": [companion, companion]}], "buildingAssemblies": [{"elementId": "facade", "preview": "assembled.png", "rawFacadePreview": "facade.png"}]}
        self.building_contract = {"packageVersion": self.manifest["version"], "archiveSha256": self.manifest["archive"]["sha256"], "buildings": [{"portableElementId": "facade", "doors": [{"closedElementId": "closed", "openingElementId": "door", "closingElementId": "door", "openElementId": "closed"}]}]}
        MODULE.write(self.source / "package.json", self.manifest)
        MODULE.write(self.source / "apercus.json", self.previews)
        MODULE.write(self.source / "portes-et-assemblages.json", self.contract)
        MODULE.write(self.source / "assemblages-portes.json", self.building_contract)
        MODULE.prepare(self.source, REPO, self.output)
        self.resources = json.loads((self.output / "ressources.json").read_text())

    def tearDown(self):
        self.temporary.cleanup()

    def test_native_ids_and_shared_state_are_not_duplicated(self):
        by_id = {item["id"]: item for item in self.resources}
        self.assertEqual(set(by_id), {"door", "closed", "facade"})
        self.assertEqual(by_id["door"]["relatedResourceIds"], ["door", "closed"])
        self.assertEqual(by_id["closed"]["appearanceGroup"], by_id["door"]["appearanceGroup"])

    def test_assembled_preview_retains_native_facade_and_caption(self):
        facade = next(item for item in self.resources if item["id"] == "facade")
        self.assertEqual(facade["preview"], "assembled.png")
        self.assertEqual(facade["rawPreview"], "facade.png")
        self.assertIn("indépendantes", facade["previewCaption"])
        self.assertEqual(facade["relatedResourceIds"], ["facade", "closed", "door"])
        self.assertEqual(facade["relatedResourceLabel"], "Ressources associées : façade et portes")
        self.assertNotIn("appearanceGroup", facade)
        script = (self.output / "catalogue.js.proposed").read_text()
        self.assertIn("copy.append(node('span', 'resource-meta', 'Aperçu assemblé : façade + porte'))", script)

    def test_gallery_counts_do_not_redefine_native_inventory(self):
        patch = json.loads((self.output / "manifest-patch.json").read_text())
        self.assertEqual(patch["counts"], {"galleryResources": 3, "galleryCards": 2})
        self.assertNotIn("primaryResources", patch["counts"])
        self.assertFalse(patch["published"])
        html = (self.output / "bibliotheque.html").read_text()
        self.assertIn("<strong>7</strong>", html)
        self.assertIn("elle ne présente pas chaque composant", html)

    def test_shared_theme_filters_and_relative_links_are_preserved(self):
        html = (self.output / "bibliotheque.html").read_text()
        for value in ["../../../site/catalogue.js", "../../../site/dark.css", "brand/avelune-studio.svg"]:
            self.assertIn(value, html)
        for identifier in ["family", "kind", "context", "dimension", "sort", "resource-dialog", "pagination"]:
            self.assertIn('id="' + identifier + '"', html)
        self.assertNotIn("Noir & Blanc 2", html)
        self.assertNotIn("/Users/", html)

    def test_missing_native_preview_rejects_publication(self):
        (self.source / "closed.png").unlink()
        with self.assertRaises(FileNotFoundError):
            MODULE.prepare(self.source, REPO, self.output)

    def test_stale_door_contract_is_rejected(self):
        self.contract["archiveSha256"] = "b" * 64
        MODULE.write(self.source / "portes-et-assemblages.json", self.contract)
        with self.assertRaises(ValueError):
            MODULE.prepare(self.source, REPO, self.output)

    def test_duplicate_native_preview_id_is_rejected(self):
        self.previews.append(self.previews[0])
        MODULE.write(self.source / "apercus.json", self.previews)
        with self.assertRaises(ValueError):
            MODULE.prepare(self.source, REPO, self.output)

    def test_missing_building_association_is_rejected(self):
        self.building_contract["buildings"] = []
        MODULE.write(self.source / "assemblages-portes.json", self.building_contract)
        with self.assertRaises(ValueError):
            MODULE.prepare(self.source, REPO, self.output)

    def test_unknown_associated_door_is_rejected(self):
        self.building_contract["buildings"][0]["doors"][0]["openingElementId"] = "invented-target"
        MODULE.write(self.source / "assemblages-portes.json", self.building_contract)
        with self.assertRaises(ValueError):
            MODULE.prepare(self.source, REPO, self.output)

    def test_stale_building_association_is_rejected(self):
        self.building_contract["archiveSha256"] = "b" * 64
        MODULE.write(self.source / "assemblages-portes.json", self.building_contract)
        with self.assertRaises(ValueError):
            MODULE.prepare(self.source, REPO, self.output)

    def test_generator_is_deterministic_without_mutating_sources(self):
        before = {path.name: MODULE.digest(path) for path in self.output.iterdir()}
        source = {path.name: MODULE.digest(path) for path in self.source.iterdir()}
        shared = MODULE.digest(REPO / "site/catalogue.js")
        MODULE.prepare(self.source, REPO, self.output)
        self.assertEqual(before, {path.name: MODULE.digest(path) for path in self.output.iterdir()})
        self.assertEqual(source, {path.name: MODULE.digest(path) for path in self.source.iterdir()})
        self.assertEqual(shared, MODULE.digest(REPO / "site/catalogue.js"))


if __name__ == "__main__":
    unittest.main()
