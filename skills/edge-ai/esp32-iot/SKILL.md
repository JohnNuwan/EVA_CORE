---
name: esp32-iot
description: "Programmer l'ESP32 (Xtensa LX6/LX7) pour l'IoT — Wi-Fi, Bluetooth BLE, Arduino Core, ESP-IDF, MicroPython, communication MQTT/HTTP/CoAP, OTA, deep sleep et protocoles industriels."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [esp32, xtensa, iot, wi-fi, bluetooth, ble, arduino-core, esp-idf, micropython, mqtt, http, coap, ota, deep-sleep, freertos, wifi-manager, ble-peripheral, sensor, actuator, esp-now]
    related_skills: [arduino-programmation, stm32-arm-cortex, embedded-systems-firmware, pcb-design-electronique]
---

# ESP32 — IoT et Systèmes Embarqués Connectés

## Vue d'ensemble

L'ESP32 est un microcontrôleur de la famille Xtensa (LX6/LX7, 32 bits dual-core) produit par Espressif Systems, intégrant nativement le Wi-Fi 802.11 b/g/n, le Bluetooth 4.2/5.0 (BR/EDR + BLE), deux cœurs CPU cadencés jusqu'à 240 MHz, 520 KB SRAM, et de nombreux périphériques (ADC, DAC, I²C, SPI, UART, CAN, I²S, USB OTG, Ethernet MAC, etc.).

### Architecture matérielle ESP32

```
┌──────────────────────────────────────────────────────────────┐
│                     ESP32 (Xtensa LX6/LX7)                   │
├──────────────────────────────────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐   │
│  │ CPU Core 0 │  │ CPU Core 1 │  │  Wi-Fi + Bluetooth   │   │
│  │  (240 MHz) │  │  (240 MHz) │  │  802.11 b/g/n + BLE  │   │
│  │ 32 KB IRAM │  │ 32 KB IRAM │  │  + Classic BT 4.2/5.0│   │
│  └────────────┘  └─────┬──────┘  └──────────────────────┘   │
│                        │                                     │
│  ┌─────────────────────┴────────────────────────────────────┐│
│  │               FreeRTOS + Scheduler                       ││
│  │        (dual-core SMP, files de messages, mutex)         ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐│
│  │   ADC    │ │  UART    │ │  I²C/SPI │ │ GPIO / PWM / IR  ││
│  │ 2×12-bit │ │ 3× UART  │ │ 4× SPI   │ │ 34× GPIO         ││
│  │  (18 can.)│ │          │ │ 2× I²C   │ │ 8× PWM (LEDC)   ││
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Développer un système IoT connecté au Wi-Fi ou au Bluetooth BLE avec l'ESP32.
- Mettre en œuvre une communication MQTT, HTTP REST, CoAP ou WebSocket entre capteurs et un serveur central.
- Programmer l'ESP32 en Arduino Core (rapide, vaste bibliothèque) ou en ESP-IDF (contrôle total, performance).
- Implémenter des modes basse consommation (deep sleep, light sleep) pour des capteurs sur batterie.
- Configurer une mise à jour OTA (Over-The-Air) du firmware ESP32.
- Utiliser BLE pour la communication avec un smartphone (périphérique BLE + services personnalisés).
- Créer un réseau maillé ESP-Now pour la communication sans infrastructure entre ESP32.

Ne pas utiliser pour : du temps réel ultra-critique < 10 µs (les interruptions Wi-Fi ont une latence variable, utiliser un microcontrôleur dédié), des projets nécessitant une certification industrielle complète (IEC 61508), des applications audio professionnelles (préférer un DSP dédié).

---

## 1. Environnements de Développement

### 1.1 Comparaison Arduino Core vs ESP-IDF

| Critère | Arduino Core | ESP-IDF |
|:---|---|---|---:|
| **Prise en main** | Très facile | Complexe (CMake, menuconfig, partitions) |
| **Performances** | Bonnes (couche d'abstraction) | Optimales (accès direct aux registres) |
| **Wi-Fi/BLE** | Bibliothèques simples | Contrôle fin, WiFi events, BLE GATT |
| **Multitâche** | FreeRTOS masqué | FreeRTOS explicite |
| **OTA** | SimpleArduinoOTA | esp_https_ota complet |
| **Basse consommation** | Limité | Mode deep sleep, wake stub |
| **Taille du binaire** | Plus lourde | Plus légère (liens vers l'essentiel) |
| **Documentation** | Très abondante | Technique (Espressif docs) |

### 1.2 Installation PlatformIO

```bash
# Installer PlatformIO Core
pip install platformio

