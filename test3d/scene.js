// EV DRIVE — 3D motion-graphics test: "One-pedal driving". Deterministic: window.renderAt(t).
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';

const W = 1080, H = 1920;
const TIM = await (await fetch('./timing.json')).json();
const SC = Object.fromEntries(TIM.scenes.map(s => [s.id, s]));

// ---------- helpers ----------
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const easeIO = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const easeO = x => { x = clamp(x); return 1 - Math.pow(1 - x, 3); };
const backO = x => { x = clamp(x); const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
const lerp = (a, b, k) => a + (b - a) * k;
const V = (x, y, z) => new THREE.Vector3(x, y, z);

// ---------- renderer ----------
const canvas = document.getElementById('gl');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
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

// ---------- motion over time ----------
const T = TIM.total;
const tL = SC.lift.start, tR = SC.regen.start, tS = SC.stop.start, tB = SC.light.start, tE = SC.end.start;
function speedAt(t) {               // m/s
  if (t < tR + 0.4) return 15;
  if (t < tS + 0.6) return lerp(15, 3.2, easeIO((t - tR - 0.4) / (tS + 0.6 - tR - 0.4)));
  if (t < tS + 2.6) return lerp(3.2, 0, easeO((t - tS - 0.6) / 2.0));
  return 0;
}
const DT = 1 / 120, distTab = [0];
for (let t = DT; t <= T + 1; t += DT) distTab.push(distTab[distTab.length - 1] + speedAt(t) * DT);
const distAt = t => distTab[Math.min(distTab.length - 1, Math.max(0, Math.round(t / DT)))];
const regenAmt = t => (t > tL + 1.2 && speedAt(t) > 0.5) ? clamp((t - tL - 1.2) / 0.6) * (t < tS + 2.6 ? 1 : 0) : 0;
const xray = t => clamp(Math.min((t - (tL + 0.8)) / 0.9, 1 - (t - (tS + 1.6)) / 0.9));
const brakeLights = t => (t > tL + 1.4 && t < tE + 0.6) ? 1 : 0;
const caliperOn = t => (t > tS + 0.8 && t < tB + 0.5) ? clamp((t - tS - 0.8) / 0.4) : 0;

// camera keyframes: [time, pos, target, fov]
const K = [
  [0.0, V(9.0, 1.3, 8.8), V(0.3, 0.8, 0), 30],
  [tL - 0.4, V(5.4, 1.1, 10.6), V(0, 0.8, 0), 30],
  [tL + 0.6, V(0.5, 1.5, 12.5), V(0, 0.75, 0), 30],
  [tR, V(-0.8, 1.8, 12.0), V(-0.3, 0.65, 0), 30],
  [tR + 1.6, V(-4.0, 6.2, 8.4), V(-0.2, 0.45, 0), 32],
  [tS - 0.3, V(-2.4, 5.8, 8.0), V(-0.2, 0.45, 0), 32],
  [tS + 0.9, V(-4.4, 0.9, 4.6), V(-1.45, 0.5, 0.9), 30],
  [tB - 0.3, V(-4.0, 0.95, 4.2), V(-1.45, 0.5, 0.9), 30],
  [tB + 0.8, V(-11.5, 1.5, 2.6), V(-1.2, 0.8, 0), 28],
  [tE - 0.2, V(-11.0, 1.7, 3.4), V(-1.0, 0.8, 0), 28],
  [tE + 1.2, V(7.5, 6.0, 11.5), V(0, 0.6, 0), 32],
  [T + 1, V(10.0, 7.0, 9.5), V(0, 0.6, 0), 32],
];
function camAt(t) {
  let i = 0; while (i < K.length - 2 && t > K[i + 1][0]) i++;
  const a = K[i], b = K[i + 1];
  const u = easeIO((t - a[0]) / Math.max(1e-6, b[0] - a[0]));
  const pos = a[1].clone().lerp(b[1], u), tgt = a[2].clone().lerp(b[2], u);
  // gentle handheld drift
  pos.x += Math.sin(t * 0.7) * 0.05; pos.y += Math.sin(t * 0.9 + 1) * 0.03;
  return [pos, tgt, lerp(a[3], b[3], u)];
}

// ---------- post ----------
const composer = new EffectComposer(renderer);
composer.setPixelRatio(1); composer.setSize(W, H);
composer.addPass(new RenderPass(scene, camera));
composer.addPass(new ShaderPass({
  uniforms: { tDiffuse: { value: null } },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
  fragmentShader: 'uniform sampler2D tDiffuse; varying vec2 vUv; void main(){ vec4 c = texture2D(tDiffuse, vUv); if (!(c.r == c.r) || !(c.g == c.g) || !(c.b == c.b) || !(c.a == c.a)) c = vec4(0.0, 0.0, 0.0, 1.0); gl_FragColor = clamp(c, 0.0, 40.0); }',
}));
const bloom = new UnrealBloomPass(new THREE.Vector2(W / 2, H / 2), 0.45, 0.5, 0.93);
composer.addPass(bloom);
composer.addPass(new OutputPass());

// ---------- 2D overlay ----------
const layer = document.getElementById('layer'), lines = document.getElementById('lines');
const bar = document.getElementById('bar'), cap = document.getElementById('cap');
function el(html, css) { const d = document.createElement('div'); d.className = 'abs'; d.innerHTML = html; Object.assign(d.style, css); layer.appendChild(d); return d; }
const E = {
  h1: el('<div class="head">ONE PEDAL.</div>', { top: '300px' }),
  h1b: el('<div class="head acc">NO BRAKE?</div>', { top: '405px' }),
  pedals: el(`<svg width="420" height="250" viewBox="0 0 420 250">
     <rect x="20" y="40" width="150" height="190" rx="26" fill="rgba(20,24,32,.75)" stroke="#8a96a8" stroke-width="5"/>
     <text x="95" y="150" text-anchor="middle" font-family="Inter Display" font-weight="900" font-size="34" fill="#8a96a8">BRAKE</text>
     <line id="strike" x1="10" y1="230" x2="180" y2="40" stroke="#ff4d4d" stroke-width="14" stroke-linecap="round"/>
     <rect x="250" y="10" width="150" height="230" rx="26" fill="rgba(198,255,61,.16)" stroke="#C6FF3D" stroke-width="5"/>
     <text x="325" y="138" text-anchor="middle" font-family="Inter Display" font-weight="900" font-size="34" fill="#C6FF3D">GO</text></svg>`, { left: '330px', top: '560px' }),
  gen: el('<div class="head">MOTOR <span class="acc">→</span><br><span class="acc">GENERATOR</span></div>', { top: '300px' }),
  frac: el('<div class="head" style="font-size:84px">≈ <span class="acc">1/5</span> OF FULL<br>BRAKING FORCE</div>', { top: '290px' }),
  spd: el('<div class="chip"><small>SPEED</small><span id="spdv">54 km/h</span></div>', { left: '90px', top: '560px' }),
  bat: el('<div class="chip acc"><small>BATTERY</small><span id="batv">71%</span></div>', { left: '690px', top: '560px' }),
  stop: el('<div class="head" style="font-size:80px">FRICTION BRAKES<br><span class="acc">FINISH THE STOP</span></div>', { top: '290px' }),
  hold: el('<div class="call">HOLD ✓</div>', { left: '470px', top: '520px' }),
  light: el('<div class="head">BRAKE LIGHTS:<br><span class="red">ON</span></div>', { top: '290px' }),
  end1: el('<div class="head">WOULD YOU DRIVE<br>WITH <span class="acc">ONE PEDAL?</span></div>', { top: '300px' }),
  end2: el('<div class="call" style="font-size:40px;padding:18px 40px">FOLLOW EV DRIVE</div>', { left: '340px', top: '560px' }),
  cMotor: el('<div class="call" style="background:#FF7A3D">MOTOR</div>', {}),
  cPack: el('<div class="call">BATTERY</div>', {}),
  cCal: el('<div class="call red">FRICTION BRAKE</div>', {}),
};
const lineEls = {};
for (const k of ['cMotor', 'cPack', 'cCal']) { const l = document.createElementNS('http://www.w3.org/2000/svg', 'line'); l.setAttribute('stroke', k === 'cCal' ? '#ff5a4d' : k === 'cMotor' ? '#FF7A3D' : '#C6FF3D'); l.setAttribute('stroke-width', '4'); lines.appendChild(l); lineEls[k] = l; }
function show(e, a, dy = 0, sc = 1) { e.style.opacity = a; e.style.transform = `translateY(${(1 - a) * 40 + dy}px) scale(${sc})`; e.style.display = a > 0.001 ? 'block' : 'none'; }
function win(t, a0, a1, fi = 0.35, fo = 0.3) { return Math.min(easeO((t - a0) / fi), 1 - easeIO((t - (a1 - fo)) / fo)); }
function proj(v) { const p = v.clone().project(camera); return [(p.x + 1) / 2 * W, (1 - p.y) / 2 * H]; }
function callout(key, world, dx, dy, a) {
  const e = E[key]; const [x, y] = proj(world);
  show(e, a); e.style.left = (x + dx - 80) + 'px'; e.style.top = (y + dy - 30) + 'px'; e.style.transform = `scale(${0.85 + 0.15 * a})`;
  const l = lineEls[key]; l.setAttribute('x1', x); l.setAttribute('y1', y); l.setAttribute('x2', x + dx); l.setAttribute('y2', y + dy); l.setAttribute('opacity', a);
}
// captions: chunks of <= ~4 words with exact word timing
const chunks = [];
for (const s of TIM.scenes) { let cur = [];
  s.words.forEach((w, i) => { cur.push(w); if (cur.length >= 4 || /[.,?!]$/.test(w.w) || i === s.words.length - 1) { chunks.push(cur); cur = []; } }); }
let lastCap = null;
function captions(t) {
  let c = null; for (const ch of chunks) if (t >= ch[0].s - 0.05 && t < ch[ch.length - 1].e + 0.25) c = ch;
  if (c !== lastCap) { cap.innerHTML = c ? '<div class="ln">' + c.map(w => `<span>${w.w}</span>`).join(' ') + '</div>' : ''; lastCap = c; }
  if (c) { const sp = cap.querySelectorAll('span'); c.forEach((w, i) => sp[i].className = (t >= w.s && t < w.e + 0.06) ? 'on' : '');
           const ln = cap.querySelector('.ln'); const k = backO((t - c[0].s + 0.05) / 0.22); ln.style.transform = `scale(${0.9 + 0.1 * k})`; }
}

// ---------- render ----------
window.renderAt = function (t) {
  const v = speedAt(t), d = distAt(t);
  // world motion
  dashes.forEach((m, i) => { const k = Math.floor(i / 2); m.position.x = ((k * 4.6 - d) % 119.6 + 119.6) % 119.6 - 60; });
  posts.forEach((g, i) => { g.position.x = ((i * 12.0 - d) % 168 + 168) % 168 - 84; });
  wheels.forEach(w => { w.spin.rotation.z = -d / 0.37; });
  car.position.y = 0.012 * Math.sin(t * 13) * Math.min(1, v / 10);
  car.rotation.z = (v > 0.5 && t > tR && t < tS + 2.6) ? 0.012 * clamp((t - tR) / 0.8) : 0; // nose dips while slowing
  // x-ray
  const xr = clamp(xray(t));
  paint.opacity = 1 - 0.78 * xr; glassMat.opacity = 1 - 0.8 * xr; blackMat.opacity = 1 - 0.7 * xr;
  paint.depthWrite = xr < 0.05; glassMat.depthWrite = xr < 0.05;
  packMat.opacity = 0.9 * xr; cellMat.opacity = xr; motorMat.opacity = xr; axleMat.opacity = xr;
  const rg = regenAmt(t);
  motorMat.emissiveIntensity = xr * (0.25 + 1.5 * rg * (0.75 + 0.25 * Math.sin(t * 18)));
  cellMat.emissiveIntensity = xr * (0.1 + 0.55 * rg * (0.6 + 0.4 * Math.sin(t * 6)));
  packMat.emissiveIntensity = 0.05 + 0.18 * rg * xr;
  partMat.opacity = xr * rg;
  const m = new THREE.Matrix4();
  for (let i = 0; i < NP; i++) {
    const u = ((t * 0.32 * (0.6 + v / 25)) + i / NP) % 1;
    const p = flowPath.getPointAt(u); const s = 0.6 + 0.6 * Math.sin(i * 7.1 + t * 5);
    m.makeScale(s, s, s); m.setPosition(p); parts.setMatrixAt(i, m);
  }
  parts.instanceMatrix.needsUpdate = true;
  // brakes & lights
  const bl = brakeLights(t);
  tailMat.emissiveIntensity = 0.8 + 3.2 * bl; tailGlow.intensity = 2.2 * bl;
  caliperMat.emissiveIntensity = 1.6 * caliperOn(t);
  // camera
  const [pos, tgt, fov] = camAt(t);
  camera.position.copy(pos); camera.lookAt(tgt); camera.fov = fov; camera.updateProjectionMatrix();
  bloom.strength = 0.45 + 0.2 * bl * clamp((t - tB) / 0.6);
  composer.render();

  // ---- overlay ----
  bar.style.width = (W * t / T) + 'px';
  const h = win(t, 0.15, tL - 0.1);
  show(E.h1, easeO((t - 0.15) / 0.4) * h); show(E.h1b, easeO((t - 0.7) / 0.4) * h);
  show(E.pedals, easeO((t - 1.4) / 0.4) * h);
  const st = E.pedals.querySelector('#strike'); const sk = easeO((t - 2.6) / 0.35);
  st.setAttribute('x2', 10 + 170 * sk); st.setAttribute('y2', 230 - 190 * sk); st.setAttribute('opacity', sk > 0 ? 1 : 0);
  show(E.gen, win(t, tL + 0.9, tR));
  show(E.frac, win(t, tR + 1.8, tS));
  const chipA = win(t, tR + 0.6, tS + 0.4);
  show(E.spd, chipA); show(E.bat, chipA, 0);
  E.spd.style.top = E.bat.style.top = '1060px';
  document.getElementById('spdv').textContent = Math.round(v * 3.6) + ' km/h';
  const batt = 71 + 2.0 * clamp((t - tR) / (tS - tR));
  document.getElementById('batv').textContent = batt.toFixed(1) + '%';
  show(E.stop, win(t, tS + 0.6, tB));
  show(E.hold, win(t, tS + 3.0, tB), 0, 0.9 + 0.1 * backO((t - tS - 3.0) / 0.4));
  show(E.light, win(t, tB + 0.9, tE));
  show(E.end1, win(t, tE + 0.5, T + 5)); show(E.end2, win(t, tE + 1.6, T + 5), 0, 0.9 + 0.1 * backO((t - tE - 1.6) / 0.4));
  callout('cMotor', V(-1.45, 0.42, 0).applyMatrix4(car.matrixWorld), -90, -330, clamp(Math.min(xr, win(t, tL + 1.6, tR + 1.2))));
  callout('cPack', V(0.1, 0.5, 0).applyMatrix4(car.matrixWorld), 150, -380, clamp(Math.min(xr, win(t, tR + 2.6, tS + 0.3))));
  callout('cCal', V(-1.28, 0.49, 1.03).applyMatrix4(car.matrixWorld), 60, -420, win(t, tS + 1.3, tB - 0.1));
  captions(t);
  const gl = renderer.getContext(); gl.finish(); const px = new Uint8Array(4); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
};
renderer.compile(scene, camera);
window.renderAt(0.5);
window.READY = true;
