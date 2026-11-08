// Photoreal car renderer: Khronos "Car Concept" (CC-BY 4.0, Eric Chadwick / DGG) with studio lighting.
// window.pose({ang, dist, h, ty, fov, paint, env, bg, doors, lights, brake, ground})
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const W = +(new URLSearchParams(location.search).get('w') || 1600);
const H = +(new URLSearchParams(location.search).get('h') || 1000);
const canvas = document.getElementById('gl');
canvas.width = W; canvas.height = H;
document.body.style.width = W + 'px'; document.body.style.height = H + 'px';
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false);
renderer.toneMapping = THREE.AgXToneMapping; renderer.toneMappingExposure = 1.0;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(28, W / H, 0.05, 200);
const pmrem = new THREE.PMREMGenerator(renderer);
function studioScene() {
  // dark photo studio with big softboxes -> long clean reflections on the paint
  const sc = new THREE.Scene();
  const room = new THREE.Mesh(new THREE.BoxGeometry(40, 16, 40), new THREE.MeshBasicMaterial({ color: 0x0c0d10, side: THREE.BackSide }));
  room.position.y = 7; sc.add(room);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(40, 40), new THREE.MeshBasicMaterial({ color: 0x1b1c1f }));
  floor.rotation.x = -Math.PI / 2; floor.position.y = -0.9; sc.add(floor);
  const box = (w, h, x, y, z, rx, ry, I, col = 0xffffff) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: new THREE.Color(col).multiplyScalar(I), side: THREE.DoubleSide }));
    m.position.set(x, y, z); m.rotation.set(rx, ry, 0); sc.add(m);
  };
  box(14, 5, 0, 12, 0, Math.PI / 2, 0, 5);                // overhead softbox
  box(16, 1.2, 0, 4.5, 11, 0, 0, 7);                      // long strip front side (streak along body)
  box(16, 1.2, 0, 4.5, -11, 0, 0, 7);                     // strip other side
  box(1.6, 8, 14, 3.5, 0, 0, -Math.PI / 2, 4);            // front kicker
  box(1.6, 8, -14, 3.5, 0, 0, Math.PI / 2, 6, 0xdfe8ff);  // rear rim (cool)
  box(30, 2.5, 0, 0.6, 15, 0, 0, 0.9);                    // low horizon glow
  return sc;
}
const ENVS = { studio: pmrem.fromScene(studioScene(), 0.0).texture, room: pmrem.fromScene(new RoomEnvironment(), 0.02).texture };
async function hdr(name) {
  if (ENVS[name]) return ENVS[name];
  const t = await new RGBELoader().loadAsync('./env/' + name + '_1k.hdr');
  t.mapping = THREE.EquirectangularReflectionMapping;
  ENVS[name] = pmrem.fromEquirectangular(t).texture; return ENVS[name];
}

// soft key light for the contact shadow + highlights
const key = new THREE.DirectionalLight(0xffffff, 2.2); key.position.set(2, 8, 3);
key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.radius = 3;
Object.assign(key.shadow.camera, { left: -4, right: 4, top: 4, bottom: -4, near: 0.5, far: 20 }); key.shadow.bias = -0.0005;
scene.add(key);
const rim = new THREE.DirectionalLight(0xdfe8ff, 1.2); rim.position.set(-5, 3, -4); scene.add(rim);

// shadow catcher (transparent PNG keeps only the shadow)
const ground = new THREE.Mesh(new THREE.PlaneGeometry(30, 30), new THREE.ShadowMaterial({ opacity: 0.55 }));
ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; scene.add(ground);
// soft ambient-occlusion blob under the car
const aoC = document.createElement('canvas'); aoC.width = aoC.height = 256;
{ const g = aoC.getContext('2d'); const gr = g.createRadialGradient(128, 128, 10, 128, 128, 128);
  gr.addColorStop(0, 'rgba(0,0,0,0.85)'); gr.addColorStop(0.55, 'rgba(0,0,0,0.45)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 256, 256); }
const ao = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(aoC), transparent: true, depthWrite: false }));
ao.rotation.x = -Math.PI / 2; ao.position.y = 0.002; scene.add(ao);