# Créer un projet
pio init --board esp32-devkitc-v4 --project-dir mon_projet
cd mon_projet

# Structure du projet
# mon_projet/
# ├── platformio.ini      # Configuration
# ├── src/
# │   └── main.cpp
# ├── lib/                # Bibliothèques locales
# └── include/            # En-têtes

# Compiler et uploader
pio run
pio run --target upload

# Moniteur série
pio device monitor --port /dev/ttyUSB0 --baud 115200
```

### 1.3 Fichier platformio.ini typique

```ini
[env:esp32-devkitc-v4]
platform = espressif32
board = esp32-devkitc-v4
framework = arduino
monitor_speed = 115200
board_build.partitions = default_16MB.csv

; Bibliothèques
lib_deps =
    bblanchon/ArduinoJson @ ^6.21
    knolleary/PubSubClient @ ^2.8
    plerup/ESPAsyncWebServer @ ^3.3
    tzapu/WiFiManager @ ^2.0

; Options de compilation
build_flags =
    -DCORE_DEBUG_LEVEL=5        ; Logs de debug Wi-Fi
    -DBOARD_HAS_PSRAM           ; Activer PSRAM si disponible
    -mno-optimize-sibling-calls

; Taille de la partition SPIFFS
board_build.filesystem_size = 1MB
```

---

## 2. Connectivité Wi-Fi

### 2.1 Connexion à un réseau Wi-Fi

```cpp
#include <WiFi.h>

const char* ssid = "MonReseau";
const char* password = "MonMotDePasse";

void setup() {
    Serial.begin(115200);

    WiFi.mode(WIFI_STA);           // Station (client)
    WiFi.begin(ssid, password);

    Serial.print("Connexion Wi-Fi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("\nConnecté !");
    Serial.print("Adresse IP : ");
    Serial.println(WiFi.localIP());
    Serial.print("Puissance signal RSSI : ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
}

void loop() {
    // Vérifier périodiquement la connexion
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi déconnecté, reconnexion...");
        WiFi.reconnect();
    }
    delay(10000);
}
```

### 2.2 WiFiManager (Configuration automatique par portail captif)

```cpp
#include <WiFiManager.h>

WiFiManager wm;

void setup() {
    Serial.begin(115200);

    WiFi.mode(WIFI_AP_STA);  // Point d'accès + Station

    // Configuration WiFiManager
    wm.setConfigPortalTimeout(180);  // 3 minutes max
    wm.setConnectTimeout(30);
    wm.setConfigPortalBlocking(false);  // Non bloquant

    // Tenter la connexion ; si échec, ouvrir un portail captif
    if (!wm.autoConnect("ESP32_Config")) {
        Serial.println("Portail captif ouvert (192.168.4.1)");
    }

    Serial.print("Connecté à : ");
    Serial.println(WiFi.SSID());
}

void loop() {
    wm.process();  // Gérer le portail captif en arrière-plan
}
```

### 2.3 Serveur Web asynchrone

```cpp
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>

AsyncWebServer server(80);

void setup() {
    Serial.begin(115200);
    WiFi.begin("SSID", "PASS");

    while (WiFi.status() != WL_CONNECTED) delay(500);

    // Route racine
    server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
        request->send(200, "text/html",
            "<html><body><h1>ESP32 Web Server</h1>"
            "<p>Température: <span id='temp'>--</span> °C</p>"
            "<script>"
            "setInterval(() => {"
            "  fetch('/api/temp').then(r => r.text()).then(v => "
            "    document.getElementById('temp').textContent = v);"
            "}, 1000);"
            "</script></body></html>");
    });

    // API JSON
    server.on("/api/temp", HTTP_GET, [](AsyncWebServerRequest *request){
        float temp = 20.0 + random(-5, 5);  // Capteur simulé
        request->send(200, "text/plain", String(temp));
    });

    server.begin();
    Serial.print("Serveur démarré : http://");
    Serial.println(WiFi.localIP());
}

void loop() {}
```

---

## 3. Communication MQTT

### 3.1 Client MQTT

```cpp
#include <WiFi.h>
#include <PubSubClient.h>

WiFiClient espClient;
PubSubClient client(espClient);

