import collections
import hashlib
import io
import json
import struct
from fractions import Fraction

from PIL import Image


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def png_identity(data):
    chunks = [data[:8]]
    offset = 8
    while offset < len(data):
        length = struct.unpack_from('>I', data, offset)[0]
        kind = data[offset + 4:offset + 8]
        if kind not in {b'iTXt', b'tEXt', b'zTXt'}:
            chunks.append(data[offset:offset + length + 12])
        offset += length + 12
    with Image.open(io.BytesIO(b''.join(chunks))) as image:
        if getattr(image, 'n_frames', 1) != 1:
            return hashlib.sha256(data).hexdigest()
        header = json.dumps([image.size, {k: str(image.info[k]) for k in ['gamma', 'icc_profile', 'srgb'] if k in image.info}], sort_keys=True).encode()
        return hashlib.sha256(header + image.convert('RGBA').tobytes()).hexdigest()


def rational(value):
    result = Fraction(value)
    return f'{result.numerator}/{result.denominator}'


def vector_sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def affine(points, values, axes):
    a, b, c = [(p[axes[0]], p[axes[1]]) for p in points]
    determinant = (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])
    result = []
    for va, vb, vc in zip(*values):
        x = ((vb - va) * (c[1] - a[1]) - (vc - va) * (b[1] - a[1])) / determinant
        y = ((b[0] - a[0]) * (vc - va) - (c[0] - a[0]) * (vb - va)) / determinant
        result.append((x, y, va - x * a[0] - y * a[1]))
    return result


def surface_identity(attributes, indices, repeats=None, details=False):
    repeats = repeats or {}
    positions = [tuple(Fraction(v) for v in point) for point in attributes['POSITION']]
    channels = {key: [tuple(Fraction(v) for v in row) for row in values] for key, values in attributes.items() if key != 'POSITION'}
    surfaces = collections.defaultdict(list)
    degenerate = []
    for i in range(0, len(indices), 3):
        ids = indices[i:i + 3]
        points = [positions[j] for j in ids]
        normal = cross(vector_sub(points[1], points[0]), vector_sub(points[2], points[0]))
        if not any(normal):
            degenerate.append(json.dumps({key: [[rational(v) for v in rows[j]] for j in ids] for key, rows in attributes.items()}, sort_keys=True))
            continue
        divisor = abs(next(v for v in normal if v))
        normal = tuple(v / divisor for v in normal)
        drop = max(range(3), key=lambda axis: abs(normal[axis]))
        axes = [axis for axis in range(3) if axis != drop]
        fields = []
        for channel, values in sorted(channels.items()):
            coeffs = affine(points, [values[j] for j in ids], axes)
            for component, repeat in enumerate(repeats.get(channel, [])):
                if repeat and component < len(coeffs):
                    x, y, offset = coeffs[component]
                    coeffs[component] = (x, y, offset % 1)
            fields.append((channel, [[rational(v) for v in row] for row in coeffs]))
        key = json.dumps([[rational(v) for v in normal], rational(dot(normal, points[0])), fields], sort_keys=True)
        for a, b in zip(points, points[1:] + points[:1]):
            if a != b:
                surfaces[key].append((a, b))
    result = []
    for surface, edges in sorted(surfaces.items()):
        lines = collections.defaultdict(collections.Counter)
        for a, b in edges:
            delta = vector_sub(b, a)
            axis = next(i for i, v in enumerate(delta) if v)
            direction = tuple(v / delta[axis] for v in delta)
            moment = cross(a, direction)
            key = json.dumps([[rational(v) for v in direction], [rational(v) for v in moment]])
            sign = 1 if b[axis] > a[axis] else -1
            start, end = sorted([a[axis], b[axis]])
            lines[key][start] += sign
            lines[key][end] -= sign
        boundary = []
        for line, events in sorted(lines.items()):
            count = 0
            previous = None
            segments = []
            for point, change in sorted(events.items()):
                if previous is not None and count:
                    if segments and segments[-1][2] == count and segments[-1][1] == rational(previous):
                        segments[-1][1] = rational(point)
                    else:
                        segments.append([rational(previous), rational(point), count])
                count += change
                previous = point
            if count:
                raise ValueError('Unclosed edge interval')
            if segments:
                boundary.append([line, segments])
        result.append([surface, boundary])
    return [result, sorted(degenerate)] if details else digest([result, sorted(degenerate)])


