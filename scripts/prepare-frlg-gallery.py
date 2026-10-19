import argparse
import hashlib
import json
import re
from pathlib import Path


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(source, repo, output):
    manifest = read(source / "package.json")
    previews = read(source / "apercus.json")
    contracts = read(source / "portes-et-assemblages.json")
    building_contract = read(source / "assemblages-portes.json")
    if contracts.get("archiveSha256", manifest["archive"]["sha256"]) != manifest["archive"]["sha256"]:
        raise ValueError("Le contrat des portes ne correspond pas à l’archive candidate.")
    if building_contract["archiveSha256"] != manifest["archive"]["sha256"] or building_contract["packageVersion"] != manifest["version"]:
        raise ValueError("Le contrat d’assemblage des bâtiments ne correspond pas à l’archive candidate.")
    if len({item["packageId"] for item in previews}) != len(previews):
        raise ValueError("Identifiants natifs dupliqués dans les aperçus standards.")
    assemblies = {item["elementId"]: item for item in contracts["buildingAssemblies"]}
    building_associations = {item["portableElementId"]: item for item in building_contract["buildings"]}
    if len(building_associations) != len(building_contract["buildings"]):
        raise ValueError("Associations de bâtiments dupliquées.")
    resources = {}
    for preview in previews:
        family = preview["family"].split(" / ")
        item = {
            "id": preview["packageId"],
            "sourceId": preview["id"],
            "kind": "element",
            "name": preview["name"],
            "description": preview["description"],
            "family": family[-1],
            "familyPath": family,
            "context": preview["placementContext"],
            "dimension": "2D",
            "role": preview["role"],
            "preview": preview["preview"],
            "previewSha256": preview["previewSha256"],
            "nativeDimensionsPx": preview["nativeDimensionsPx"],
            "frameCount": preview["frameCount"],
            "previewScope": "first-authored-frame",
            "previewCaption": "Première image exacte du décor. L’animation complète se consulte dans Studio.",
            "sourceCount": 1,
            "sourceNames": [preview["name"], preview["id"]],
        }
        assembly = assemblies.get(item["id"])
        if assembly:
            item["rawPreview"] = assembly["rawFacadePreview"]
            item["rawPreviewSha256"] = digest(source / assembly["rawFacadePreview"])
            item["preview"] = assembly["preview"]
            item["previewSha256"] = digest(source / assembly["preview"])
            item["previewScope"] = "explicit-facade-plus-closed-door-preview-only"
            item["previewCaption"] = "Aperçu assemblé : façade + porte fermée. La façade et la porte restent deux ressources indépendantes dans Studio."
        resources[item["id"]] = item
    for group in contracts["doorGroups"]:
        primary = resources[group["primaryId"]]
        group_id = "door:" + primary["id"]
        primary["appearanceGroup"] = group_id
        primary["relatedResourceIds"] = list(dict.fromkeys([primary["id"]] + [item["id"] for item in group["companions"]]))
        for companion in group["companions"]:
            if companion["id"] in resources:
                continue
            resources[companion["id"]] = {
                "id": companion["id"],
                "kind": "element",
                "name": companion["name"],
                "description": "État ou séquence de porte associé à « " + primary["name"] + " ». Composant conservé dans le package ; aucun événement automatique n’est créé.",
                "family": primary["family"],
                "familyPath": primary["familyPath"],
                "context": primary["context"],
                "dimension": "2D",
                "role": companion["role"],
                "frameCount": companion["frameCount"],
                "preview": companion["preview"],
                "previewSha256": digest(source / companion["preview"]),
                "previewScope": "first-authored-frame",
                "previewCaption": "Première image exacte de cet état ou de cette séquence. Les variantes de palette et les états restent distincts.",
                "appearanceGroup": group_id,
                "sourceCount": 1,
                "sourceNames": [companion["name"]],
            }
    for identifier in assemblies:
        if identifier not in resources or identifier not in building_associations:
            raise ValueError("Association de bâtiment absente : " + identifier)
        doors = building_associations[identifier].get("doors", [])
        if not doors:
            raise ValueError("Aucune porte associée au bâtiment : " + identifier)
        related = [identifier]
        for door in doors:
            for key in ["closedElementId", "openingElementId", "closingElementId", "openElementId"]:
                target = door.get(key)
                if target not in resources:
                    raise ValueError("Porte associée absente des ressources illustrées : " + str(target))
                related.append(target)
        resources[identifier]["relatedResourceIds"] = list(dict.fromkeys(related))
        resources[identifier]["relatedResourceLabel"] = "Ressources associées : façade et portes"
    for item in resources.values():
        for key in ["preview", "rawPreview"]:
            if key in item:
                path = Path(item[key])
                if path.is_absolute() or ".." in path.parts or not (source / path).is_file():
                    raise ValueError("Aperçu invalide : " + str(path))
    write(output / "ressources.json", list(resources.values()))
    version = manifest["version"]
    html = (repo / "packages/nb2/0.9.0/galerie.html").read_text()
    html = html.replace("Noir & Blanc 2", "Rouge Feu & Vert Feuille").replace("Unys, pièce par pièce.", "Kanto, pièce par pièce.")
    html = html.replace("VERSION 0.9.0", "VERSION " + version).replace("Release NB2 à publier", "Release FRLG à publier")
    html = html.replace("BIBLIOTHÈQUE MODULAIRE", "CARTES ET DÉCORS · PIXEL ART 2D")
    html = html.replace("Des terrains aux toits, des arbres au mobilier. Retrouvez les ressources de l’inventaire intégré NB2, classées par familles pour créer vos cartes dans Avelune Studio.", "Bâtiments, arbres, mobilier et portes animées : parcourez les décors illustrés et leurs états associés. Les terrains, chemins, bordures et environnements sont également inclus dans le pack et détaillés dans le CSV.")
    html = re.sub(r'<meta name="description" content="[^"]+">', '<meta name="description" content="Décors de Kanto et portes animées FRLG pour Avelune Studio. Recherche, familles, contextes et variantes associées.">', html)
    count = lambda value: f"{value:,}".replace(",", " ")
    html = html.replace("<strong>8 818</strong>", "<strong>" + count(manifest["counts"]["primaryResources"]) + "</strong>")
    html = html.replace("<b>5 506</b><span>modèles 3D</span>", "<b>" + count(len(previews)) + "</b><span>décors standards illustrés</span>")
    html = html.replace("<b>3 981</b><span>motifs de dessin</span>", "<b>" + count(manifest["counts"]["standardPaths"]) + "</b><span>chemins dans le pack</span>")
    html = html.replace("202,7 Mo", str(round(manifest["archive"]["bytes"] / 1000000, 1)).replace(".", ",") + " Mo")
    html = html.replace("<b>0.9.0</b><span>import vérifié</span>", "<b>" + version + "</b><span>vérifications ciblées</span>")
    start = html.index('<details class="compatibility">')
    end = html.index("</details>", start) + len("</details>")
    html = html[:start] + '<details class="compatibility"><summary>Compatibilité, contenu et vérifications</summary><p>Le pack contient des ressources natives éditables de cartes et leurs dépendances. Studio doit prendre en charge le catalogue partitionné et SmartTile 9. La galerie illustre les ' + count(len(previews)) + ' décors standards ainsi que leurs états de portes associés ; elle ne présente pas chaque composant, terrain, chemin, bordure ou environnement du pack. L’inventaire CSV conserve leur liste complète.</p><p>Les images viennent des ressources réelles. Une façade assemblée est explicitement signalée et sa façade seule reste visible dans la fiche. Une image fixe ne prouve pas toute une animation. Les vérifications ciblées du lot sont documentées dans le manifeste ; elles ne certifient pas l’exhaustivité du jeu ni les appareils physiques. <a class="text-link" href="inventaire.json">Consulter la fiche d’inventaire ↗</a></p></details>' + html[end:]
    html = html.replace("Les ressources qui partagent le même aperçu sont réunies sur une fiche. Ouvrez-la pour choisir une variante ou son outil de dessin : aucune variante n’est masquée par les filtres.", "Les portes réunissent leurs états, animations et variantes utiles sur une fiche. Les éléments restent distincts dans le pack et recherchables individuellement. Les façades assemblées sont indiquées dans le détail.")
    html = html.replace("Modèles, sprites, terrains et pinceaux.", "Décors, portes animées, terrains et pinceaux.")
    (output / "bibliotheque.html").write_text(html)
    script = (repo / "site/catalogue.js").read_text()
    old = "resources.length !== manifest.counts.primaryResources"
    current = "resources.length !== (manifest.counts.galleryResources ?? manifest.counts.primaryResources)"
    if old not in script and current not in script:
        raise ValueError("Le contrat du script commun a changé : relire avant de générer le patch.")
    script = script.replace(old, current)
    old = "  if (resource.description) copy.append(node('p', '', resource.description));"
    new = old + "\n  if (resource.previewCaption) copy.append(node('p', 'detail-note', resource.previewCaption));\n  if (resource.rawPreview) {\n    const details = document.createElement('details');\n    details.append(node('summary', '', 'Voir la façade seule, sans porte'));\n    const raw = document.createElement('img');\n    raw.src = resource.rawPreview;\n    raw.alt = resource.name + ' — façade seule';\n    details.append(raw);\n    copy.append(details);\n  }"
    if old not in script:
        raise ValueError("Le détail de la galerie a changé : relire avant de générer le patch.")
    if "if (resource.previewCaption) copy.append" not in script:
        script = script.replace(old, new)
    needle = "  const container = $('resource-detail');"
    if "if (resource.relatedResourceIds) group =" not in script:
        script = script.replace(needle, "  if (resource.relatedResourceIds) group = { resources: resource.relatedResourceIds.map(id => resources.find(item => item.id === id)).filter(Boolean) };\n" + needle)
    script = script.replace("  if (resource.relatedResourceIds) group = { resources: resource.relatedResourceIds.map(id => resources.find(item => item.id === id)).filter(Boolean) };", "  if (resource.relatedResourceIds && !group?.explicitRelations) group = { resources: resource.relatedResourceIds.map(id => resources.find(item => item.id === id)).filter(Boolean), associationLabel: resource.relatedResourceLabel, explicitRelations: true };")
    script = script.replace("node('label', 'variant-picker', 'Variantes et outils associés')", "node('label', 'variant-picker', group.associationLabel || 'Variantes et outils associés')")
    needle = "  if (group.resources.length > 1) copy.append"
    if "Aperçu assemblé : façade + porte" not in script:
        script = script.replace(needle, "  if (resource.rawPreview) copy.append(node('span', 'resource-meta', 'Aperçu assemblé : façade + porte'));\n" + needle)
    (output / "catalogue.js.proposed").write_text(script)
    check = (repo / "scripts/check-site.mjs").read_text()
    if "if (frlg.catalogue.resources) {" not in check:
        check += "\nif (frlg.catalogue.resources) {\n  const illustrated = await read(join(dirname(frlgEntry.manifest), frlg.catalogue.resources));\n  assert.equal(illustrated.length, frlg.counts.galleryResources);\n  assert.equal(new Set(illustrated.map(item => item.id)).size, illustrated.length);\n  assert.equal(groupResources(illustrated).length, frlg.counts.galleryCards);\n  const known = new Set(illustrated.map(item => item.id));\n  for (const resource of illustrated) {\n    assert.ok(resource.familyPath.length && resource.dimension === '2D');\n    assert.ok(['both', 'exterior', 'interior', 'unspecified'].includes(resource.context));\n    for (const id of resource.relatedResourceIds || []) assert.ok(known.has(id));\n    for (const key of ['preview', 'rawPreview']) if (resource[key]) {\n      assert.ok(!resource[key].includes('..') && !resource[key].startsWith('/'));\n      const hash = createHash('sha256').update(await readFile(join(root, dirname(frlgEntry.manifest), resource[key]))).digest('hex');\n      assert.equal(hash, resource[key + 'Sha256']);\n    }\n  }\n  console.log(JSON.stringify({ status: 'valid-frlg-gallery', illustratedResources: illustrated.length, cards: frlg.counts.galleryCards }));\n}\n"
    (output / "check-site.mjs.proposed").write_text(check)
    groups = {item.get("appearanceGroup", item["id"]) for item in resources.values()}
    write(output / "manifest-patch.json", {"version": version, "catalogue": {"gallery": "bibliotheque.html", "resources": "ressources.json"}, "counts": {"galleryResources": len(resources), "galleryCards": len(groups)}, "published": False, "archive": {"url": "https://github.com/yoahnl/avelune-packages/releases/download/frlg-v" + version + "/" + manifest["archive"]["file"]}})
    write(output / "preparation-receipt.json", {"version": version, "standardPreviews": len(previews), "illustratedResources": len(resources), "galleryCards": len(groups), "primaryResourcesUnchanged": manifest["counts"]["primaryResources"], "doorGroups": len(contracts["doorGroups"]), "buildingAssemblies": len(assemblies), "inputArchiveSha256": manifest["archive"]["sha256"], "sharedScriptBaseSha256": digest(repo / "site/catalogue.js"), "inputs": {name: digest(source / name) for name in ["package.json", "apercus.json", "portes-et-assemblages.json", "assemblages-portes.json"]}, "publication": "blocked until canonical native validation, verified GitHub release download and explicit manifest plus registry published activation", "scope": "Illustrated standard decors and associated door components. Other native families remain in complete CSV; gallery is not the complete native resource inventory."})
    return len(resources), len(groups)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    print(prepare(args.source.resolve(), args.repo.resolve(), args.output.resolve()))
