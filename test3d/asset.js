import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
const W = 1600, H = 1000;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const easeIO = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const lerp = (a, b, k) => a + (b - a) * k;
const V = (x, y, z) => new THREE.Vector3(x, y, z);
// ---------- renderer ----------
const canvas = document.getElementById('gl');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.85;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x06080c);
scene.fog = new THREE.Fog(0x06080c, 18, 60);
const pmrem = new THREE.PMREMGenerator(renderer);
const envTex = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environment = envTex;
scene.environmentIntensity = 0.28;

const camera = new THREE.PerspectiveCamera(34, W / H, 0.1, 200);

// ---------- lights ----------
scene.add(new THREE.HemisphereLight(0x8fa6c8, 0x0a0c10, 0.18));
const key = new THREE.SpotLight(0xffffff, 55, 40, 0.5, 0.7, 1.6);
key.position.set(3, 9, 4); key.target.position.set(0, 0, 0);
key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.radius = 6; key.shadow.bias = -0.0004;
scene.add(key, key.target);
const sun = new THREE.DirectionalLight(0xffffff, 1.05); sun.position.set(5, 9, 7); sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048); sun.shadow.camera.left = -6; sun.shadow.camera.right = 6; sun.shadow.camera.top = 6; sun.shadow.camera.bottom = -6; sun.shadow.radius = 5;
scene.add(sun);
const fill = new THREE.DirectionalLight(0xbcd4ff, 0.55); fill.position.set(-6, 3, 8); scene.add(fill);
const front = new THREE.DirectionalLight(0xffffff, 0.5); front.position.set(9, 2, 1); scene.add(front);
const rimL = new THREE.SpotLight(0x6fb8ff, 45, 30, 0.6, 0.8, 1.4); rimL.position.set(-6, 3, -5); scene.add(rimL, rimL.target);
const rimR = new THREE.SpotLight(0xc6ff3d, 22, 30, 0.6, 0.8, 1.4); rimR.position.set(6, 2.5, -4); scene.add(rimR, rimR.target);

// ---------- ground / road ----------
const groundMat = new THREE.MeshStandardMaterial({ color: 0x0c0f15, roughness: 0.32, metalness: 0.35 });
const ground = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), groundMat);
ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; scene.add(ground);
const roadMat = new THREE.MeshStandardMaterial({ color: 0x14181f, roughness: 0.45, metalness: 0.2 });
const road = new THREE.Mesh(new THREE.PlaneGeometry(200, 7.4), roadMat);
road.rotation.x = -Math.PI / 2; road.position.y = 0.002; road.receiveShadow = true; scene.add(road);
const dashMat = new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xffffff, emissiveIntensity: 0.12, roughness: 0.6 });
const edgeMat = new THREE.MeshStandardMaterial({ color: 0xc6ff3d, emissive: 0xc6ff3d, emissiveIntensity: 0.9 });
const dashes = [];
for (let i = 0; i < 26; i++) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(2.2, 0.14), dashMat);
  m.rotation.x = -Math.PI / 2; m.position.set(0, 0.004, -1.85); scene.add(m); dashes.push(m);
  const m2 = m.clone(); m2.position.z = 1.85; scene.add(m2); dashes.push(m2);
}
for (const z of [-3.7, 3.7]) {
  const e = new THREE.Mesh(new THREE.PlaneGeometry(200, 0.06), edgeMat);
  e.rotation.x = -Math.PI / 2; e.position.set(0, 0.005, z); scene.add(e);
}
// roadside light posts (give a sense of speed)
const postMat = new THREE.MeshStandardMaterial({ color: 0x1a1f28, roughness: 0.5, metalness: 0.6 });
const lampMat = new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xbfe6ff, emissiveIntensity: 2 });
const posts = [];
for (let i = 0; i < 14; i++) {
  const g = new THREE.Group();
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.06, 4.2, 10), postMat); pole.position.y = 2.1; g.add(pole);
  const lamp = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.08, 0.18), lampMat); lamp.position.set(0, 4.2, 0.3); g.add(lamp);
  g.position.set(0, 0, -6.0); scene.add(g); posts.push(g);
}

// ---------- the car ----------
const car = new THREE.Group(); scene.add(car);
const paint = new THREE.MeshPhysicalMaterial({ color: 0xaeb6c0, metalness: 0.5, roughness: 0.28, clearcoat: 1, clearcoatRoughness: 0.04, transparent: true, opacity: 1 });
const glassMat = new THREE.MeshPhysicalMaterial({ color: 0x05070a, metalness: 0.9, roughness: 0.06, clearcoat: 1, transparent: true, opacity: 1 });
const blackMat = new THREE.MeshStandardMaterial({ color: 0x0b0d10, roughness: 0.55, metalness: 0.3, transparent: true, opacity: 1 });

