---
name: arduino-programmation
description: "Programmer des microcontrôleurs Arduino (AVR, SAMD, RP2040) — langage Wiring/C++, bibliothèques, capteurs, actionneurs, communication série et protocoles IoT."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [arduino, avr, atmega, samd, rp2040, wiring, c-plus-plus, i2c, spi, uart, pwm, adc, capteur, actionneur, servo, moteur, iot, modbus, platformio, arduino-cli]
    related_skills: [esp32-iot, stm32-arm-cortex, embedded-systems-firmware, electronique-analogique]
---

# Programmation Arduino

## Vue d'ensemble

Arduino est une plateforme de prototypage électronique open source basée sur des microcontrôleurs AVR (ATmega), SAMD (Cortex-M0+) et RP2040 (Cortex-M0+ dual-core). Cette compétence couvre la programmation en langage Wiring/C++, l'utilisation des bibliothèques, l'interface avec les capteurs et actionneurs, la communication série et les protocoles IoT industriels.

### Architecture logicielle d'un programme Arduino

```
┌──────────────────────────────────────────────────────┐
│                 Programme Arduino (.ino)              │
├──────────────────────────────────────────────────────┤
│ void setup() {                                       │
│   // Configuration unique au démarrage                │
│   pinMode(LED_BUILTIN, OUTPUT);                      │
│   Serial.begin(115200);                              │
│ }                                                    │
│                                                      │
│ void loop() {                                        │
│   // Boucle infinie exécutée en continu               │
│   digitalWrite(LED_BUILTIN, HIGH);                   │
│   delay(1000);                                       │
│   digitalWrite(LED_BUILTIN, LOW);                    │
│   delay(1000);                                       │
│ }                                                    │
├──────────────────────────────────────────────────────┤
│                  Bibliothèques                        │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│ │ Capteurs │ │ Affichage│ │Communication│ │Moteurs/  │ │
│ │ DS18B20  │ │  OLED    │ │ Serial/  │ │ Servos   │ │
│ │ BME280   │ │   LCD    │ │ I²C/SPI  │ │ Steppers │ │
│ │ HC-SR04  │ │          │ │ MQTT/HTTP│ │ DC Motor │ │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
└──────────────────────────────────────────────────────┘
```

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Programmer un microcontrôleur Arduino pour lire des capteurs (température, humidité, distance, lumière, mouvement) et commander des actionneurs (LED, relais, moteurs, servos, afficheurs).
- Mettre en œuvre une communication série (UART) entre un Arduino et un PC ou un autre microcontrôleur.
- Utiliser les protocoles I²C et SPI pour connecter des périphériques (écran OLED, lecteur RFID, mémoire SD, DAC).
- Développer un projet IoT avec connexion Ethernet (W5500, ENC28J60) ou Wi-Fi (ESP8266 en AT mode).
- Implémenter un protocole Modbus RTU (via RS-485) sur Arduino pour l'interface avec des automates industriels.
- Contrôler des moteurs pas-à-pas (stepper) ou des servos pour la robotique.
- Prototyper rapidement un système embarqué avant de le porter sur un microcontrôleur plus performant (STM32, ESP32).

Ne pas utiliser pour : du développement firmware industriel certifié SIL (utiliser `embedded-systems-firmware`), des applications nécessitant du multitâche temps réel complexe (préférer STM32 + FreeRTOS), la gestion de mémoire étendue (> 256 KB RAM).

---

## 1. Environnement de Développement

### 1.1 Arduino IDE vs Arduino CLI vs PlatformIO

| Outil | Type | Points forts | Limites |
|:---|---|---|:---|
| **Arduino IDE 2.x** | GUI | Simple, auto-détection des ports, moniteur série intégré | Limité pour les gros projets |
| **Arduino CLI** | Ligne de commande | Scriptable, CI/CD, compilation + upload automatisé | Pas d'IDE graphique |
| **PlatformIO (VSCode)** | Extension IDE | Gestion des dépendances, support multi-plateforme, debugging | Courbe d'apprentissage |

### 1.2 Installation et configuration (Arduino CLI)

```bash
# Installation sur Linux
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
sudo mv arduino-cli /usr/local/bin/

# Configuration initiale
arduino-cli config init
arduino-cli core update-index

# Installation du cœur AVR (Arduino Uno, Mega, Nano)
arduino-cli core install arduino:avr

# Installation du cœur SAMD (Arduino Zero, MKR)
arduino-cli core install arduino:samd

# Installation du cœur RP2040 (Raspberry Pi Pico, Nano RP2040)
arduino-cli core install arduino:mbed_rp2040

# Liste des cartes installées
arduino-cli board list

# Compilation et upload
arduino-cli compile --fqbn arduino:avr:uno mon_projet/
arduino-cli upload --fqbn arduino:avr:uno -p /dev/ttyACM0 mon_projet/
```

