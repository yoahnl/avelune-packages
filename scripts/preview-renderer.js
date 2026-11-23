import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, preserveDrawingBuffer: true });
renderer.setSize(256, 224);
renderer.setPixelRatio(1);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.setClearColor(0x000000, 0);
const scene = new THREE.Scene();
scene.add(new THREE.HemisphereLight(0xffffff, 0xb6c3cd, 2));
const light = new THREE.DirectionalLight(0xffffff, 2);
light.position.set(-3, 7, 5);
scene.add(light);
const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 1000);
const loader = new GLTFLoader();
const canvas = document.createElement('canvas');
canvas.width = 256;
canvas.height = 224;
const context = canvas.getContext('2d');

window.renderResource = async task => {
  const url = '/' + task.source;
  if (task.kind === 'image') {
    const image = await createImageBitmap(await (await fetch(url)).blob());
    const crop = task.crop || [0, 0, image.width, image.height];
    if (crop[0] < 0 || crop[1] < 0 || crop[0] + crop[2] > image.width || crop[1] + crop[3] > image.height) throw new Error('Crop outside source');
    const scale = Math.min(224 / crop[2], 192 / crop[3], 5);
    const width = crop[2] * scale, height = crop[3] * scale;
    context.clearRect(0, 0, 256, 224);
    context.imageSmoothingEnabled = false;
    context.drawImage(image, ...crop, (256 - width) / 2, (224 - height) / 2, width, height);
    image.close();
    return canvas.toDataURL('image/png');
  }
  const loaded = await loader.loadAsync(url);
  const object = loaded.scene;
  const box = new THREE.Box3().setFromObject(object);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  object.position.sub(center);
  scene.add(object);
  const span = Math.max(size.x, size.y, size.z, 0.01);
  camera.position.set(span * 2, span * 1.7, span * 3);
  camera.lookAt(0, 0, 0);
  const vertical = span * 0.83;
  camera.left = -vertical * 256 / 224;
  camera.right = vertical * 256 / 224;
  camera.top = vertical;
  camera.bottom = -vertical;
  camera.far = span * 30 + 10;
  camera.updateProjectionMatrix();
  renderer.render(scene, camera);
  const result = renderer.domElement.toDataURL('image/png');
  scene.remove(object);
  object.traverse(node => {
    node.geometry?.dispose();
    for (const material of Array.isArray(node.material) ? node.material : node.material ? [node.material] : []) {
      for (const value of Object.values(material)) if (value?.isTexture) { value.image?.close?.(); value.dispose(); }
      material.dispose();
    }
  });
  renderer.renderLists.dispose();
  return result;
};
window.rendererReady = true;