def glb_identity(data, details=False):
    length = struct.unpack_from('<I', data, 12)[0]
    document = json.loads(data[20:20 + length])
    if document.get('animations') or document.get('skins') or document.get('extras', {}).get('aveluneMaterialAnimations'):
        return hashlib.sha256(data).hexdigest(), 'animated-byte-exact'
    binary = data[28 + length:]
    views = document.get('bufferViews', [])
    ignored_extras = {'aveluneSource', 'aveluneSourceCellExtraction', 'nb2SourceUnit', 'sourceMaterials', 'aveluneNitroMaterial', 'nb2Lot02SourceComposition', 'nb2ReusableWhiteFence'}

    def strip(value):
        if isinstance(value, dict):
            result = {}
            for key, item in value.items():
                if key == 'name':
                    continue
                if key == 'extras':
                    item = {k: v for k, v in item.items() if k not in ignored_extras}
                    if not item:
                        continue
                result[key] = strip(item)
            return result
        if isinstance(value, list):
            return [strip(item) for item in value]
        return value

    def view_bytes(index):
        view = views[index]
        if view.get('buffer', 0) != 0:
            raise ValueError('External buffer')
        offset = view.get('byteOffset', 0)
        return binary[offset:offset + view['byteLength']]

    def accessor(index):
        item = document['accessors'][index]
        if 'sparse' in item or item['type'].startswith('MAT'):
            raise ValueError('Unsupported accessor')
        code, size = {5120: ('b', 1), 5121: ('B', 1), 5122: ('h', 2), 5123: ('H', 2), 5125: ('I', 4), 5126: ('f', 4)}[item['componentType']]
        count = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[item['type']]
        view = views[item['bufferView']]
        raw = view_bytes(item['bufferView'])
        stride = view.get('byteStride', count * size)
        offset = item.get('byteOffset', 0)
        values = [struct.unpack_from('<' + code * count, raw, offset + i * stride) for i in range(item['count'])]
        if item.get('normalized'):
            maximum = {5120: 127, 5121: 255, 5122: 32767, 5123: 65535}[item['componentType']]
            values = [tuple(max(Fraction(-1), Fraction(v, maximum)) for v in row) for row in values]
        return values

    def image(index):
        item = document['images'][index]
        if 'bufferView' not in item:
            raise ValueError('External image')
        raw = view_bytes(item['bufferView'])
        return png_identity(raw) if item.get('mimeType') == 'image/png' else hashlib.sha256(raw).hexdigest()

    def texture(index):
        item = document['textures'][index]
        sampler = document.get('samplers', [])[item['sampler']] if 'sampler' in item else {}
        return {'image': image(item['source']), 'sampler': strip(sampler)}

    def material(index):
        item = strip(document['materials'][index])

        def resolve(value):
            if isinstance(value, dict):
                return {k: texture(v) if k == 'index' else resolve(v) for k, v in value.items()}
            if isinstance(value, list):
                return [resolve(v) for v in value]
            return value

        return resolve(item)

    def mesh(index):
        item = document['meshes'][index]
        if item.get('weights') or any(p.get('targets') for p in item['primitives']):
            raise ValueError('Morph geometry')
        primitives = []
        for primitive in item['primitives']:
            if primitive.get('mode', 4) != 4 or primitive.get('extensions'):
                raise ValueError('Unsupported geometry mode')
            attributes = {key: accessor(value) for key, value in primitive['attributes'].items()}
            indices = [row[0] for row in accessor(primitive['indices'])] if 'indices' in primitive else list(range(len(attributes['POSITION'])))
            if len(indices) % 3:
                raise ValueError('Incomplete triangle')
            repeats = {}
            if 'material' in primitive:
                mat = document['materials'][primitive['material']]
                if 'KHR_materials_unlit' in mat.get('extensions', {}):
                    attributes.pop('NORMAL', None)
                    attributes.pop('TANGENT', None)
                for field in ['baseColorTexture', 'metallicRoughnessTexture']:
                    tex = mat.get('pbrMetallicRoughness', {}).get(field)
                    if tex:
                        texdef = document['textures'][tex['index']]
                        sampler = document.get('samplers', [])[texdef['sampler']] if 'sampler' in texdef else {}
                        if not tex.get('extensions'):
                            repeats['TEXCOORD_' + str(tex.get('texCoord', 0))] = [sampler.get('wrapS', 10497) == 10497, sampler.get('wrapT', 10497) == 10497]
            primitives.append({'material': material(primitive['material']) if 'material' in primitive else None, 'surface': surface_identity(attributes, indices, repeats, details), 'extras': strip(primitive.get('extras', {}))})
        return {'primitives': primitives, 'extras': strip(item.get('extras', {}))}

    def node(index, ancestry=frozenset()):
        if index in ancestry:
            raise ValueError('Cyclic scene')
        item = strip(document['nodes'][index])
        if 'mesh' in item:
            item['mesh'] = mesh(item['mesh'])
        if 'children' in item:
            item['children'] = [node(child, ancestry | {index}) for child in item['children']]
        return item

    try:
        result = {k: strip(v) for k, v in document.items() if k not in {'asset', 'scenes', 'scene', 'nodes', 'meshes', 'accessors', 'bufferViews', 'buffers', 'images', 'textures', 'samplers', 'materials', 'extras'}}
        result['extras'] = strip({'extras': document.get('extras', {})}).get('extras', {})
        result['scene'] = [node(index) for index in document['scenes'][document.get('scene', 0)].get('nodes', [])]
        return (result if details else digest(result)), 'exact-static-surfaces'
    except (ValueError, KeyError, IndexError, struct.error):
        return hashlib.sha256(data).hexdigest(), 'unsupported-byte-exact'