### 1.3 Structure d'un projet

```
mon_projet/
├── mon_projet.ino        # Code principal (setup + loop)
├── config.h              # Configuration (pins, constantes)
├── capteur_temperature/  # Dossier de bibliothèque locale
│   ├── capteur_temperature.h
│   └── capteur_temperature.cpp
└── lib/                  # Bibliothèques tierces
    └── Adafruit_BME280/
```

---

## 2. Entrées/Sorties Fondamentales

### 2.1 GPIO (General Purpose Input/Output)

```cpp
// Configuration des broches dans setup()
void setup() {
    // Sorties
    pinMode(LED_BUILTIN, OUTPUT);       // LED interne sur broche 13 (Uno)
    pinMode(9, OUTPUT);                 // Sortie PWM sur broche 9
    pinMode(8, OUTPUT);                 // Sortie numérique standard

    // Entrées
    pinMode(2, INPUT);                  // Entrée numérique (bouton poussoir)
    pinMode(3, INPUT_PULLUP);           // Entrée avec résistance de pull-up interne
    pinMode(A0, INPUT);                 // Entrée analogique (ADC 10 bits)

    // Sorties avec état initial
    digitalWrite(LED_BUILTIN, LOW);
}

void loop() {
    // Lecture d'un bouton (pull-up interne : LOW = appuyé)
    bool bouton = digitalRead(3);
    digitalWrite(8, bouton ? HIGH : LOW);

    // Lecture analogique (0-1023 sur AVR 10 bits)
    int valeur = analogRead(A0);
    float tension = valeur * (5.0 / 1023.0);

    // Sortie PWM (0-255 pour AVR 8 bits)
    int pwm = map(valeur, 0, 1023, 0, 255);
    analogWrite(9, pwm);

    delay(50);
}
```

### 2.2 Gestion du temps

```cpp
void loop() {
    // 1. delay() — bloquant, à éviter pour les tâches multiples
    // delay(1000);

    // 2. millis() — non bloquant, recommandé
    static unsigned long dernier_appel = 0;
    const unsigned long interval = 1000;  // 1 seconde

    unsigned long maintenant = millis();
    if (maintenant - dernier_appel >= interval) {
        dernier_appel = maintenant;
        // Action périodique ici
        digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
    }

    // 3. micros() pour les temporisations précises
    static unsigned long dernier_us = 0;
    if (micros() - dernier_us >= 500) {  // 500 µs
        dernier_us = micros();
        // Traitement haute fréquence
    }
}
```

### 2.3 Interruptions externes

```cpp
// Compteur d'impulsions avec interruption
volatile unsigned long impulsion_count = 0;
const byte interrupt_pin = 2;  // Arduino Uno : INT0 = pin 2, INT1 = pin 3

void setup() {
    Serial.begin(115200);

    // Interruption sur front montant
    attachInterrupt(digitalPinToInterrupt(interrupt_pin),
                    compteur_impulsion, RISING);
}

void compteur_impulsion() {
    impulsion_count++;  // Volatile car modifiée dans l'ISR
}

void loop() {
    // Affichage toutes les secondes
    static unsigned long last_display = 0;
    if (millis() - last_display >= 1000) {
        last_display = millis();
        Serial.print("Fréquence : ");
        Serial.print(impulsion_count);
        Serial.println(" Hz");
        impulsion_count = 0;
    }
}
```

---

## 3. Protocoles de Communication

### 3.1 UART (Série)

```cpp
void setup() {
    Serial.begin(115200);         // Console de debug
    Serial1.begin(9600);          // Port série matériel 1 (pins RX1/TX1)
}

void loop() {
    // Lecture de données série
    if (Serial.available() > 0) {
        String data = Serial.readStringUntil('\n');
        Serial1.println(data);    // Relai vers Serial1
    }

    if (Serial1.available() > 0) {
        int val = Serial1.parseInt();
        // Traitement
    }
}

// Format de trame recommandé
// CSV simple : "TEMP,23.5,HUM,65.2\r\n"
// JSON compact : {"t":23.5,"h":65.2}\n
// Binaire : 0xAA 0x01 <LSB> <MSB> <CRC> (plus efficace)
```

### 3.2 I²C (Wire)

