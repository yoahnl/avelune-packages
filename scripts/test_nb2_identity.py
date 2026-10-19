import io
import json
import struct
import unittest

from PIL import Image, PngImagePlugin

from nb2_identity import glb_identity, png_identity, surface_identity


class SurfaceIdentityTest(unittest.TestCase):
    def geometry(self, split=False, uv_shift=0, height=0, color=1):
        positions = [(0, height, 0), (1, height, 0), (1, height, 1), (0, height, 1)]
        if split:
            positions.append((0.5, height, 0.5))
        return {'POSITION': positions, 'TEXCOORD_0': [(p[0] + uv_shift, p[2]) for p in positions], 'COLOR_0': [(color, color, color, 1)] * len(positions)}

    def test_retessellation_preserves_surface(self):
        a = surface_identity(self.geometry(), [0, 1, 2, 0, 2, 3])
        b = surface_identity(self.geometry(True), [0, 1, 4, 1, 2, 4, 2, 3, 4, 3, 0, 4])
        self.assertEqual(a, b)

    def test_real_geometry_color_uv_and_winding_variants_survive(self):
        base = surface_identity(self.geometry(), [0, 1, 2, 0, 2, 3])
        for geometry in [self.geometry(height=1), self.geometry(color=0.5), self.geometry(uv_shift=0.5)]:
            self.assertNotEqual(base, surface_identity(geometry, [0, 1, 2, 0, 2, 3]))
        self.assertNotEqual(base, surface_identity(self.geometry(), [0, 2, 1, 0, 3, 2]))

    def test_wrapped_integer_uv_shift_only(self):
        indices = [0, 1, 2, 0, 2, 3]
        repeats = {'TEXCOORD_0': [True, True]}
        self.assertEqual(surface_identity(self.geometry(), indices, repeats), surface_identity(self.geometry(uv_shift=2), indices, repeats))
        self.assertNotEqual(surface_identity(self.geometry(), indices), surface_identity(self.geometry(uv_shift=2), indices))

    def test_holes_and_overlap_survive(self):
        geometry = self.geometry(True)
        base = surface_identity(geometry, [0, 1, 4, 1, 2, 4, 2, 3, 4, 3, 0, 4])
        self.assertNotEqual(base, surface_identity(geometry, [0, 1, 4, 1, 2, 4, 2, 3, 4]))
        self.assertNotEqual(base, surface_identity(geometry, [0, 1, 4, 1, 2, 4, 2, 3, 4, 3, 0, 4, 0, 1, 4]))

    def test_subpixel_difference_survives(self):
        a = self.geometry()
        b = self.geometry()
        b['POSITION'][1] = (1.0000001192092896, 0, 0)
        self.assertNotEqual(surface_identity(a, [0, 1, 2, 0, 2, 3]), surface_identity(b, [0, 1, 2, 0, 2, 3]))

    def test_png_provenance_is_ignored_but_pixels_and_alpha_are_preserved(self):
        def png(color, label):
            stream = io.BytesIO()
            info = PngImagePlugin.PngInfo()
            info.add_itxt('aveluneSource', label)
            Image.new('RGBA', (2, 2), color).save(stream, format='PNG', pnginfo=info)
            return stream.getvalue()
        a = png((1, 2, 3, 255), 'Route 19')
        self.assertEqual(png_identity(a), png_identity(png((1, 2, 3, 255), 'Pavonnay')))
        self.assertNotEqual(png_identity(a), png_identity(png((1, 2, 3, 254), 'Route 19')))

    def glb(self, extras):
        positions = struct.pack('<9f', 0, 0, 0, 1, 0, 0, 0, 0, 1)
        document = {'asset': {'version': '2.0'}, 'scene': 0, 'scenes': [{'nodes': [0]}], 'nodes': [{'mesh': 0}], 'meshes': [{'primitives': [{'attributes': {'POSITION': 0}, 'material': 0}]}], 'materials': [{'extensions': {'KHR_materials_unlit': {}}}], 'buffers': [{'byteLength': len(positions)}], 'bufferViews': [{'buffer': 0, 'byteLength': len(positions)}], 'accessors': [{'bufferView': 0, 'componentType': 5126, 'count': 3, 'type': 'VEC3'}], 'extras': extras}
        encoded = json.dumps(document).encode()
        encoded += b' ' * (-len(encoded) % 4)
        return struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(positions)) + struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(positions), 0x004e4942) + positions

    def test_static_source_metadata_is_ignored_and_unknown_extras_are_preserved(self):
        a = self.glb({'aveluneSource': {'map': 'Route 19'}})
        b = self.glb({'aveluneSource': {'map': 'Pavonnay'}})
        self.assertEqual(glb_identity(a), glb_identity(b))
        self.assertNotEqual(glb_identity(a), glb_identity(self.glb({'runtimeField': 1})))

    def test_animated_material_sources_are_never_merged_by_static_geometry(self):
        a = self.glb({'aveluneMaterialAnimations': {'clips': [{'durationSeconds': 1}]}})
        b = self.glb({'aveluneMaterialAnimations': {'clips': [{'durationSeconds': 2}]}})
        self.assertEqual(glb_identity(a)[1], 'animated-byte-exact')
        self.assertNotEqual(glb_identity(a), glb_identity(b))


if __name__ == '__main__':
    unittest.main()
