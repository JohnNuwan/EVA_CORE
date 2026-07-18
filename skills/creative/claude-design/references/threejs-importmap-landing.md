# Three.js Importmap Landing Page Pattern

Use this when creating a creative/interactive landing page with a Three.js 3D background, inspired by sites like [homunculus.jp](https://homunculus.jp/).

## Architecture

Three files: `index.html` + `style.css` + `script.js`

## Key Pattern: Loading Three.js (two options)

### Option A: Importmap (modern browsers only)

```html
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.168.0/build/three.module.js"
  }
}
</script>
<script type="module" src="script.js"></script>
```

Script.js must use `import * as THREE from 'three'`.

**Pros:** Clean ES module syntax. **Cons:** SPOF — fails silently if CDN blocked. Not supported in older browsers. The `importmap` approach is the most common cause of \"nothing appears\" in corporate environments.

### Option B: Classic CDN script tag (RECOMMENDED ✅)

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="script.js"></script>
```

Script.js uses `THREE` as a global (no `import`):

```js
// script.js — regular <script>, not type="module"
if (typeof THREE !== 'undefined') {
  initHead3D();
} else {
  console.warn('Three.js CDN failed — 3D disabled');
  window._heliosReady = true;
}

function initHead3D() {
  window._heliosReady = true;
  // ... Three.js code using THREE.AmbientLight, THREE.Mesh, etc.
}
```

**Pros:** Works in ALL browsers. Graceful fallback. Simpler error handling. Compatible with corporate proxies. **Cons:** Global namespace, no tree-shaking.

## ⚠️ CRITICAL: Inline Fallback Pattern (required for both options)

**The Three.js script is a SPOF (Single Point of Failure).** If the CDN is blocked or slow, the entire page breaks — no text, no buttons, no UI at all.

**Solution: Duplex architecture — inline script handles ALL UI, the external script handles ONLY 3D background.**

The inline script (in `index.html`, runs immediately, no CDN dependency) owns everything visible:

```
inline script (index.html, NOT deferred, NOT module)
  ├── startSite() → removes loading, reveals UI
  ├── revealUI() → handles display:none→opacity transitions
  ├── goInside/goBack → scene transitions
  ├── showDetail/closeDetail → modal panels
  ├── contactOpen/close → contact overlay
  ├── Matrix rain (Canvas 2D, zero dependencies)
  ├── custom cursor, nav buttons, keyboard shortcuts
  └── ZERO external dependencies

external script (script.js, loaded after Three.js CDN)
  └── 3D scene (head, particles, rings, stars)
  └── ABSOLUTELY OPTIONAL — if CDN fails, site works perfectly
```

### Communication protocol between inline and external script

```js
// In index.html (inline script):
window.startSite = function(withSound) {
  revealUI();  // Show all HTML UI immediately
  if (window._heliosReady) window._heliosEnter(withSound);
};

// In script.js (loaded after Three.js CDN):
window._heliosReady = true;
// If user already clicked Enter before this script loaded:
if (window._heliosSound !== undefined) {
  window._heliosEnter(window._heliosSound);
}
```

### The Enter button MUST have onclick in HTML

```html
<button class="loading-start" onclick="startSite(true)">Enter</button>
<button class="loading-noSound" onclick="startSite(false)">Start</button>
```

Without `onclick=""`, the Enter button won't respond until the external script loads — which defeats the entire fallback pattern. The `onclick` triggers the inline `startSite()` which is defined in the inline script.

### HTML structure (recommended)

```html
<!-- 1. Inline script (runs immediately, drives all UI) -->
<script>
// All UI code here — startSite, revealUI, navigation, etc.
</script>

<!-- 2. Three.js from CDN (classic script tag) -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

<!-- 3. 3D enhancement script -->
<script src="script.js"></script>
```

### Why this matters

Without this pattern, if the CDN fails (corporate proxy, no internet, DNS block), the user sees:
- ❌ A blank/dark screen with no text
- ❌ No buttons, no navigation, no feedback
- ❌ They think the page is broken

With this pattern, the page works fully even offline:
- ✅ All text, buttons, navigation, modals load instantly
- ✅ The 3D background is a bonus enhancement
- ✅ User can interact immediately

## Background Strategy: Transparent Three.js Over CSS Gradient

Instead of a flat solid color, use a CSS gradient as the page background (renders immediately, works without Three.js) and make the Three.js canvas transparent so 3D elements float on top.

```css
/* In style.css — visible immediately, no JS dependency */
body {
  background: radial-gradient(ellipse at 50% 40%,
    #1e1b4b 0%,    /* indigo center */
    #0f172a 50%,   /* dark slate mid */
    #020617 100%   /* near-black edge */
  );
}

/* Optional: pulsing accent glow */
body::before {
  content: '';
  position: fixed;
  width: 100%; height: 100%;
  top: 0; left: 0;
  background: radial-gradient(circle at 50% 40%,
    rgba(249,115,22,0.03) 0%, transparent 60%);
  pointer-events: none;
  animation: bgPulse 6s ease-in-out infinite alternate;
}
@keyframes bgPulse {
  0% { opacity: 0.3; transform: scale(1); }
  100% { opacity: 1; transform: scale(1.1); }
}
```

```js
// In script.js — transparent canvas
const renderer = new THREE.WebGLRenderer({
  canvas, alpha: true, antialias: true
});
renderer.setClearColor(0x000000, 0);  // fully transparent
// scene.background is NOT set — CSS gradient shows through
```

```css
/* Canvas CSS — no background-color */
#bg-canvas {
  position: fixed;
  width: 100%; height: 100%;
  top: 0; left: 0;
  display: block;
}
```

This means:
- ❌ No flat "purple screen" before Three.js loads
- ✅ Beautiful gradient visible immediately
- ✅ 3D particles/objects float on top of gradient
- ✅ If Three.js fails, the page still has a rich background

## Loading Screen Pattern (CSS-only, no JS timing)

Avoid JS `setTimeout` chains for the loading screen. Use CSS `@keyframes` with `animation-delay` for reliable, zero-dependency loading animations.

```css
.loading-bar {
  animation: loadingBarFade 2.5s ease forwards;
}
.loading-barIn {
  animation: loadingBarFill 2s 0.3s ease-out forwards;
}
@keyframes loadingBarFill {
  0%   { transform: scaleX(0); }
  70%  { transform: scaleX(0.85); }
  100% { transform: scaleX(1); }
}
@keyframes loadingBarFade {
  0%, 80% { opacity: 1; }
  100%    { opacity: 0; }
}