```cpp
#include <Wire.h>

#define BMP280_ADDR 0x76  // Adresse I²C du BMP280

void setup() {
    Wire.begin();           // Maître I²C
    Serial.begin(115200);
}

// Lecture d'un registre I²C
uint8_t read_reg_i2c(uint8_t addr, uint8_t reg) {
    Wire.beginTransmission(addr);
    Wire.write(reg);
    Wire.endTransmission(false);  // Restart condition

    Wire.requestFrom(addr, (uint8_t)1);
    if (Wire.available()) {
        return Wire.read();
    }
    return 0;
}

float read_bmp280_temperature() {
    uint8_t msb = read_reg_i2c(BMP280_ADDR, 0xFA);
    uint8_t lsb = read_reg_i2c(BMP280_ADDR, 0xFB);
    uint8_t xlsb = read_reg_i2c(BMP280_ADDR, 0xFC);

    int32_t adc = (msb << 12) | (lsb << 4) | (xlsb >> 4);
    return adc / 100.0;  // Simplifié
}
```

### 3.3 SPI

```cpp
#include <SPI.h>

#define CS_PIN 10  // Chip Select

void setup() {
    pinMode(CS_PIN, OUTPUT);
    digitalWrite(CS_PIN, HIGH);     // Désélectionné par défaut
    SPI.begin();                    // SCK=13, MOSI=11, MISO=12
    SPI.beginTransaction(SPISettings(4000000, MSBFIRST, SPI_MODE0));
}

// Lecture d'un registre SPI (mode 16 bits : commande + donnée)
uint16_t read_spi_register(uint8_t reg) {
    digitalWrite(CS_PIN, LOW);
    SPI.transfer(reg);              // Envoie l'adresse du registre
    uint16_t value = SPI.transfer16(0x0000);  // Lecture 16 bits
    digitalWrite(CS_PIN, HIGH);
    return value;
}
```

### 3.4 Modbus RTU sur RS-485

```cpp
#include <ModbusMaster.h>

#define RS485_DE 4   // Driver Enable (DE/RE sur MAX485)
#define RS485_RE 5   // Receiver Enable (RE, actif bas)

ModbusMaster node;

void setup() {
    pinMode(RS485_DE, OUTPUT);
    pinMode(RS485_RE, OUTPUT);
    digitalWrite(RS485_DE, LOW);    // Réception par défaut
    digitalWrite(RS485_RE, LOW);

    Serial1.begin(9600, SERIAL_8N1);  // Modbus RTU : 9600 bauds, 8N1
    node.begin(1, Serial1);           // ID esclave = 1
}

void loop() {
    // Lecture du registre holding 40001 (adresse 0)
    uint8_t result = node.readHoldingRegisters(0, 1);
    if (result == node.ku8MBSuccess) {
        float valeur = node.getResponseBuffer(0) / 100.0;
        Serial.print("Valeur capteur : ");
        Serial.println(valeur);
    } else {
        Serial.print("Erreur Modbus : 0x");
        Serial.println(result, HEX);
    }
    delay(100);
}
```

---

## 4. Capteurs et Actionneurs

### 4.1 Capteurs de température

```cpp
// DS18B20 (OneWire)
#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

void setup() {
    Serial.begin(115200);
    sensors.begin();
    sensors.setResolution(12);  // 12 bits = 0.0625 °C
}

void loop() {
    sensors.requestTemperatures();
    float temp = sensors.getTempCByIndex(0);
    Serial.print("Température : ");
    Serial.print(temp);
    Serial.println(" °C");
    delay(1000);
}
```

### 4.2 Contrôle de servomoteurs

```cpp
#include <Servo.h>

Servo mon_servo;
const int servo_pin = 9;

void setup() {
    mon_servo.attach(servo_pin, 544, 2400);  // pulse min/max µs
    mon_servo.write(90);                      // Position neutre (90°)
}

void loop() {
    // Balayage aller-retour
    for (int angle = 0; angle <= 180; angle += 1) {
        mon_servo.write(angle);
        delay(15);  // 15 ms par degré = ~2,7 s pour 180°
    }
    for (int angle = 180; angle >= 0; angle -= 1) {
        mon_servo.write(angle);
        delay(15);
    }
}
```

### 4.3 Moteur pas-à-pas (stepper) avec driver A4988

```cpp
#define STEP_PIN 3
#define DIR_PIN 2
#define ENABLE_PIN 4

void setup() {
    pinMode(STEP_PIN, OUTPUT);
    pinMode(DIR_PIN, OUTPUT);
    pinMode(ENABLE_PIN, OUTPUT);
    digitalWrite(ENABLE_PIN, LOW);  // Activer le driver
}

void loop() {
    // 200 pas/tour, driver en 1/16 micro-pas = 3200 pas/tour
    digitalWrite(DIR_PIN, HIGH);    // Sens horaire

    for (int i = 0; i < 3200; i++) {
        digitalWrite(STEP_PIN, HIGH);
        delayMicroseconds(2000);    // 500 pas/s
        digitalWrite(STEP_PIN, LOW);
        delayMicroseconds(2000);
    }
    delay(1000);

    digitalWrite(DIR_PIN, LOW);     // Sens anti-horaire
    for (int i = 0; i < 3200; i++) {
        digitalWrite(STEP_PIN, HIGH);
        delayMicroseconds(2000);
        digitalWrite(STEP_PIN, LOW);
        delayMicroseconds(2000);
    }
    delay(1000);
}
```

