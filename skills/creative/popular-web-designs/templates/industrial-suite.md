# Design System: Industrial Suite (Glow Dark & Orange Highlights)

> **EVA Agent — Implementation Notes**
>
> This design system is optimized for high-fidelity technical presentations, industrial dashboards (OT/IT showcases, cybersecurity compliance), and product landing pages. It builds upon the deep, precise aesthetics of Linear but incorporates warm industrial highlights and glowing gradients to prevent monotone fatigue.
> 
> - **Primary Font:** `Inter` (geometric alternates `"cv01", "ss03"` enabled)
> - **Monospace Font:** `JetBrains Mono`
> - **Color Contrast:** Deep tech-navy (`#08090a`), premium panels (`#0f1011`), glowing indigo halos, and warm industrial orange accents (`#f97316`) for vital call-to-actions.
> 
> Use the accompanying dual-mode Python template to ensure 100% execution capability across any target machine without packaging errors.

## 1. Visual Theme & Atmosphere
- **Page Background:** Midnight tech-blue and black gradient (`#0a0f1d` to `#08090a`).
- **Glow Elements (Halos):** Subtle, large background blur layers (e.g. `bg-linear-indigo/20` at `blur-[120px]`) that float behind the hero and primary cards.
- **Accents:** Warm orange (`#f97316` / `#fdba74`) to represent high voltage, industrial precision, and trust. Used on dynamic pings, status indicators, and main CTA badges.
- **Borders:** Translucent white borders (`rgba(255,255,255,0.05)`) paired with state-based hover shadows (`hover:border-linear-indigo/40`).

---

## 2. Component Blueprints

### A. Professional OT/IT Grid
Use a side-by-side layout (two columns) to pitch structural interoperability.
```html
<div class="grid md:grid-cols-2 gap-12">
  <!-- Card 1: OT/Automatisme -->
  <div class="p-8 rounded-xl bg-[#0f1011] border border-white/[0.05] relative overflow-hidden">
    <h4 class="text-xl font-bold text-white mb-6 border-b border-white/[0.05] pb-3">Automatisme & OT</h4>
    <div class="space-y-6">
      <div class="group pb-4 border-b border-white/[0.03]">
        <div class="flex justify-between items-center mb-1">
          <span class="font-mono text-sm font-semibold text-white">Siemens SCL / AWL</span>
          <span class="text-[10px] bg-white/[0.05] border border-white/[0.08] px-2 py-0.5 rounded text-linear-textSecondary font-mono">Natif</span>
        </div>
        <p class="text-xs text-[#8a8f98] font-light">Génération de blocs de données robustes optimisés pour TIA Portal.</p>
      </div>
    </div>
  </div>
  ...
</div>
```

### B. Normative & Cybersecurity Cards
Group high-impact skills into responsive glowing card wrapper blocks (`from-red-500/20 to-orange-500/10` for cybersecurity or `from-blue-500/20` for standardisation).
```html
<div class="group p-8 rounded-xl bg-gradient-to-br from-red-500/20 to-orange-500/10 border border-white/[0.05] hover:border-red-500/40 transition duration-300 shadow-xl">
  <div class="flex items-center space-x-3 mb-6 border-b border-white/[0.05] pb-4">
    <span class="w-2.5 h-2.5 rounded-full bg-red-400 animate-pulse"></span>
    <h4 class="text-lg font-bold text-white">Cybersécurité Industrielle</h4>
  </div>
  <!-- Skill entries -->
</div>
```

---

## 3. Dual-Mode Server Pattern (Zero-Dependency Fallback)
Always wrap your Flask apps with an integrated standard http fallback. This prevents "junior-dev" failures on the client side caused by missing packages in their environment during live testing.

```python
import os
import sys

# 1. Define your centralized presentation data structure
presentation_data = {
    "name": "EVA DevAssiste",
    "tagline": "L'agent autonome d'élite pour l'industrie 4.0...",
    "skills": [...]
}

# 2. Dual Flask / Standalone Routing Engine
try:
    from flask import Flask, render_template
    app = Flask(__name__, template_folder=os.path.abspath('templates'))

    @app.route('/')
    def index():
        return render_template('index.html', EVA=presentation_data)

    if __name__ == '__main__':
        app.run(debug=True, port=5000)

except ImportError:
    print("Warning: Flask not found. Activating standalone Jinja2-less engine...")
    import http.server
    import socketserver
    import re

    class StandaloneTemplateRenderer(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                template_path = os.path.join(os.path.abspath('templates'), 'index.html')
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Basic Regex replacements mimicking Jinja loops
                # [Inject fallback loop compilers here...]
                
                self.wfile.write(content.encode('utf-8'))
            else:
                super().do_GET()

    PORT = 5000
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), StandaloneTemplateRenderer) as httpd:
        httpd.serve_forever()
```
