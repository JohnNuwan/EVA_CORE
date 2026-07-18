# Three.js Loading Screen Coordination

When creating interactive HTML pages with Three.js via CDN `importmap`, the module script loads asynchronously. The loading screen must work before the module arrives and gracefully hand off to it when ready.

## Architecture

```
Browser renders HTML
  │
  ├── Inline <script> executes IMMEDIATELY
  │     └── Defines window.startSite()
  │     └── Button onclick= startSite(true/false) works at click
  │
  ├── <script type="importmap"> starts loading Three.js
  │
  └── <script type="module" src="script.js"> starts loading
        └── Sets window._EVAReady = true
        └── Checks: if _EVASound already set → reveal now
        └── Defines _EVAEnter() with full UI reveal logic
```

## Three states the user can be in when module loads

| State | What happens |
|---|---|
| **User hasn't clicked yet** | Module sets `_EVAReady = true`, defines `_EVAEnter()`. When user later clicks, inline `startSite()` calls `_EVAEnter()`. |
| **User already clicked** | Inline code already set `_EVASound`. Module checks `if (window._EVASound !== undefined)` → calls `_EVAEnter()` immediately. |
| **Module fails to load** (CDN down) | Inline `startSite()` still runs and hides the loading screen. The user sees the dark Three.js canvas background (set in HTML/CSS) without 3D content. |

## HTML structure

```html
<!-- Canvas for Three.js — MUST exist before module loads -->
<canvas id="bg-canvas"></canvas>

<!-- Loading overlay — z-index above canvas -->
<div class="loading" id="loading">
  <div class="loading-bg"></div>
  <div class="loading-bar"><div class="loading-barIn"></div></div>
  <button class="loading-start" id="loading-start" onclick="startSite(true)">
    <p class="loading-name">EVA DevAssist</p>
    <div class="loading-start-actWrapp">
      <div class="loading-start-actBg"></div>
      <div class="loading-start-act">Enter</div>
    </div>
  </button>
  <button class="loading-noSound" id="loading-noSound" onclick="startSite(false)">Start</button>
</div>

<!-- Inline fallback — executes immediately -->
<script>
window.startSite = function(withSound) {
  window._EVASound = withSound;
  const el = document.getElementById('loading');
  if (el) {
    el.style.transition = 'opacity 0.5s';
    el.style.opacity = '0';
    setTimeout(function() { el.remove(); }, 600);
  }
  if (window._EVAReady) {
    window._EVAEnter(withSound);
  }
};
</script>

<!-- importmap + module -->
<script type="importmap">{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.168.0/build/three.module.js"
  }
}</script>
<script type="module" src="script.js"></script>
```

## Module script (top)

```js
window._EVAReady = true;
if (window._EVASound !== undefined) {
  window._EVAEnter(window._EVASound);
}

// ... Three.js setup ...

window._EVAEnter = function(withSound) {
  if (document.querySelector('.loading') === null) return; // already entered
  
  // Fade out loading bg
  const bg = document.querySelector('.loading-bg');
  if (bg) { bg.style.transition = 'opacity 1.2s ease'; bg.style.opacity = '0'; }

  // Hide start buttons
  const s = document.getElementById('loading-start');
  const ns = document.getElementById('loading-noSound');
  if (s) s.style.display = 'none';
  if (ns) ns.style.display = 'none';

  // Remove loading after delay, show UI
  setTimeout(() => {
    const l = document.querySelector('.loading');
    if (l) l.remove();
    // Reveal UI elements with fade-in
    const ui = document.getElementById('top-ui');
    if (ui) { ui.style.display = 'block'; ui.style.opacity = '0';
      setTimeout(() => { ui.style.transition = 'opacity 1s ease'; ui.style.opacity = '1'; }, 50); }
  }, 1200);
};
```

## CSS rules

```css
/* Loading must be above canvas */
.loading { z-index: 1000; }
#bg-canvas { position: fixed; top: 0; left: 0; z-index: 1; }

/* UI elements start hidden */
.top-ui { display: none; }
.head-logo { display: none; }

/* Loading animations — pure CSS, no JS dependency */
@keyframes loadingBarFill {
  0% { transform: scaleX(0); }
  100% { transform: scaleX(1); }
}
@keyframes loadingFadeIn {
  from { opacity: 0; pointer-events: none; }
  to { opacity: 1; pointer-events: auto; }
}

/* Canvas background color visible if Three.js fails */
#bg-canvas { background-color: #0f172a; }
```

## Common failure modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Purple/black screen, nothing happens" | Loading buttons hidden, module not loaded, no inline fallback | Add inline `<script>` before importmap that handles click immediately |
| UI elements visible before clicking Enter | Elements start with `opacity: 0` instead of `display: none` in CSS | Add `display: none` to all UI elements in CSS; JS sets `display: block` when revealing |
| Loading bar doesn't animate | `setTimeout` in JS before module loaded | Use CSS `@keyframes` for all loading animations, not JS timers |
| Three.js never renders | CDN blocked or importmap failed | Check network tab; ensure canvas has correct id; fall back to CSS background-color |