function profileShape(pts) {
  const s = new THREE.Shape(); s.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length; i++) {
    const p = pts[i];
    if (p.length === 4) s.quadraticCurveTo(p[2], p[3], p[0], p[1]); else s.lineTo(p[0], p[1]);
  }
  s.closePath(); return s;
}
// side profile (x forward, y up) — [x, y] or [x, y, cx, cy] for curves
const bodyPts = [[-2.3, 0.34], [-2.38, 0.62, -2.42, 0.45], [-2.18, 0.98, -2.34, 0.92], [-1.35, 1.34, -1.85, 1.22], [0.25, 1.43, -0.6, 1.47],
                 [1.05, 1.0, 0.75, 1.3], [2.05, 0.84, 1.55, 0.92], [2.4, 0.56, 2.42, 0.78], [2.28, 0.3, 2.42, 0.36]];
const bodyGeo = new THREE.ExtrudeGeometry(profileShape(bodyPts), { depth: 1.72, bevelEnabled: true, bevelThickness: 0.16, bevelSize: 0.12, bevelSegments: 8, curveSegments: 28 });
bodyGeo.translate(0, 0, -0.86);
const body = new THREE.Mesh(bodyGeo, paint); body.castShadow = true; body.receiveShadow = true; car.add(body);
const glassPts = [[-1.95, 1.0], [-1.3, 1.31, -1.7, 1.2], [0.2, 1.4, -0.55, 1.44], [0.98, 1.03, 0.7, 1.27], [-1.95, 1.0]];
const glassGeo = new THREE.ExtrudeGeometry(profileShape(glassPts), { depth: 1.86, bevelEnabled: true, bevelThickness: 0.05, bevelSize: 0.05, bevelSegments: 4, curveSegments: 24 });
glassGeo.translate(0, 0.012, -0.93);
const glass = new THREE.Mesh(glassGeo, glassMat); car.add(glass);
// lower skirt
const skirt = new THREE.Mesh(new THREE.BoxGeometry(4.5, 0.16, 2.02), blackMat); skirt.position.set(0.02, 0.32, 0); car.add(skirt);
// light bars
const headMat = new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xe8f4ff, emissiveIntensity: 3 });
const head = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.05, 1.7), headMat); head.position.set(2.42, 0.66, 0); car.add(head);
const tailMat = new THREE.MeshStandardMaterial({ color: 0x400000, emissive: 0xff0808, emissiveIntensity: 1.2 });
const tail = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.07, 1.86), tailMat); tail.position.set(-2.45, 0.86, 0); car.add(tail);
const tailGlow = new THREE.PointLight(0xff2020, 0, 6, 2); tailGlow.position.set(-2.9, 0.6, 0); car.add(tailGlow);
const under = new THREE.Mesh(new THREE.PlaneGeometry(3.6, 1.5), new THREE.MeshBasicMaterial({ color: 0xc6ff3d, transparent: true, opacity: 0.09 }));
under.rotation.x = -Math.PI / 2; under.position.y = 0.01; car.add(under);

// wheels
const tireMat = new THREE.MeshStandardMaterial({ color: 0x0a0a0b, roughness: 0.85 });
const rimMat = new THREE.MeshStandardMaterial({ color: 0x9aa3ad, metalness: 1, roughness: 0.25 });
const caliperMat = new THREE.MeshStandardMaterial({ color: 0x8a1c14, emissive: 0xff4a1a, emissiveIntensity: 0, roughness: 0.4 });
const wheels = [];
for (const [x, z] of [[1.5, 0.98], [1.5, -0.98], [-1.45, 0.98], [-1.45, -0.98]]) {
  const w = new THREE.Group(); w.position.set(x, 0.37, z);
  const spin = new THREE.Group(); w.add(spin);
  const tire = new THREE.Mesh(new THREE.TorusGeometry(0.29, 0.085, 18, 48), tireMat); spin.add(tire);
  const tread = new THREE.Mesh(new THREE.CylinderGeometry(0.37, 0.37, 0.24, 48, 1, true), tireMat); tread.rotation.x = Math.PI / 2; spin.add(tread);
  const disc = new THREE.Mesh(new THREE.CylinderGeometry(0.27, 0.27, 0.05, 40), rimMat); disc.rotation.x = Math.PI / 2; disc.position.z = Math.sign(z) * 0.08; spin.add(disc);
  for (let k = 0; k < 5; k++) {
    const sp = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.24, 0.03), rimMat);
    sp.position.set(Math.cos(k * 1.2566) * 0.13, Math.sin(k * 1.2566) * 0.13, Math.sign(z) * 0.115); sp.rotation.z = k * 1.2566 + Math.PI / 2; spin.add(sp);
  }
  const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.06, 20), new THREE.MeshStandardMaterial({ color: 0xc6ff3d, emissive: 0xc6ff3d, emissiveIntensity: 1.2 }));
  hub.rotation.x = Math.PI / 2; hub.position.z = Math.sign(z) * 0.13; spin.add(hub);
  const cal = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.22, 0.08), caliperMat); cal.position.set(0.17, 0.12, Math.sign(z) * 0.05); w.add(cal);
  w.traverse(o => { if (o.isMesh) o.castShadow = true; });
  car.add(w); wheels.push({ g: w, spin, x, z });
}