---

## 5. Optimisation Mémoire (AVR 8 bits)

### 5.1 Utilisation de la mémoire

```cpp
// Les AVR ATMega328P ont 32 KB Flash et 2 KB RAM.
// Limiter l'utilisation de la RAM est critique.

// Bon : stockage en Flash (PROGMEM)
#include <avr/pgmspace.h>
const char long_message[] PROGMEM = "Ce message est stocké en Flash, pas en RAM.";

// Mauvais : stockage en RAM (copie à chaque appel)
// const char* long_message = "Ce message occupe de la RAM.";

// Lecture depuis la Flash
void print_from_flash() {
    char buffer[32];
    strcpy_P(buffer, long_message);  // Copie dans un buffer temporaire
    Serial.println(buffer);
}

// Éviter String (allocation dynamique, fragmentation)
// Préférer char[] avec snprintf_P
char buffer[64];
snprintf_P(buffer, sizeof(buffer),
           PSTR("Température : %d.%d °C"), temp / 100, temp % 100);
```

### 5.2 Consommation mémoire par type

| Type | Taille (AVR) | Usage |
|:---|---:|:---|
| `bool` | 1 octet | Drapeaux |
| `char` | 1 octet | Caractères, petits entiers |
| `int` | 2 octets | Entier standard AVR (attention : 16 bits !) |
| `unsigned int` | 2 octets | 0 à 65535 |
| `long` | 4 octets | Grands entiers |
| `float` | 4 octets | Nombres à virgule (éviter si possible) |
| `String` | variable | Fragmentation mémoire, à proscrire |

---

## Pièges Courants

1. **Utilisation de `delay()` dans un programme avec plusieurs capteurs :** `delay()` bloque tout le programme. Utiliser `millis()` non bloquant pour des tâches multiples.

2. **String + concaténation :** `String msg = "Valeur: " + String(val);` fragmente la RAM. Utiliser `snprintf()` avec un buffer fixe.

3. **Tensions incompatibles :** Un capteur 5 V connecté à une broche 3,3 V d'un Arduino peut le détruire. Vérifier la logique de tension de la carte (Uno = 5 V, Zero/MKR = 3,3 V).

4. **Courant de sortie excessif :** Les broches GPIO des AVR peuvent fournir ~20 mA max. Un relais 5 V/100 mA nécessite un transistor (2N2222, MOSFET) ou un driver (ULN2003).

5. **Bruit sur les entrées analogiques :** Les entrées ADC sont sensibles au bruit. Utiliser `analogReference()` avec une référence externe stable ou ajouter un condensateur 100 nF entre AREF et GND.

6. **Watchdog non configuré :** Pour les systèmes autonomes, activer le watchdog interne (librairie `<avr/wdt.h>`, `wdt_enable(WDTO_2S)`) avec `wdt_reset()` dans `loop()`.

7. **Pull-up manquant sur les entrées :** Une broche d'entrée flottante (pas de pull-up interne activé, pas de résistance externe) capte les parasites et donne des lectures aléatoires. Utiliser `INPUT_PULLUP` ou une résistance externe de 10 kΩ.

---

## Liste de vérification (Checklist)

- [ ] Le bon cœur (AVR/SAMD/RP2040) et le bon FQBN sont sélectionnés pour la carte.
- [ ] Les broches sont correctement configurées (INPUT/OUTPUT/INPUT_PULLUP).
- [ ] Aucune fonction bloquante (delay) n'empêche la lecture d'autres capteurs.
- [ ] La RAM utilisée est inférieure à 80 % de la RAM totale (vérifier à la compilation).
- [ ] Les communications série ont des débits en bauds cohérents.
- [ ] Les résistances de tirage I²C sont présentes (si plusieurs périphériques, 4,7 kΩ).
- [ ] Les modules RS-485 ont le contrôle DE/RE correct pour Modbus.
- [ ] Le watchdog est activé pour les déploiements autonomes.
- [ ] Les tensions d'alimentation des capteurs et actionneurs sont compatibles.
- [ ] Les interruptions ne contiennent aucun appel bloquant (delay, Serial.print).