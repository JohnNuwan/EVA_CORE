# Zéro-Dépendance Fallback Server & Gabarits Industriels

Lors de la livraison de maquettes de tableaux de bord, de landing pages ou d'interfaces d'administration pour les ingénieurs d'EVA, l'environnement cible peut ne pas disposer de paquets de serveurs web comme Flask ou FastAPI. Ce guide définit la méthode de livraison d'applications hybrides robustes à zéro dépendance avec simulation de moteur de rendu de gabarits.

## 1. Patrouille de secours : Serveur Web Standard Library (http.server)

Cette implémentation permet à l'utilisateur de lancer l'application avec un simple interpréteur Python standard, tout en maintenant l'hermétisme de la séparation des préoccupations (fichiers HTML séparés, CSS propre).

```python
import os
import sys
import re
import http.server
import socketserver

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

EVA_data = {
    "name": "EVA DevAssiste",
    "languages": [
        {"category": "OT", "list_items": [{"name": "SCL"}]}
    ]
}

try:
    from flask import Flask, render_template
    app = Flask(__name__, template_folder=TEMPLATE_DIR)

    @app.route('/')
    def index():
        return render_template('index.html', EVA=EVA_data)

except ImportError:
    # Serveur de secours autonome sans dépendances
    class StandaloneTemplateRenderer(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                template_path = os.path.join(TEMPLATE_DIR, 'index.html')
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Simulation simple de substitution
                content = content.replace('{{ EVA.name }}', EVA_data["name"])

                # Remplacement de boucles basiques par Expression Régulière
                # Exemple pour une boucle For Jinja2
                # Pour éviter le crash de Jinja2, utilisez list_items au lieu de items.
                
                self.wfile.write(content.encode('utf-8'))
            else:
                super().do_GET()

    PORT = 5000
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), StandaloneTemplateRenderer) as httpd:
        print(f"Serveur de secours autonome actif sur http://127.0.0.1:{PORT}")
        httpd.serve_forever()
```

## 2. Le Piège d'Attribut `items` de Jinja2 (Namespace Collision)

### Le Problème :
Dans un dictionnaire Python ou un contexte de rendu, l'utilisation d'une clé nommée `"items"` (ex: `{"category": "OT", "items": [...]}`) provoque un échec critique lors du rendu Jinja2 :
`TypeError: 'builtin_function_or_method' object is not iterable`

Jinja2 intercepte `.items` et tente d'appeler la méthode native `dict.items()`, ignorant l'itérable que vous avez affecté à la clé.

### La Correction Systématique :
Utilisez toujours un nom distinct et explicite comme `list_items` ou `items_list` :
```html
<!-- INCORRECT (Provoque une collision d'attribut Jinja) -->
{% for item in category.items %}

<!-- CORRECT -->
{% for item in category.list_items %}
```

## 3. Schémas de Réseaux OT/IT avec SVG Intégrés

Pour les livrables d'ingénierie, utilisez des diagrammes vectoriels SVG en ligne au lieu d'images statiques ou de librairies JavaScript lourdes.

### Bonnes pratiques :
1. **Grille de fond technique :** Définissez un motif `<pattern>` de grille sombre de 30px ou 40px pour renforcer l'aspect d'ingénierie précise.
2. **Identification des Zones (ISA/IEC 62443) :** Représentez clairement la Pyramide du CIM en segmentant par bande horizontale (Niveau 3 SCADA, Niveau 2 PLC, Niveau 1 Capteurs/Robots) avec des contours pointillés (`stroke-dasharray="4,4"`).
3. **Masquage d'Arrière-Plan :** Dessinez des rectangles opaques sous les textes de liaisons pour qu'ils soient lisibles sans être traversés par les flèches directionnelles.