/* Start button appears after bar fills */
.loading-start {
  opacity: 0;
  pointer-events: none;
  animation: loadingFadeIn 0.8s 2.2s ease forwards;
}
@keyframes loadingFadeIn {
  from { opacity: 0; pointer-events: none; }
  to   { opacity: 1; pointer-events: auto; }
}
```

The Enter button uses `onclick="startSite(true)"` in the HTML, so it responds immediately even before any JS module loads.

## display: none → opacity transition (Double rAF Trick)

You cannot transition `opacity` from `display: none`. The browser needs two frames to register the initial state.

```js
function revealUI() {
  // Step 1: set display + opacity 0 in the same tick
  el.style.display = 'block';
  el.style.opacity = '0';

  // Step 2: next frame — the browser registered opacity 0
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      el.style.transition = 'opacity 1s ease';
      el.style.opacity = '1';  // now it animates
    });
  });
}
```

Without this pattern, elements appear instantly (no animation). With it, they fade in smoothly.

## UI Element Default States

Elements that should be hidden until the user clicks Enter must start with `display: none` AND `opacity: 0` in CSS (not just opacity: 0), otherwise they briefly flash on the screen before JS hides them.

```css
.top-ui, .head-logo, .head-btnWrapp, .mute-btnWrapp {
  display: none;
  opacity: 0;
}
```

## Typical 3D Scene Setup

```js
import * as THREE from 'three';

const canvas = document.getElementById('bg-canvas');
const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(45, innerWidth / innerHeight, 0.1, 1000);
camera.position.set(0, 0, 12);

