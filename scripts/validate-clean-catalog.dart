import 'dart:convert';
import 'dart:io';
import 'package:map_core/map_core.dart';

void main(List<String> args) {
  final c = ResourcePackCatalog.fromJson(jsonDecode(File(args.single).readAsStringSync()) as Map<String, dynamic>);
  final project = ProjectManifest(name: 'Resource pack validation', version: ProjectVersion.v9, maps: const [], tilesets: c.tilesets, elements: c.elements, models3d: c.models3d, characters: c.characters, smartTileCatalog: c.smartTileCatalog, borderCatalog: c.borderCatalog, environmentPresets: c.environmentPresets, resourceLibraryCatalog: c.resourceLibraryCatalog, elementCategories: c.elementCategories, tilesetFolders: c.tilesetFolders, characterStudioCatalog: c.characterStudioCatalog, settings: ProjectSettings(dimension: ProjectDimension.threeD, spatialCamera: SpatialCameraProfile(), tileWidth: 32, tileHeight: 32));
  ProjectValidator.validate(project);
  stdout.writeln('Native catalog semantics valid');
}