// ---------- x-ray internals ----------
const inner = new THREE.Group(); car.add(inner);
const packMat = new THREE.MeshStandardMaterial({ color: 0x141a12, emissive: 0xc6ff3d, emissiveIntensity: 0.1, roughness: 0.4, transparent: true, opacity: 0 });
const pack = new THREE.Mesh(new THREE.BoxGeometry(2.9, 0.13, 1.55), packMat); pack.position.set(0.05, 0.42, 0); inner.add(pack);
const cellMat = new THREE.MeshStandardMaterial({ color: 0x0e1408, emissive: 0xc6ff3d, emissiveIntensity: 0, transparent: true, opacity: 0 });
const cells = new THREE.InstancedMesh(new THREE.BoxGeometry(0.17, 0.05, 0.22), cellMat, 12 * 5);
{ const m = new THREE.Matrix4(); let i = 0;
  for (let a = 0; a < 12; a++) for (let b = 0; b < 5; b++) { m.makeTranslation(-1.3 + a * 0.24, 0.5, -0.6 + b * 0.3); cells.setMatrixAt(i++, m); } }
inner.add(cells);
const motorMat = new THREE.MeshStandardMaterial({ color: 0x3a2a10, emissive: 0xff8a3d, emissiveIntensity: 0, metalness: 0.6, roughness: 0.3, transparent: true, opacity: 0 });
const motor = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.55, 32), motorMat); motor.rotation.x = Math.PI / 2; motor.position.set(-1.45, 0.42, 0); inner.add(motor);
const axleMat = new THREE.MeshStandardMaterial({ color: 0x777f8a, metalness: 1, roughness: 0.3, transparent: true, opacity: 0 });
const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 1.9, 12), axleMat); axle.rotation.x = Math.PI / 2; axle.position.set(-1.45, 0.37, 0); inner.add(axle);
// energy particles: wheel -> motor -> pack
const NP = 70;
const partMat = new THREE.MeshBasicMaterial({ color: 0xd8ff6a, transparent: true, opacity: 0 });
const parts = new THREE.InstancedMesh(new THREE.SphereGeometry(0.035, 10, 8), partMat, NP); inner.add(parts);
const flowPath = new THREE.CatmullRomCurve3([V(-1.45, 0.37, 0.98), V(-1.45, 0.42, 0.35), V(-1.45, 0.45, 0), V(-1.1, 0.5, 0), V(-0.3, 0.52, 0.15), V(0.6, 0.52, -0.1), V(1.3, 0.5, 0.2)]);



// ---------- asset poses (transparent background, soft contact shadow) ----------
dashes.forEach(m => m.visible = false); posts.forEach(g => g.visible = false);
scene.background = null; scene.fog = null; renderer.setClearColor(0x000000, 0);
ground.visible = false; road.visible = false;
scene.traverse(o => { if (o.isMesh && o.material === edgeMat) o.visible = false; });
const shadowPlane = new THREE.Mesh(new THREE.PlaneGeometry(14, 14), new THREE.ShadowMaterial({ opacity: 0.55 }));
shadowPlane.rotation.x = -Math.PI / 2; shadowPlane.position.y = 0.003; shadowPlane.receiveShadow = true; scene.add(shadowPlane);
under.visible = false;
camera.aspect = W / H; camera.updateProjectionMatrix();
const PAINTS = { silver: 0xaeb6c0, white: 0xe9edf2, red: 0xc8202a, blue: 0x2a5bd7, black: 0x22262c };
window.pose = function (o) {
  const ang = o.ang ?? 0.6, R = o.dist ?? 8.2, h = o.h ?? 1.5;
  camera.position.set(Math.cos(ang) * R, h, Math.sin(ang) * R);
  camera.lookAt(o.lx ?? 0, o.ly ?? 0.7, 0); camera.fov = o.fov ?? 28; camera.updateProjectionMatrix();
  paint.color.set(PAINTS[o.paint || 'silver']);
  const xr = o.xray || 0;
  paint.opacity = 1 - 0.7 * xr; glassMat.opacity = 1 - 0.75 * xr; blackMat.opacity = 1 - 0.6 * xr;
  paint.depthWrite = xr < 0.05; glassMat.depthWrite = xr < 0.05;
  packMat.opacity = 0.9 * xr; cellMat.opacity = xr; motorMat.opacity = xr * 0.8; axleMat.opacity = xr * 0.6;
  const hot = o.packColor === 'hot';
  packMat.emissive.set(hot ? 0xff5a2a : 0xc6ff3d); cellMat.emissive.set(hot ? 0xff6a3d : 0xc6ff3d);
  packMat.emissiveIntensity = 0.15 * xr; cellMat.emissiveIntensity = 0.9 * xr; motorMat.emissiveIntensity = 0.8 * xr;
  partMat.opacity = 0;
  tailMat.emissiveIntensity = o.brake ? 4 : 1; headMat.emissiveIntensity = o.head ?? 3;
  caliperMat.emissiveIntensity = o.caliper ? 1.8 : 0;
  renderer.render(scene, camera);
  const gl = renderer.getContext(); gl.finish();
};
window.renderAt = () => {};
renderer.compile(scene, camera);
window.READY = true;