const PAINTS = {
  red: 0x9a0a0e, white: 0xe8eaec, black: 0x0b0c0e, silver: 0x9aa0a6, blue: 0x0d3fa8, lime: 0x8fd11c,
  orange: 0xd9520f, gray: 0x3a3f46, teal: 0x0f6f73,
};
let car, paintMats = [], lightMats = {}, info = { meshes: [], materials: [] }, size = new THREE.Vector3(), parts = {};
new GLTFLoader().load('./models/CarConcept.glb', g => {
  car = g.scene;
  const mats = new Set();
  car.traverse(o => {
    parts[o.name] = o;
    if (!o.isMesh) return;
    o.castShadow = true; o.receiveShadow = true;
    info.meshes.push(o.name + ' :: ' + o.material.name);
    mats.add(o.material);
  });
  for (const m of mats) {
    info.materials.push(m.name + (m.map ? ' [map:' + (m.map.name || m.map.image?.src?.slice(-30) || '?') + ']' : ''));
    if (/^Paint/.test(m.name)) paintMats.push(m);
    if (/light/i.test(m.name)) lightMats[m.name] = m;
    m.envMapIntensity = 1.0;
  }
  // tire sidewall texture carries logos -> plain rubber; calm the paint flake noise
  for (const m of mats) {
    if (m.name === 'Tireside') { m.map = null; m.color.set(0x161616); m.roughness = 0.85; m.needsUpdate = true; }
    if (/^Paint/.test(m.name) && m.normalMap) { m.normalScale.set(0.12, 0.12); m.normalMap.magFilter = THREE.LinearFilter; m.normalMap.needsUpdate = true; }
  }
  // straighten steered front wheels
  window.WHEEL_ROT = ['WheelFrontL','WheelFrontR','WheelRearL','WheelRearR'].map(n => parts[n] ? n + ':' + parts[n].rotation.toArray().slice(0,3).map(v=>v.toFixed(2)).join(',') : n + ':none');
  if (parts.WheelFrontL && parts.WheelRearL) parts.WheelFrontL.rotation.set(parts.WheelRearL.rotation.x, 0, 0);
  if (parts.WheelFrontR && parts.WheelRearR) parts.WheelFrontR.rotation.set(parts.WheelRearR.rotation.x, 0, 0);
  // hide logos / plates (non-brand rule)
  car.traverse(o => { if (o.isMesh && /License|Khronos|Logo|Badge|Plate/i.test(o.name + ' ' + o.material.name)) o.visible = false; });
  // normalise: wheels on y=0, centred
  const box = new THREE.Box3().setFromObject(car); box.getSize(size);
  const c = box.getCenter(new THREE.Vector3());
  const wb = new THREE.Box3(); for (const n of ['WheelFrontL','WheelFrontR','WheelRearL','WheelRearR']) if (parts[n]) wb.expandByObject(parts[n], true);
  window.WHEEL_MIN = wb.min.y; window.BOX_MIN = box.min.y;
  car.position.set(-c.x, -(wb.isEmpty() ? box.min.y : wb.min.y), -c.z);
  const wrap = new THREE.Group(); wrap.add(car); scene.add(wrap); car = wrap;
  // long axis -> x
  window.LONG_AXIS = size.x >= size.z ? 'x' : 'z';
  if (window.LONG_AXIS === 'z') car.rotation.y = Math.PI / 2;
  const L = Math.max(size.x, size.z), Wd = Math.min(size.x, size.z);
  ao.scale.set(L * 1.25, Wd * 1.6, 1);
  car.updateMatrixWorld(true);
  for (const n of ['WheelFrontL','WheelFrontR','WheelRearL','WheelRearR']) { if (!parts[n]) continue;
    const b = new THREE.Box3().setFromObject(parts[n], true); const cc = b.getCenter(new THREE.Vector3()); const sz = b.getSize(new THREE.Vector3());
    const blob = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), ao.material.clone()); blob.material.opacity = 0.95;
    blob.rotation.x = -Math.PI / 2; blob.position.set(cc.x, 0.003, cc.z); blob.scale.set(Math.max(sz.x, 0.35) * 1.5, sz.z * 0.9, 1);
    scene.add(blob); window.BLOBS = (window.BLOBS || []).concat(blob); }
  window.CAR_INFO = { cn: window.CN_DBG, wheelRot: window.WHEEL_ROT, wheelMin: window.WHEEL_MIN, boxMin: window.BOX_MIN, ...info, size: size.toArray(), nodes: Object.keys(parts) };
  window.READY = true;
}, undefined, e => { window.LOAD_ERR = String(e); });