const char* mqtt_server = "broker.emqx.io";
const int mqtt_port = 1883;

void callback(char* topic, byte* payload, unsigned int length) {
    Serial.print("Message reçu [");
    Serial.print(topic);
    Serial.print("] : ");
    for (unsigned int i = 0; i < length; i++) {
        Serial.print((char)payload[i]);
    }
    Serial.println();
}

void reconnect_mqtt() {
    while (!client.connected()) {
        Serial.print("Connexion MQTT...");
        if (client.connect("ESP32_Client")) {
            Serial.println("Connecté !");
            client.subscribe("maison/salon/lampe/cmd");
        } else {
            Serial.print("Échec (rc=");
            Serial.print(client.state());
            Serial.println("). Retry dans 5 s");
            delay(5000);
        }
    }
}

void setup() {
    Serial.begin(115200);
    WiFi.begin("SSID", "PASS");
    while (WiFi.status() != WL_CONNECTED) delay(500);

    client.setServer(mqtt_server, mqtt_port);
    client.setCallback(callback);
}

void loop() {
    if (!client.connected()) reconnect_mqtt();
    client.loop();

    // Publier la température toutes les 30 secondes
    static unsigned long last_pub = 0;
    if (millis() - last_pub >= 30000) {
        last_pub = millis();
        float temp = 22.5;  // Capteur simulé
        char payload[32];
        snprintf(payload, sizeof(payload), "{\"temp\":%.1f}", temp);
        client.publish("maison/capteurs/temperature", payload);
    }
}
```

### 3.2 MQTT avec TLS (MQTTS)

```cpp
#include <WiFiClientSecure.h>

WiFiClientSecure espSecureClient;
PubSubClient clientSecure(espSecureClient);

void setup() {
    // Charger le certificat CA (facultatif selon le broker)
    // espSecureClient.setCACert(ca_cert);  // PEM

    // Désactiver la vérification pour test (NE PAS FAIRE en prod)
    espSecureClient.setInsecure();

    clientSecure.setServer("mqtts://broker.emqx.io", 8883);
}

// Pour un déploiement sécurisé, ajouter le certificat CA :
// 1. Télécharger le PEM du CA :
//    openssl s_client -connect broker.emqx.io:8883 -showcerts
// 2. Le stocker dans PROGMEM :
//    const char ca_cert[] PROGMEM = R"EOF(
//    -----BEGIN CERTIFICATE-----
//    ...
//    -----END CERTIFICATE-----
//    )EOF";
```

---

## 4. Bluetooth Low Energy (BLE)

### 4.1 Service BLE personnalisé (périphérique)

```cpp
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>

#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

bool led_state = false;

BLECharacteristic *pCharacteristic;

class MyCallbacks: public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *pChar) {
        std::string value = pChar->getValue();
        if (value.length() > 0) {
            led_state = (value[0] == '1');
            digitalWrite(2, led_state ? HIGH : LOW);
            Serial.print("LED : ");
            Serial.println(led_state ? "ON" : "OFF");
        }
    }
};

void setup() {
    Serial.begin(115200);
    pinMode(2, OUTPUT);

    BLEDevice::init("ESP32_BLE_Device");
    BLEServer *pServer = BLEDevice::createServer();
    BLEService *pService = pServer->createService(SERVICE_UUID);

    pCharacteristic = pService->createCharacteristic(
        CHARACTERISTIC_UUID,
        BLECharacteristic::PROPERTY_READ |
        BLECharacteristic::PROPERTY_WRITE
    );
    pCharacteristic->setCallbacks(new MyCallbacks());
    pCharacteristic->setValue("0");  // Valeur initiale

    pService->start();
    BLEAdvertising *pAdvertising = pServer->getAdvertising();
    pAdvertising->start();

    Serial.println("Périphérique BLE prêt à se connecter.");
}
```

---

## 5. Modes Basse Consommation

### 5.1 Deep Sleep pour capteurs sur batterie

```cpp
#define uS_TO_S_FACTOR 1000000ULL  // Microsecondes → secondes
#define SLEEP_TIME 3600             // 1 heure

RTC_DATA_ATTR int boot_count = 0;   // Conservé en veille

