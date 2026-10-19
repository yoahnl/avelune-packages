import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:archive/archive.dart';
import 'package:map_core/map_core.dart';
import 'package:map_distribution/map_distribution.dart';

final class FileSink implements ResourcePackArchiveSink {
  FileSink(this.target) : temporary = File('${target.path}.partial') {
    if (target.existsSync() || temporary.existsSync()) throw StateError('Output already exists');
    handle = temporary.openSync(mode: FileMode.writeOnly);
  }
  final File target;
  final File temporary;
  late final RandomAccessFile handle;
  bool closed = false;
  @override
  Future<void> write(Uint8List chunk) async => handle.writeFromSync(chunk);
  @override
  Future<void> finish() async {
    handle.flushSync();
    handle.closeSync();
    closed = true;
    temporary.renameSync(target.path);
  }
  @override
  Future<void> abort() async {
    if (!closed) handle.closeSync();
    if (temporary.existsSync()) temporary.deleteSync();
  }
}

Future<void> main(List<String> args) async {
  if (args.length != 4) throw ArgumentError('Expected original pack, snapshot, cleaned catalog and destination');
  final source = File(args[0]);
  final snapshot = jsonDecode(File(args[1]).readAsStringSync()) as Map<String, dynamic>;
  final catalog = ResourcePackCatalog.fromJson(jsonDecode(File(args[2]).readAsStringSync()) as Map<String, dynamic>);
  final manifest = ResourcePackManifest.fromJson(snapshot['manifest'] as Map<String, dynamic>);
  final archive = ZipDecoder().decodeBytes(source.readAsBytesSync(), verify: true);
  final metadata = manifest.pack.toJson()..['version'] = '0.9.0';
  metadata['provenance'] = '${metadata['provenance']} Version 0.9 : regroupement conservateur des définitions graphiques et comportementales équivalentes ; traçabilité des alias conservée dans le catalogue public.';
  final paths = {for (final file in catalog.files) file.archivePath};
  final documents = {...manifest.content.files.where((f) => f.path.startsWith('licenses/')).map((f) => f.path)};
  final inventory = {for (final file in manifest.content.files) file.path: file};
  final sources = <ResourcePackBuildSource>[];
  for (final path in {...paths, ...documents}) {
    final item = archive.findFile(path);
    if (item == null) throw StateError('Missing source $path');
    final bytes = item.content as List<int>;
    final file = inventory[path]!;
    sources.add(ResourcePackBuildSource(path: path, byteLength: file.byteLength, rawSha256: file.rawSha256, mediaType: file.mediaType, openRead: () async* {
      for (var offset = 0; offset < bytes.length; offset += 65536) {
        yield bytes.sublist(offset, offset + 65536 < bytes.length ? offset + 65536 : bytes.length);
      }
    }));
  }
  final destination = File(args[3]);
  destination.parent.createSync(recursive: true);
  stdout.writeln(jsonEncode({'pid': pid, 'phase': 'build', 'resources': ResourcePackDependencyGraph.fromCatalog(catalog).validateAll().resources.length, 'files': catalog.files.length}));
  final result = await const ResourcePackBuilder().build(metadata: ResourcePackMetadata.fromJson(metadata), catalog: catalog, tileWidth: manifest.compatibility.tileWidth, tileHeight: manifest.compatibility.tileHeight, sources: sources, sink: FileSink(destination));
  File('${destination.path}.sha256').writeAsStringSync('${result.archiveRawSha256}  ${destination.uri.pathSegments.last}\n', flush: true);
  File('${destination.path}.receipt.json').writeAsStringSync(jsonEncode({'manifest': result.manifest.toJson(), 'archiveBytes': result.archiveBytes, 'sha256': result.archiveRawSha256}), flush: true);
  stdout.writeln(jsonEncode({'phase': 'complete', 'bytes': result.archiveBytes, 'sha256': result.archiveRawSha256}));
}