const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setClearColor(0x000000, 0);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
```

## Scene Elements (layered for depth)

| Layer | Purpose | Typical Config |
|---|---|---|
| **Background stars** | Far depth, slow drift | `PointsMaterial` gold/warm, size 0.06, opacity 0.6 |
| **Particle cloud** | Mid depth, orbits center | 4000 particles, shell distribution, `AdditiveBlending`, vertexColors |
| **Centerpiece** | Focal 3D object | `IcosahedronGeometry` wireframe + `MeshPhysicalMaterial` emissive |
| **Glow sphere** | Subtle inner glow | `SphereGeometry` + `MeshBasicMaterial` opacity 0.08, pulsing scale |
| **Orbital rings** | Motion accent | `TorusGeometry` dashed or solid, rotating at different speeds/axes |

## Particle Shell Distribution

```js
for (let i = 0; i < count; i++) {
  const radius = 2.5 + Math.random() * spread;
  const theta = Math.random() * Math.PI * 2;
  const phi = Math.acos(2 * Math.random() - 1);
  positions[i*3] = radius * Math.sin(phi) * Math.cos(theta);
  positions[i*3+1] = radius * Math.sin(phi) * Math.sin(theta);
  positions[i*3+2] = radius * Math.cos(phi);
}
```

## Mouse Parallax

```js
const mouse = { x: 0, y: 0, targetX: 0, targetY: 0 };
document.addEventListener('mousemove', (e) => {
  mouse.targetX = (e.clientX / innerWidth) * 2 - 1;
  mouse.targetY = -(e.clientY / innerHeight) * 2 + 1;
});

// In animate():
mouse.x += (mouse.targetX - mouse.x) * 0.05;
mouse.y += (mouse.targetY - mouse.y) * 0.05;
camera.position.x = Math.sin(t * 0.1) * 0.8 + mouse.x * 0.5;
```

## Lighting

- `AmbientLight` for base fill
- 2 `DirectionalLight` at opposite positions with different colors (accent + cool)
- 1 `PointLight` orbiting the scene for dynamic highlights

## Animation Loop

```js
function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();
  // Rotate objects, move camera, update particles
  renderer.render(scene, camera);
}
```

## Custom 3D Head Geometry (Vertex Manipulation)

For a metahuman/stylized 3D head (like homunculus.jp), modify a `SphereGeometry`'s vertices to create facial features.

```js
function createHeadGeometry() {
  const geo = new THREE.SphereGeometry(1.5, 40, 40);
  const pos = geo.attributes.position;

  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i);
    const len = Math.sqrt(x*x + y*y + z*z);
    const nx = x/len, ny = y/len, nz = z/len;
    let scale = 1.0;

    // Cranium: elongate top-back
    if (ny > 0.2) scale += (ny - 0.2) * 0.25;

    // Cheeks: widen at mid-face
    const cheekFactor = 1 - Math.abs(ny + 0.2) * 1.5;
    if (cheekFactor > 0 && Math.abs(nx) < 0.3) scale += cheekFactor * 0.08;

    // Jaw/chin: pull down + narrow at bottom
    if (ny < -0.1) {
      scale += Math.abs(ny + 0.1) * 0.8 * 0.15;
      if (ny < -0.3) scale -= Math.abs(ny + 0.3) * 0.3;
    }

    // Eye sockets: subtle indent at (±0.3, 0.15)
    const eyeDist = Math.min(
      Math.sqrt((nx-0.3)**2 + (ny-0.15)**2 + nz**2),
      Math.sqrt((nx+0.3)**2 + (ny-0.15)**2 + nz**2)
    );
    scale -= Math.max(0, 1 - eyeDist * 4) * 0.12;

    // Nose bridge: protrusion in center face
    if (nz < -0.2 && Math.abs(nx) < 0.15 && ny > -0.1 && ny < 0.25) {
      const nf = (1 - Math.abs(ny)*3) * (1 - Math.abs(nx)*8) * Math.abs(nz+0.3);
      if (nf > 0) scale += nf * 0.15;
    }

    // Mouth: subtle indent
    if (ny < -0.15 && ny > -0.35 && Math.abs(nx) < 0.2 && nz < -0.1) {
      scale -= Math.max(0, 1 - Math.abs(ny+0.25)*10) * (1 - Math.abs(nx)*5) * 0.05;
    }

    pos.setXYZ(i, nx*len*scale, ny*len*scale, nz*len*scale);
  }
  pos.needsUpdate = true;
  geo.computeVertexNormals();
  return geo;
}
```

### Rendering the head

```js
// Wireframe head
const head = new THREE.Mesh(headGeo, new THREE.MeshPhysicalMaterial({
  color: 0xf97316, wireframe: true, transparent: true, opacity: 0.45,
  emissive: 0xf97316, emissiveIntensity: 0.15
}));

