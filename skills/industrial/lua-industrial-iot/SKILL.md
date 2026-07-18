---
name: lua-industrial-iot
description: "Scripter en Lua pour les passerelles IoT et Kepware."
version: 1.1.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, windows]
metadata:
  tags: [lua, iot, gateway, kepware, embedded, scripting, edge, network-monitoring]
  related_skills: [industrial-programming-languages, ot-it-integration-languages]
---

# Scripting Lua pour l'IoT Industriel, les Routeurs Cellulaires et Kepware

Cette compétence régit le développement de scripts Lua légers et performants destinés à s'exécuter dans des environnements industriels aux ressources matérielles contraintes (passerelles IoT, routeurs, serveurs de communication Kepware).

---

## 1. Modèle d'Objets avec Métatables et Optimisation Mémoire

En Lua, la table (`{}`) est la structure de données unique. Pour concevoir du code structuré sans gaspiller de mémoire, on utilise les métatables pour implémenter des mécanismes de classes légères.

```lua
-- Définition d'une classe de capteur
Sensor = {}
Sensor.__index = Sensor

function Sensor.new(tag, min_val, max_val)
    local self = setmetatable({}, Sensor)
    self.tag = tag
    self.min = min_val
    self.max = max_val
    return self
end

function Sensor:scale_value(raw_val)
    -- Conversion d'une valeur brute 0-32767 (PLC) vers la plage réelle
    local scaled = self.min + (raw_val / 32767.0) * (self.max - self.min)
    return scaled
end
```

### Règle d'Or de Gestion de la RAM (Garbage Collector)
Pour éviter la latence induite par le ramasse-miettes (Garbage Collector - GC) dans les environnements embarqués (par ex. routeurs Teltonika avec 32 Mo de RAM) :
* Évitez d'instancier des tables temporaires dans les boucles d'acquisition rapides.
* Forcez manuellement des cycles de nettoyage si nécessaire à des moments calmes de la passerelle :
  ```lua
  -- Ajustement de l'agressivité du GC
  collectgarbage("setpause", 100) -- Reprise immédiate du GC
  collectgarbage("setstepmul", 200) -- Vitesse d'exécution double
  ```

---

## 2. Scripting Avancé de Simulation de Données sous Kepware

Kepware intègre Lua pour modéliser des comportements dynamiques de variables sans connecter de véritable automate lors des phases de tests FAT.

```lua
-- Script Kepware exécuté cycliquement pour simuler la température d'un four
-- Les variables d'état persistantes doivent être déclarées au niveau global

if temp_four == nil then
    temp_four = 20.0       -- Température initiale
    consigne = 180.0       -- Consigne thermique
    constante_temps = 0.05 -- Inertie thermique
end

-- Algorithme de transfert thermique simple (premier ordre)
local ecart = consigne - temp_four
local variation = ecart * constante_temps

-- Ajout d'une fluctuation aléatoire simulant du bruit de mesure (ex: +/- 0.5 °C)
local bruit = (math.random() - 0.5) * 1.0
temp_four = temp_four + variation + bruit

-- Assignation de la valeur simulée au Tag Kepware
-- Remarque : La fonction d'écriture dépend du runtime de Kepware (ex: WriteTag)
WriteTag("Canal_1.Equipement_1.Temperature_Four", temp_four)
```

---

## 3. Scripts d'Administration et Diagnostic Réseau (Teltonika / OpenWrt)

Les passerelles IoT ou routeurs cellulaires d'atelier (ex: Teltonika RUT240/RUT955) s'appuient sur Lua pour interagir avec le système de configuration unifié UCI et l'API système `ubus`.

### Script de Surveillance WAN avec Alerte MQTT
Ce script s'exécute en tâche périodique (cron) pour vérifier la qualité de la liaison cellulaire et publier des diagnostics.

```lua
local http = require("socket.http")
local ltn12 = require("ltn12")

-- Fonction pour lire le niveau de signal réseau via la commande CLI du modem
function get_signal_dbm()
    local handle = io.popen("gsmctl -q") -- Commande spécifique Teltonika
    local result = handle:read("*a")
    handle:close()
    local dbm = tonumber(result:match("([^%s]+)"))
    return dbm or -113 -- Valeur minimale par défaut en cas d'échec
end

local signal = get_signal_dbm()
local status = "OK"

if signal < -95 then
    status = "FAIBLE"
elseif signal < -110 then
    status = "DECONNECTE"
end

-- Envoi d'une alerte JSON au serveur central
local payload = string.format('{"gateway_id":"RUT955_Atelier_1", "signal_dbm":%d, "wan_status":"%s"}', signal, status)
local response = {}

local _, code = http.request{
    url = "http://192.168.1.50:8080/api/gateways/health",
    method = "POST",
    headers = {
        ["Content-Type"] = "application/json",
        ["Content-Length"] = tostring(string.len(payload))
    },
    source = ltn12.source.string(payload),
    sink = ltn12.sink.table(response)
}

if code ~= 200 then
    -- Échec d'envoi réseau : journalisation en mémoire locale locale ou syslog
    os.execute("logger -t ActemiumIoT 'Echec envoi diagnostics WAN'")
end
```