void setup() {
    Serial.begin(115200);
    delay(1000);  // Attendre la stabilisation du port série

    boot_count++;
    Serial.printf("Réveil #%d\n", boot_count);

    // Configurer la source de réveil (timer + externe)
    esp_sleep_enable_timer_wakeup(SLEEP_TIME * uS_TO_S_FACTOR);
    esp_sleep_enable_ext0_wakeup(GPIO_NUM_4, 0);  // Bouton sur GPIO4

    // Mesurer et envoyer les données (capteurs)
    float temperature = read_temperature_sensor();
    float humidite = read_humidity_sensor();
    send_mqtt(temperature, humidite);  // Publier sur MQTT

    Serial.println("Entrée en deep sleep...");
    Serial.flush();
    esp_deep_sleep_start();  // Le code ne revient jamais ici
}

void loop() {
    // Ne sera jamais exécuté en deep sleep
}

float read_temperature_sensor() {
    return 22.5;  // Simulation
}

float read_humidity_sensor() {
    return 55.0;
}

void send_mqtt(float temp, float hum) {
    // Connexion Wi-Fi rapide
    WiFi.begin("SSID", "PASS");
    WiFi.setAutoReconnect(false);
    // Attendre la connexion (max 5 s)
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 50) {
        delay(100);
        attempts++;
    }
    if (WiFi.status() == WL_CONNECTED) {
        // Publier MQTT
        PubSubClient client(WiFi);
        client.setServer("broker.emqx.io", 1883);
        if (client.connect("ESP32_DeepSleep")) {
            char payload[64];
            snprintf(payload, sizeof(payload),
                     "{\"temp\":%.1f,\"hum\":%.1f}", temp, hum);
            client.publish("maison/capteurs/environnement", payload);
        }
        client.disconnect();
    }
    WiFi.disconnect(true);
}

// Consommation typique :
// - Deep sleep (RTC only) : ~5 µA
// - Deep sleep (ULP coprocessor) : ~150 µA
// - Light sleep : ~0.8 mA
// - Active Wi-Fi TX : ~80-200 mA
// - Active Bluetooth : ~95-130 mA
```

### 5.2 ULP (Ultra-Low-Power) Coprocesseur

```cpp
// Le co-processeur ULP peut fonctionner pendant le deep sleep
// pour lire des capteurs ou compter des impulsions.
// Programmation en assembleur ULP ou via ESP-IDF.

// Exemple ULP (lecture ADC en deep sleep) :
// 1. Configurer l'ULP dans l'ESP-IDF
// 2. Charger un programme ULP dans la mémoire RTC
// 3. Le réveil se produit quand ULP détecte un dépassement de seuil

// Voir : esp-idf/examples/system/ulp/
```

---

## 6. Mise à Jour OTA (Over-The-Air)

### 6.1 ArduinoOTA

```cpp
#include <ArduinoOTA.h>

void setup() {
    WiFi.begin("SSID", "PASS");
    while (WiFi.status() != WL_CONNECTED) delay(500);

    ArduinoOTA.setHostname("ESP32-Capteur");
    ArduinoOTA.setPassword("ota_password");

    ArduinoOTA.onStart([]() { Serial.println("OTA : Début"); });
    ArduinoOTA.onEnd([]() { Serial.println("OTA : Terminé"); });
    ArduinoOTA.onError([](ota_error_t error) {
        Serial.printf("OTA : Erreur %d\n", error);
    });
    ArduinoOTA.begin();
}

void loop() {
    ArduinoOTA.handle();  // Gérer les requêtes OTA
}

// Commande pour uploader :
// espota.py -i 192.168.1.42 -f firmware.bin -a ota_password
```

### 6.2 HTTPS OTA (ESP-IDF)

```bash
# Générer une partition OTA
# La partition OTA permet un rollback en cas d'échec de mise à jour
cat partitions_ota.csv
# nvs,      data, nvs,     0x9000,  0x5000,
# otadata,  data, ota,     0xe000,  0x2000,
# app0,     app,  ota_0,   0x10000, 2M,
# app1,     app,  ota_1,   ,        2M,
# spiffs,   data, spiffs,  ,        1M,
```

---

## 7. Protocoles Industriels sur ESP32

### 7.1 Modbus RTU (RS-485)

```cpp
#include <ModbusRTU.h>

ModbusRTU mb;

void setup() {
    Serial2.begin(9600, SERIAL_8N1, 16, 17);  // RX=16, TX=17
    mb.begin(&Serial2);
    mb.slave(1);  // ID esclave Modbus = 1
}