// Solid glow head (inner)
const glowHead = new THREE.Mesh(headGeo.clone(), new THREE.MeshPhysicalMaterial({
  color: 0xf97316, transparent: true, opacity: 0.06,
  emissive: 0xf97316, emissiveIntensity: 0.1
}));
glowHead.scale.setScalar(0.92);

// Edge glow lines
const edges = new THREE.EdgesGeometry(headGeo);
const edgeLine = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({
  color: 0xf97316, transparent: true, opacity: 0.15
}));
```

### Head-shaped particle distribution

Morph particles toward the head silhouette for a denser aura near the face:

```js
for (let i = 0; i < pointCount; i++) {
  const theta = Math.random() * Math.PI * 2;
  const phi = Math.acos(2 * Math.random() - 1);
  const r = 2.0 + Math.random() * 14;

  const morph = Math.max(0, 1 - (r - 2) / 6);
  const headR = 1.5 * (1 + 0.3 * (phi > Math.PI/2 ? -1 : 1) * Math.cos(phi));

  const px = (r * (1-morph) + headR * morph) * Math.sin(phi) * Math.cos(theta);
  const py = (r * (1-morph) + headR * morph) * Math.cos(phi) + 0.3 * morph;
  const pz = (r * (1-morph) + headR * morph) * Math.sin(phi) * Math.sin(theta);
}
```

### Head animation

```js
head.rotation.y = t * 0.15 + mouse.x * 0.3;
head.rotation.x = Math.sin(t * 0.08) * 0.08 + mouse.y * 0.12;
head.position.y = 0.3 + Math.sin(t * 0.4) * 0.03;
glowHead.rotation.copy(head.rotation);
edgeLine.rotation.copy(head.rotation);
```

## Matrix Rain Effect (Canvas 2D)

Add a Matrix-style digital rain as a full-screen Canvas 2D layer behind the Three.js scene. Runs independently — no CDN, no module, works immediately.

### HTML

```html
<canvas id="bg-canvas"></canvas>   <!-- Three.js (z-index: 2) -->
<canvas id="matrix-rain"></canvas> <!-- Matrix (z-index: 1) -->
```

### CSS

```css
#matrix-rain {
  position: fixed; width: 100%; height: 100%;
  top: 0; left: 0; display: block;
  z-index: 1; opacity: 0.35; pointer-events: none;
}
```

### JS (inline, zero dependencies)

```js
(function() {
  var mc = document.getElementById('matrix-rain');
  if (!mc) return;
  var ctx = mc.getContext('2d');
  var chars = 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789ABCDEF';

  function resize() {
    mc.width = window.innerWidth;
    mc.height = window.innerHeight;
    cols = Math.floor(mc.width / 16);
    drops = Array.from({ length: cols }, () =>
      Math.floor(Math.random() * -mc.height / 16)
    );
  }
  resize();
  window.addEventListener('resize', resize);

  function draw() {
    ctx.fillStyle = 'rgba(15,23,42,0.06)'; // trail fade
    ctx.fillRect(0, 0, mc.width, mc.height);
    ctx.font = '14px monospace';

    for (var i = 0; i < drops.length; i++) {
      var char = chars[Math.floor(Math.random() * chars.length)];
      var x = i * 16;
      var y = drops[i] * 16;

      // Lead character (bright)
      ctx.fillStyle = '#f97316';
      ctx.fillText(char, x, y);

      // Trail (gradient fade)
      for (var j = 1; j < 12; j++) {
        var cy = y - j * 16;
        if (cy < 0) break;
        var alpha = 0.6 - j * 0.045;
        if (alpha <= 0) break;
        ctx.fillStyle = 'rgba(249,115,22,' + alpha.toFixed(2) + ')';
        ctx.fillText(chars[Math.floor(Math.random() * chars.length)], x, cy);
      }

      if (drops[i] * 16 > mc.height && Math.random() > 0.975) drops[i] = 0;
      drops[i]++;
    }
    requestAnimationFrame(draw);
  }
  draw();
})();
```

### Customization

| Variable | Effect |
|---|---|
| `opacity: 0.35` (CSS) | Overall brightness |
| `'rgba(15,23,42,0.06)'` | Trail fade speed |
| `chars` | Character set (katakana, hex, binary) |
| `'#f97316'` | Lead character color |
| `'14px monospace'` | Column width / density |
| `j < 12` | Trail length |

## Multi-Canvas Z-Index Stacking

```
z-index: 10+    → HTML UI (buttons, text, modals)
z-index: 3     → Three.js canvas (head, particles)
z-index: 2     → Matrix rain (or noise/grain)
z-index: 1     → CSS gradient background
```

Each layer is independent — one can fail without breaking others, and effects compose visually.

## Navigation Pattern: Flexbox-Centered Buttons

Avoid `position: absolute` with `calc(50vw - Xvw)` for navigation buttons — these cause horizontal scrollbars on smaller screens and break when button labels change length.

### Recommended: Flexbox Navigation

```css
/* Navigation container — centered flex */
.top-navi {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 60px;
  height: 40px;
}