// x-ray: ghost body + glowing battery pack in the floor
let pack = null, xrayMats = null;
function buildPack(hot) {
  if (pack) scene.remove(pack);
  pack = new THREE.Group();
  const nx = 18, nz = 9, L = 2.5, Wd = 1.45, cw = L / nx, cd = Wd / nz;
  const cellG = new THREE.CylinderGeometry(cw * 0.36, cw * 0.36, 0.09, 14);
  const cellM = new THREE.MeshStandardMaterial({ color: hot ? 0xff6a1a : 0x9fe830, emissive: hot ? 0xff4a00 : 0x7cd61a, emissiveIntensity: 1.6, metalness: 0.3, roughness: 0.35 });
  const inst = new THREE.InstancedMesh(cellG, cellM, nx * nz * 2); let k = 0; const m4 = new THREE.Matrix4();
  for (let i = 0; i < nx; i++) for (let j = 0; j < nz; j++) for (let r = 0; r < 2; r++) {
    m4.makeTranslation(-L / 2 + cw * (i + 0.5) + (r ? cw / 2 : 0) - 0.15, 0.22, -Wd / 2 + cd * (j + 0.5) + (r ? cd / 2 : 0) * 0); if (r) continue;
    inst.setMatrixAt(k++, m4); }
  inst.count = k; pack.add(inst);
  const tray = new THREE.Mesh(new THREE.BoxGeometry(L + 0.1, 0.05, Wd + 0.1), new THREE.MeshStandardMaterial({ color: 0x2a2f36, metalness: 0.8, roughness: 0.4 }));
  tray.position.set(-0.15, 0.16, 0); pack.add(tray);
  scene.add(pack);
}
function setXray(on, hot) {
  if (!xrayMats) { xrayMats = []; car.traverse(o => { if (o.isMesh && !/^Wheel|mesh_(89|9[0-6])/.test(o.name) && !/Tire|Rim|Disc|Brake$/.test(o.material.name)) xrayMats.push(o); }); }
  for (const o of xrayMats) {
    if (on) { if (!o.userData.m0) o.userData.m0 = o.material;
      o.material = new THREE.MeshPhysicalMaterial({ color: 0xbfd8ff, transparent: true, opacity: /Paint|Glass/.test(o.userData.m0.name) ? 0.14 : 0.05, roughness: 0.2, metalness: 0, depthWrite: false, emissive: 0x2a4a7a, emissiveIntensity: 0.25 });
      o.castShadow = false; }
    else if (o.userData.m0) { o.material = o.userData.m0; o.castShadow = true; }
  }
  if (on) buildPack(hot); else if (pack) { scene.remove(pack); pack = null; }
}
// ---- "Chinese premium EV" design cues (generic, not any real model): light bars, roof lidar, two-tone ----
let cn = null;
function wbox(name) { const o = parts[name]; return o ? new THREE.Box3().setFromObject(o, true) : null; }
function buildCN() {
  cn = new THREE.Group(); car.updateMatrixWorld(true);
  const hl = wbox('BodyHeadlights'), tl = wbox('BodyTaillights'), ws = wbox('BodyWindshield'), roof = wbox('BodyRoofPanel');
  const barMat = c => new THREE.MeshStandardMaterial({ color: 0x111111, emissive: c, emissiveIntensity: 6, roughness: 0.3 });
  const front = hl.getCenter(new THREE.Vector3()).x > 0 ? 1 : -1;
  const meshes = []; car.traverse(o => { if (o.isMesh && o.visible && !/Glass/.test(o.material.name)) meshes.push(o); });
  const rc = new THREE.Raycaster();
  const hit = (from, dir) => { rc.set(from, dir); const h = rc.intersectObjects(meshes, false)[0]; return h ? h.point : null; };
  // light bar: trace the body surface across the width, then a glowing tube 4 mm proud of it
  const bar = (dirX, y, zMax, col, name) => {
    const pts = [];
    for (let i = 0; i <= 40; i++) { const z = -zMax + 2 * zMax * i / 40;
      const p = hit(new THREE.Vector3(dirX * 6, y, z), new THREE.Vector3(-dirX, 0, 0)); if (p) pts.push(p.add(new THREE.Vector3(dirX * 0.006, 0, 0))); }
    if (pts.length < 4) return;
    const tube = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 120, name === 'frontBar' ? 0.013 : 0.011, 8, false),
      new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: col, emissiveIntensity: 9, roughness: 0.2 }));
    tube.name = name; cn.add(tube);
  };
  const hc = hl.getCenter(new THREE.Vector3()), tc = tl.getCenter(new THREE.Vector3());
  bar(front, hc.y + 0.012, (hl.max.z - hl.min.z) / 2 * 0.98, 0xeaf4ff, 'frontBar');
  bar(-front, tc.y, (tl.max.z - tl.min.z) / 2 * 1.0, 0xff1a1a, 'rearBar');
  // lidar pod centred on the roof's leading edge
  const lx = roof.max.x - 0.06 * front;
  const ry = hit(new THREE.Vector3(lx, 5, 0), new THREE.Vector3(0, -1, 0))?.y ?? roof.max.y;
  const podMat = new THREE.MeshPhysicalMaterial({ color: 0x07080a, metalness: 0.3, roughness: 0.12, clearcoat: 1 });
  const g = new THREE.Group(); g.name = 'lidar';
  const base = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.15, 0.035, 32), podMat); base.scale.set(1.25, 1, 1);
  const dome = new THREE.Mesh(new THREE.SphereGeometry(0.11, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), podMat); dome.scale.set(1.35, 0.55, 1.1); dome.position.y = 0.015;
  const win = new THREE.Mesh(new THREE.BoxGeometry(0.01, 0.025, 0.13), new THREE.MeshPhysicalMaterial({ color: 0x1a1d24, metalness: 0.9, roughness: 0.05, clearcoat: 1 }));
  win.position.set(front * 0.145, 0.03, 0);
  g.add(base, dome, win); g.position.set(lx, ry + 0.012, 0); cn.add(g);
  window.CN_DBG = { ry, lx };
  scene.add(cn);
}
window.pose = async (o = {}) => {
  const STY = o.style ?? 'cn'; if (STY === 'cn' && !cn) buildCN();
  if (cn) cn.visible = STY === 'cn';
  setXray(!!o.xray, o.packColor === 'hot');
  const env = await hdr(o.env || 'studio');
  scene.environment = env; scene.environmentIntensity = o.envI ?? 1.0;
  scene.background = o.bg ? (o.bg === 'env' ? env : new THREE.Color(o.bg)) : null;
  scene.backgroundBlurriness = 0.4;
  ground.visible = ao.visible = o.ground !== false; (window.BLOBS||[]).forEach(b => b.visible = o.ground !== false);
  key.intensity = o.key ?? 2.2;
  renderer.toneMappingExposure = o.exp ?? 1.0;
  const col = new THREE.Color(PAINTS[o.paint] ?? o.paint ?? PAINTS.red);
  for (const m of paintMats) { if (m.name.includes('Paint 1') || m.name.includes('Paint 2')) {
    m.color.copy(STY === 'cn' && m.name.includes('Paint 2') ? new THREE.Color(o.roof ?? 0x08090b) : col); if (m.map) m.map = m.map; m.metalness = o.metal ?? 0.65; m.roughness = o.rough ?? 0.32;
    if ('clearcoat' in m) { m.clearcoat = 1; m.clearcoatRoughness = 0.03; }
    if ('iridescence' in m) m.iridescence = 0; m.needsUpdate = true; } }
  for (const [n, m] of Object.entries(lightMats)) {
    const on = /brake/i.test(n) ? !!o.brake : (o.lights !== false);
    if (!m.userData.e0) m.userData.e0 = m.emissive.clone();
    m.emissiveIntensity = on ? (/brake/i.test(n) ? 40 : 3) : 0.2; if (/brake/i.test(n) && on) { m.color.set(0xff2020); }
    if (/brake/i.test(n) && o.brake) m.emissive.set(0xff1010);
  }
  const ang = o.ang ?? 0.6, dist = o.dist ?? 7.5, h = o.h ?? 1.2, ty = o.ty ?? 0.62;
  camera.fov = o.fov ?? 28; camera.aspect = W / H; camera.updateProjectionMatrix();
  camera.position.set(Math.cos(ang) * dist, h, Math.sin(ang) * dist);
  camera.lookAt(o.tx ?? 0, ty, o.tz ?? 0);
  renderer.render(scene, camera);
  renderer.getContext().finish();
  return true;
};
window.renderNow = () => { renderer.render(scene, camera); renderer.getContext().finish(); };