void loop() {
    if (!mb.slave()) {
        mb.addHreg(0, 250);  // Registre holding 40001 = température * 10 (25.0 °C)
        mb.addHreg(1, 550);  // Registre holding 40002 = humidité * 10
    }

    // Mettre à jour les registres avec les valeurs des capteurs
    mb.Hreg(0, read_temperature() * 10);
    mb.Hreg(1, read_humidity() * 10);

    mb.task();
    delay(10);
}
```

### 7.2 ESP-Now (communication sans infrastructure)

```cpp
#include <esp_now.h>
#include <WiFi.h>

uint8_t broadcast_mac[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

typedef struct {
    uint16_t id;
    float temperature;
    float humidite;
    uint8_t batterie_pct;
} SensorData;

SensorData sensor_data;

void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
    Serial.printf("Paquet envoyé : %s\n",
                  status == ESP_NOW_SEND_SUCCESS ? "OK" : "ÉCHEC");
}

void setup() {
    Serial.begin(115200);
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();  // Pas besoin de connexion Wi-Fi

    if (esp_now_init() != ESP_OK) {
        Serial.println("Échec d'initialisation ESP-Now");
        return;
    }

    esp_now_register_send_cb(OnDataSent);
    esp_now_peer_info_t peerInfo = {};
    memcpy(peerInfo.peer_addr, broadcast_mac, 6);
    peerInfo.channel = 1;
    peerInfo.ifidx = WIFI_IF_STA;

    esp_now_add_peer(&peerInfo);

    sensor_data.id = 1;
    sensor_data.temperature = 22.5;
    sensor_data.humidite = 65.0;
    sensor_data.batterie_pct = 87;
}

void loop() {
    esp_now_send(broadcast_mac, (uint8_t *)&sensor_data, sizeof(sensor_data));
    delay(60000);  // Envoyer toutes les minutes
}
```

---

## Pièges Courants

1. **Consommation Wi-Fi excessive :** Le Wi-Fi consomme 80-200 mA en transmission. Pour les capteurs sur batterie, utiliser `WiFi.setSleep(true)` ou passer en deep sleep entre les envois.

2. **Débordement de la pile FreeRTOS :** Avec l'Arduino Core, les tâches Wi-Fi/MQTT s'exécutent sur le cœur 1. Si la taille de pile par défaut est insuffisante, définir `CONFIG_ARDUINO_EVENT_RUNNING_CORE=0` ou augmenter la pile avec `CONFIG_ARDUINO_LOOP_STACK_SIZE=16384`.

3. **Conflit de temporisation :** Les tâches Wi-Fi et Bluetooth partagent l'antenne. Ne pas activer Wi-Fi et BLE simultanément sauf si l'application gère les créneaux temporels (time-sharing).

4. **Mauvaise gestion de la mémoire PSRAM :** Certains ESP32 ont une PSRAM externe (4-8 MB). Activer `CONFIG_SPIRAM_SUPPORT=y` dans menuconfig et utiliser `heap_caps_malloc(..., MALLOC_CAP_SPIRAM)` pour les gros buffers.

5. **Réinitialisation liée à l'OTA :** Une mise à jour OTA échouée sans partition de secours (fallback) rend l'ESP32 inutilisable. Toujours avoir au moins deux partitions OTA (`ota_0` et `ota_1`).

6. **Perte de calibration ADC :** L'ESP32 n'a pas de référence de tension interne stable pour l'ADC. Pour des mesures précises, utiliser une référence externe ou un capteur calibré (via I²C/SPI).

---

## Liste de vérification (Checklist)

- [ ] Le framework (Arduino Core / ESP-IDF / MicroPython) est choisi selon les besoins.
- [ ] Les partitions sont correctement configurées (OTA, SPIFFS, PSRAM).
- [ ] Le mode Wi-Fi (STA/AP/AP_STA) est adapté au déploiement.
- [ ] Les certificats TLS sont chargés pour MQTT sécurisé.
- [ ] Le watchdog est activé pour les déploiements autonomes.
- [ ] La consommation énergétique est mesurée et optimisée (deep sleep si sur batterie).
- [ ] Les broches conflictuelles sont évitées (ADC2 + Wi-Fi, strapping pins).
- [ ] Le BLE advertising est configuré pour une découverte rapide (intervalle d'advertising).
- [ ] La mise à jour OTA est testée avec un rollback fonctionnel.
- [ ] Les protocoles industriels (Modbus, CAN) ont les terminaisons de bus appropriées.