/* Decorative line as ::before (not on the container itself) */
.top-navi::before {
  content: '';
  position: absolute;
  width: 100%; height: 1px;
  top: 50%; left: 0;
  transform: translateY(-50%);
  pointer-events: none;
  background: linear-gradient(to right,
    transparent,
    rgba(255,255,255,0.15) 15%,
    rgba(255,255,255,0.0) 45%,
    rgba(255,255,255,0.0) 55%,
    rgba(255,255,255,0.15) 85%,
    transparent
  );
}
```

### Buttons with data-section attributes

```html
<button class="top-navi-btn" data-section="code">
  <div class="top-navi-wave"></div><p>Code &amp; Dev<sup>#1</sup></p>
</button>
<button class="top-navi-btn" data-section="industrial">
  <div class="top-navi-wave"></div><p>Industrial &amp; OT<sup>#2</sup></p>
</button>
```

```css
.top-navi-btn {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  padding-left: 30px;
  white-space: nowrap;
  font-size: 14px;
}
```

```js
// Mapping: data-section → detail section id
document.querySelectorAll('.top-navi-btn').forEach(function(btn) {
  btn.addEventListener('click', function() {
    var s = btn.dataset.section;
    var id = s === 'code' ? 1 : s === 'industrial' ? 2 : s === 'ai' ? 3 : s === 'platform' ? 4 : 5;
    showDetail(id);
  });
});
```

### Why this is better

| Approach | Problem | Fix |
|---|---|---|
| `position: absolute; left: calc(50vw - 28vw)` | Buttons overflow viewport, horizontal scroll, breaks on resize | Flexbox centered |
| `:nth-child(1)` CSS selectors | Brittle — breaks if buttons reordered | `data-section` attributes |
| Inline `onclick="showDetail(1)"` | Couples HTML to JS logic | JS event listener reads `dataset.section` |

## Card-Based Detail Content Layout

When displaying capabilities (agent landing page, portfolio), use a card grid instead of flat text lists for better visual scannability.

### HTML Structure

```html
<div class="detail-card-grid">
  <div class="detail-card">
    <div class="detail-card-icon">⌨</div>
    <div class="detail-card-title">Langages</div>
    <div class="detail-card-items">
      <span>Python</span><span>JavaScript</span><span>TypeScript</span><span>Go</span>
    </div>
  </div>
  <div class="detail-card">
    <div class="detail-card-icon">🌐</div>
    <div class="detail-card-title">Web &amp; Backend</div>
    <div class="detail-card-items">
      <span>React</span><span>Node.js</span><span>REST APIs</span>
    </div>
  </div>
