import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:map_authoring/map_authoring.dart';
import 'package:map_core/map_core.dart';

Future<void> main(List<String> args) async {
  if (args.length != 3) throw ArgumentError('Expected package, fresh canonical project and proof destination');
  final root = Directory(args[1]).resolveSymbolicLinksSync();
  const reader = LocalProjectFileReader();
  final policy = await WorkspacePolicy.create(allowedRootPaths: [root], fileReader: reader);
  final handles = WorkspaceHandleStore();
  final loader = ProjectSnapshotLoader(handles: handles);
  final service = ProjectOpenService(policy: policy, fileReader: reader, handles: handles);
  final opened = await service.openProject(root);
  final mutations = LocalMapAuthoringMutationApi(policy: policy, snapshotLoader: loader, resourcePackSourceRoots: [root]);
  await mutations.attachProject(projectRootPath: root, workspaceHandle: opened.workspaceHandle, projectHandle: opened.projectHandle);
  final api = LocalResourcePackTransferApi(mutations: mutations, snapshotLoader: loader);
  final records = <String, Object?>{};
  stdout.writeln(jsonEncode({'pid': pid, 'phase': 'open', 'project': root}));
  Future<Map<String, Object?>> call(String verb, Map<String, Object?> input) => api.transfer(opened.projectHandle, verb: verb, input: input);
  Future<Map<String, Object?>> job(String verb, Map<String, Object?> input) async {
    final started = await call(verb, input);
    String? previous;
    while (true) {
      final current = await call('get', {'jobId': started['jobId']});
      final snapshot = current['snapshot'] as Map;
      final status = '${snapshot['state']}:${current['phase']}';
      if (status != previous) {
        stdout.writeln(jsonEncode({'verb': verb, 'status': status}));
        previous = status;
      }
      if (snapshot['state'] == 'failed' || snapshot['state'] == 'cancelled') throw StateError(jsonEncode(current));
      if (snapshot['state'] == 'succeeded') {
        records[verb] = current;
        return Map<String, Object?>.from(current['result'] as Map);
      }
      await Future<void>.delayed(const Duration(milliseconds: 500));
    }
  }
  try {
    final staged = await job('stage', {'sourcePath': File(args[0]).resolveSymbolicLinksSync()});
    final inspected = await job('inspect', {'archiveHandle': staged['archiveHandle']});
    final selection = await call('selection.create', {'mode': 'archive', 'inspectionHandle': inspected['inspectionHandle']});
    final selected = await call('selection.select_filtered', {'selectionHandle': selection['selectionHandle'], 'revision': selection['revision'], 'filter': <String, Object?>{}});
    final before = await loader.load(opened.projectHandle);
    final prepared = await job('prepare', {'selectionHandle': selected['selectionHandle'], 'revision': selected['revision'], 'expectedRevision': before.revision, 'conflictPolicy': 'preserveProject'});
    final plan = await mutations.planMutation(opened.projectHandle, AuthoringRequest(requestId: 'qualify-clean-nb2', actionId: 'resource_pack.import', actionVersion: 1, workspaceHandle: opened.workspaceHandle.value, expectedRevision: before.revision, idempotencyKey: 'qualify-clean-nb2-090', parameters: {'preparedImportHandle': prepared['preparedImportHandle']}));
    stdout.writeln(jsonEncode({'phase': 'planned', 'planId': plan.planId}));
    final confirmation = await mutations.confirmMutation(opened.projectHandle, planId: plan.planId);
    await job('start_apply', {'planId': plan.planId, 'operationId': 'qualify-clean-nb2-090', 'confirmationToken': confirmation.confirmationToken});
    final after = await loader.load(opened.projectHandle);
    ProjectValidator.validate(after.manifest);
    final manifest = after.manifest;
    final counts = {'models3d': manifest.models3d.length, 'tilesets': manifest.tilesets.length, 'characters': manifest.characters.length, 'elements': manifest.elements.length, 'environmentPresets': manifest.environmentPresets.length, 'smartTilePresets': manifest.smartTileCatalog.presets.length, 'smartTilePatterns': manifest.smartTileCatalog.patterns.length, 'borderBlueprints': manifest.borderCatalog.records.length};
    records['counts'] = counts;
    records['revision'] = after.revision;
    records['sourceSha256'] = inspected['archiveRawSha256'];
    records['canonicalImport'] = true;
    await api.closeTransferWorkspace(opened.workspaceHandle);
    await mutations.detachWorkspace(opened.workspaceHandle);
    handles.closeWorkspace(opened.workspaceHandle);
    final reopened = await service.openProject(root);
    final snapshot = await loader.load(reopened.projectHandle);
    ProjectValidator.validate(snapshot.manifest);
    records['strictReopen'] = true;
    records['reopenedRevision'] = snapshot.revision;
    handles.closeWorkspace(reopened.workspaceHandle);
    File(args[2]).writeAsStringSync(jsonEncode(records), flush: true);
    stdout.writeln(jsonEncode({'phase': 'complete', 'counts': counts, 'strictReopen': true, 'sourceSha256': records['sourceSha256']}));
  } catch (error) {
    File('${args[2]}.error').writeAsStringSync(error.toString());
    rethrow;
  } finally {
    try { await api.closeTransferWorkspace(opened.workspaceHandle); } catch (_) {}
    try { await mutations.detachWorkspace(opened.workspaceHandle); } catch (_) {}
    handles.closeWorkspace(opened.workspaceHandle);
  }
}