</div>
```

### CSS

```css
.detail-card-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin: 20px 30px;
}
@media (max-width: 600px) {
  .detail-card-grid {
    grid-template-columns: 1fr;
    margin: 16px 20px;
  }
}
.detail-card {
  background: #fff;
  border-radius: 10px;
  padding: 18px;
  border: 1px solid rgba(0,0,0,0.05);
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.detail-card-icon {
  font-size: 20px;
  margin-bottom: 8px;
}
.detail-card-title {
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 6px;
}
.detail-card-items {
  font-size: 13px;
  line-height: 1.5em;
  color: #475569;
}
.detail-card-items span {
  display: inline-block;
  background: rgba(249,115,22,0.08);
  color: #c2410c;
  padding: 1px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin: 1px 2px;
  white-space: nowrap;
}
```

### Profile section (dark card for company info)

```css
.detail-profile-section {
  margin: 40px 30px 0 30px;
  padding: 24px;
  background: #0f172a;
  border-radius: 12px;
  color: #e2e8f0;
}
.detail-profile-section .detail-card-title {
  color: #f97316;
}
.detail-profile-section .detail-card-items {
  color: #94a3b8;
}
```

### Multiple sections with showDetail(id)

Maintain 5 sections (1-5) with a clear mapping. The `showDetail` function must handle all IDs:

```js
window.showDetail = function(id) {
  // Hide all sections
  [1,2,3,4,5].forEach(function(i) {
    document.getElementById('detail-' + i).style.display = i === id ? 'block' : 'none';
  });
  // ... animation logic
};
```

When closing, reset all sections:

```js
[1,2,3,4,5].forEach(function(i) {
  var t = document.getElementById('detail-title-' + i);
  var c = document.getElementById('detail-cont-' + i);
  if (t) t.classList.remove('detail-title-mask-anim');
  if (c) c.classList.remove('detail-title-mask-anim');
});
```

## Detail Panel Auto-Scroll

When opening a detail panel, auto-scroll to the content area (skip the decorative title image). Add this after the mask animation:

```js
setTimeout(function() {
  var block = document.querySelector('.detail-block');
  if (block) {
    var rect = block.getBoundingClientRect();
    page.scrollTo({ top: rect.top - 80, behavior: 'smooth' });
  }
}, 600);
```

The 600ms delay allows the mask-reveal animation to play before the scroll starts. The -80px offset leaves breathing room at the top.

## When to Use

- Creative/artistic landing pages (agency, portfolio, product launch)
- Agent presentation pages (like homunculus.jp style)
- Any single-page experience where background motion and depth matters
- Fast prototyping — no build step, no bundler

## When NOT to Use

- Production sites needing SEO — Three.js canvas is invisible to crawlers
- Pages with heavy interactivity that conflicts with Three.js event handlers
- Battery-constrained targets — 3D rendering is expensive on mobile
- Sites that must work fully offline — CDN-based three.js will fail

## Comprehensive Content Rule (Agent/Landing Pages)

When creating a **presentation/landing page for an agent** (AI assistant, engineering service, agency), the user expects **exhaustive coverage** of capabilities — not a summary. This is a recurring expectation from Actemium/Homunculus-style clients.

### What \"exhaustive\" means

| Topic | Minimal (fails) | Exhaustive (passes) |
|---|---|---|
| Languages | "Python, JavaScript" | "Python, JavaScript/TypeScript, Go, Rust, C, Java, Bash, PowerShell" |
| PLC brands | "Siemens, Rockwell" | "Siemens S7/TIA Portal, Rockwell Studio 5000, Beckhoff TwinCAT, Schneider Control Expert, B&R, Mitsubishi GX Works, Omron Sysmac, WAGO, CODESYS, Phoenix PLCnext" |
| AI/ML | "PyTorch, TensorFlow" | "PyTorch, TensorFlow/Keras, JAX, scikit-learn, XGBoost, LightGBM, Transformers, YOLO, SAM, RAG, ONNX, TensorRT" |
| Standards | "ISA-88" | "IEC 61131-3, ISA-88 (Batch/PackML), ISA-95, ISA-18.2, ISO 13849, ISO 12100, IEC 62443" |

### How to populate content

1. **Look at the agent's actual skills library** — the available skills list IS the feature catalog
2. **Group by category** — matching the navigation sections (Code, Industrial, AI, Platform, Profile)
3. **Be specific** — list exact brand names and protocol names, not generic categories
4. **Include versions/standards numbers** — IEC 61131-3, ISA-88, ISO 27001
5. **Expect iteration** — the user will flag anything missing. Treat the first pass as v1.

### Common gaps that users will call out

- Missing a specific PLC brand ("tu n'as pas mis Schneider")
- Missing a protocol ("où est OPC UA?")
- Missing safety standards ("et la sécurité fonctionnelle?")
- Missing a language ("Go aussi non?")
- Missing a domain ("et l'edge computing?")
- Missing platform capabilities ("et la délégation multi-agents?", "et le gateway?")