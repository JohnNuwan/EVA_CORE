---
name: "embedded-communication-protocols"
description: "Protocoles de communication embarquée — UART, I2C, SPI, I2S, CAN, LIN, 1-Wire, protocole implémentation"
category: "edge-ai"
author: "E.V.A"
version: "1.0.0"
---

# Protocoles de Communication Embarquée

## Vue d'ensemble

Protocoles filaires pour systèmes embarqués : UART, I2C, SPI, I2S, CAN, LIN, 1-Wire. Implémentation bare-metal, timings, topologies, erreurs typiques, et optimisation.

## UART (Universal Asynchronous Receiver-Transmitter)

### Spécifications

```
Topologie : Point-à-point (peer-to-peer)
Signaux  : TX (transmit), RX (receive), [RTS, CTS]
Vitesse  : 300 bps - 4 Mbps (typ. 9600, 115200, 921600)
Bits     : Start(1) + Data(5-9) + Parity(0/1) + Stop(1-2)
Tension  : RS-232 (±12V), TTL (3.3V/5V), RS-485 (différentiel)
```

### Format de trame

```
IDLE    START   D0   D1   D2   D3   D4   D5   D6   D7   PARITY  STOP
  ──┐  ┌──┐  ┌──┐  ┌──┐  ┌──┐  ┌──┐  ┌──┐  ┌──┐  ┌──┐  ┌──┐  ┌──┐
    │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │
    └──┘  └──┘  └──┘  └──┘  └──┘  └──┘  └──┘  └──┘  └──┘  └──┘  └──
```

### Implémentation Bare-Metal (Polling)

```c
// USART2 — STM32F4, 115200 baud, 8N1
void uart_init(uint32_t baud) {
    // Activer clocks
    RCC->APB1ENR |= RCC_APB1ENR_USART2EN;
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;

    // GPIO PA2=TX, PA3=RX (AF7)
    GPIOA->MODER  &= ~(3 << 4) | ~(3 << 6);
    GPIOA->MODER  |= (2 << 4) | (2 << 6);   // Alternate function
    GPIOA->AFR[0] |= (7 << 8) | (7 << 12);  // AF7 USART2

    // USART config
    uint32_t usartdiv = (SystemCoreClock / 2) / baud;  // APB1 = 42MHz
    USART2->BRR = usartdiv;
    USART2->CR1 = USART_CR1_UE | USART_CR1_TE | USART_CR1_RE;
}

void uart_putc(char c) {
    while (!(USART2->SR & USART_SR_TXE));
    USART2->DR = c;
}

char uart_getc(void) {
    while (!(USART2->SR & USART_SR_RXNE));
    return USART2->DR;
}

void uart_puts(const char *s) {
    while (*s) uart_putc(*s++);
}

// IRQ version
void USART2_IRQHandler(void) {
    if (USART2->SR & USART_SR_RXNE) {
        uint8_t byte = (uint8_t)USART2->DR;
        ringbuf_put(&uart_rx_ring, byte);
    }
    if (USART2->SR & USART_SR_TXE) {
        if (ringbuf_get(&uart_tx_ring, &tx_byte))
            USART2->DR = tx_byte;
        else
            USART2->CR1 &= ~USART_CR1_TXEIE;  // Désactiver TX IRQ
    }
}
```

### RS-485 (Half-duplex)

```c
// RS-485 : DE/RE pin controle le transceiver
void rs485_send(const uint8_t *data, uint32_t len) {
    GPIO_SetPin(DE_PIN);   // Enable driver
    delay_us(5);           // Attendre stabilisation driver
    for (uint32_t i = 0; i < len; i++) uart_putc(data[i]);
    while (!(USART2->SR & USART_SR_TC));  // Attendre transmission complète
    delay_us(5);           // Dernier bit transmis
    GPIO_ClearPin(DE_PIN); // Disable driver, enable receiver
}
```

## I2C (Inter-Integrated Circuit)

### Spécifications

```
Topologie : Bus multi-maître, 2 fils + pull-up
Signaux  : SDA (data), SCL (clock)
Vitesse  : Standard (100kHz), Fast (400kHz), Fast+ (1MHz), HS (3.4MHz)
Adresses : 7-bit (128 devices) ou 10-bit
Charge   : 400pF max (bus capacitance)
Tension  : 1.2V - 5V (pull-up vers VCC)
```

### Format de trame

```
┌──────┐     ┌──────┐                ┌──────┐
│ START│     │ ADDR │     ┌──────┐    │ STOP │
│  SDA │     │ 7bit │  W  │ ACK  │    │  SDA │
│  ↓1  │     │      │  ↓  │      │    │  ↑1  │
└──────┘     └──────┘  └──┘ └──────┘    └──────┘
                               DATA (8-bit)
```

### Implémentation Bit-banging

```c
// I2C bit-bang (n'importe quels GPIO)
#define I2C_DELAY() delay_us(5)  // ~100kHz

void i2c_start(void) {
    SDA_OUT(); SDA_HIGH(); SCL_HIGH(); I2C_DELAY();
    SDA_LOW();  I2C_DELAY();
    SCL_LOW();
}

void i2c_stop(void) {
    SDA_LOW();  SCL_HIGH(); I2C_DELAY();
    SDA_HIGH(); I2C_DELAY();
}

void i2c_ack(void) {
    SDA_LOW();  SCL_HIGH(); I2C_DELAY(); SCL_LOW();
}

void i2c_nack(void) {
    SDA_HIGH(); SCL_HIGH(); I2C_DELAY(); SCL_LOW();
}

bool i2c_write_byte(uint8_t byte) {
    for (int i = 0; i < 8; i++) {
        if (byte & 0x80) SDA_HIGH(); else SDA_LOW();
        byte <<= 1;
        SCL_HIGH(); I2C_DELAY(); SCL_LOW();
    }
    SDA_IN();  // Release SDA pour ACK
    SCL_HIGH(); I2C_DELAY();
    bool ack = SDA_READ();  // 0 = ACK, 1 = NACK
    SCL_LOW();
    SDA_OUT();
    return !ack;
}

uint8_t i2c_read_byte(bool ack) {
    uint8_t data = 0;
    SDA_IN();
    for (int i = 0; i < 8; i++) {
        data <<= 1;
        SCL_HIGH(); I2C_DELAY();
        if (SDA_READ()) data |= 1;
        SCL_LOW(); I2C_DELAY();
    }
    SDA_OUT();
    if (ack) i2c_ack(); else i2c_nack();
    return data;
}

// Transaction complète
bool i2c_write_reg(uint8_t dev_addr, uint8_t reg, uint8_t data) {
    i2c_start();
    if (!i2c_write_byte(dev_addr << 1 | 0)) { i2c_stop(); return false; }
    if (!i2c_write_byte(reg)) { i2c_stop(); return false; }
    if (!i2c_write_byte(data)) { i2c_stop(); return false; }
    i2c_stop();
    return true;
}
```

### I2C périphérique (STM32 HAL)

```c
// Utilisation du périphérique I2C matériel
#define I2C_TIMEOUT 100  // ms

HAL_StatusTypeDef i2c_mem_write(I2C_HandleTypeDef *hi2c,
    uint16_t dev_addr, uint16_t mem_addr, uint16_t mem_size,
    uint8_t *data, uint16_t size) {

    return HAL_I2C_Mem_Write(hi2c, dev_addr << 1,
        mem_addr, mem_size, data, size, I2C_TIMEOUT);
}

HAL_StatusTypeDef i2c_mem_read(I2C_HandleTypeDef *hi2c,
    uint16_t dev_addr, uint16_t mem_addr, uint16_t mem_size,
    uint8_t *data, uint16_t size) {

    return HAL_I2C_Mem_Read(hi2c, dev_addr << 1,
        mem_addr, mem_size, data, size, I2C_TIMEOUT);
}
```

## SPI (Serial Peripheral Interface)

### Spécifications

```
Topologie : Maître ↔ Esclave(s), 4 fils
Signaux  : MOSI (Master Out), MISO (Master In), SCK (Clock), SS (Slave Select)
Vitesse  : Jusqu'à 80 MHz (typ. 1-40 MHz)
Modes    : CPOL=0/1, CPHA=0/1 (4 modes d'horloge)
Daisy-chain : Possible (SS unique + données qui circulent)
```

### Modes SPI

```
Mode  CPOL  CPHA  Échantillonnage
 0     0     0    Front montant (rising edge)
 1     0     1    Front descendant (falling edge)
 2     1     0    Front descendant
 3     1     1    Front montant
```

### Implémentation Bit-banging

```c
// SPI mode 0 (CPOL=0, CPHA=0)
uint8_t spi_transfer(uint8_t tx_byte) {
    uint8_t rx_byte = 0;
    for (int i = 0; i < 8; i++) {
        // Mettre MOSI
        if (tx_byte & 0x80) MOSI_HIGH(); else MOSI_LOW();
        tx_byte <<= 1;

        // SCK rising → échantillonner MISO
        SCK_HIGH(); delay_us(1);
        rx_byte = (rx_byte << 1) | MISO_READ();
        SCK_LOW(); delay_us(1);
    }
    return rx_byte;
}

// Transaction multi-octets
void spi_transfer_buf(const uint8_t *tx, uint8_t *rx, uint32_t len) {
    for (uint32_t i = 0; i < len; i++) {
        rx[i] = spi_transfer(tx ? tx[i] : 0x00);
    }
}
```

### SPI DMA (haute vitesse)

```c
// SPI2 + DMA2 Stream 3 (TX) et Stream 0 (RX) — STM32F4
void spi_dma_transfer(uint8_t *tx_buf, uint8_t *rx_buf, uint32_t len) {
    // Désactiver SPI
    SPI2->CR1 &= ~SPI_CR1_SPE;

    // Configurer DMA TX
    DMA2_Stream3->CR = 0;  // Reset
    DMA2_Stream3->PAR = (uint32_t)&SPI2->DR;
    DMA2_Stream3->M0AR = (uint32_t)tx_buf;
    DMA2_Stream3->NDTR = len;
    DMA2_Stream3->CR = DMA_SxCR_CHSEL_3 | DMA_SxCR_DIR_0 |  // Mem→Periph
                       DMA_SxCR_MINC | DMA_SxCR_TCIE;

    // Configurer DMA RX
    DMA2_Stream0->CR = 0;
    DMA2_Stream0->PAR = (uint32_t)&SPI2->DR;
    DMA2_Stream0->M0AR = (uint32_t)rx_buf;
    DMA2_Stream0->NDTR = len;
    DMA2_Stream0->CR = DMA_SxCR_CHSEL_3 |  // Periph→Mem
                       DMA_SxCR_MINC | DMA_SxCR_TCIE;

    // Activer DMA
    DMA2_Stream3->CR |= DMA_SxCR_EN;
    DMA2_Stream0->CR |= DMA_SxCR_EN;

    // Activer SPI
    SPI2->CR2 |= SPI_CR2_TXDMAEN | SPI_CR2_RXDMAEN;
    SPI2->CR1 |= SPI_CR1_SPE;
}
```

## I2S (Inter-IC Sound)

### Spécifications

```
Topologie : Point-à-point, audio numérique
Signaux  : SD (data), WS (word select), CK (clock), [MCK (master clock)]
Vitesse  : Jusqu'à 192 kHz × 32 bits × 2 canaux = 12.288 MHz
Formats  : I2S (MSB-first), Left-justified, PCM, TDM
Standards: Philips I2S, Left-Justified, Right-Justified, DSP
```

### Format I2S Philips

```
WS=0 → Left channel, WS=1 → Right channel
┌──────────────┐ ┌──────────────┐
│  LEFT CH     │ │  RIGHT CH    │
│ MSB ← LSB    │ │ MSB ← LSB    │
└──────────────┘ └──────────────┘
```

## CAN (Controller Area Network)

### Spécifications

```
Topologie : Bus multi-maître, 2 fils différentiels
Signaux  : CAN_H, CAN_L
Vitesse  : 125 kbps - 1 Mbps (CAN 2.0), jusqu'à 8 Mbps (CAN FD)
Trames   : Standard (11-bit ID), Extended (29-bit ID)
Terminaison : 120Ω aux deux extrémités
Longueur : 40m @ 1 Mbps, 500m @ 125 kbps
```

### Trame CAN 2.0A

```
┌──────────────┬─────────┬──────────┬────────┬──────────┬──────────┐
│ SOF (1)      │ ID (11) │ RTR (1)  │ DLC (4)│ Data (0..64)│ CRC (15) │ ACK (2) │ EOF (7) │
└──────────────┴─────────┴──────────┴────────┴──────────┴──────────┘
```

### Implémentation CAN (STM32 bxCAN)

```c
// STM32F4 bxCAN — 1Mbps, 16 filters
void can_init(void) {
    // Activer clock
    RCC->APB1ENR |= RCC_APB1ENR_CAN1EN;
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOBEN;

    // GPIO PB8=RX, PB9=TX (AF9)
    GPIOB->MODER  |= (2 << 16) | (2 << 18);  // AF
    GPIOB->AFR[1] |= (9 << 0) | (9 << 4);    // AF9 CAN

    // CAN config
    CAN1->MCR = CAN_MCR_INRQ;  // Initialization mode
    while (!(CAN1->MSR & CAN_MSR_INAK));

    // Bit timing @ 42MHz APB1, 1Mbps
    // BS1=9, BS2=6, SJW=1, Prescaler=2
    // tq = 2 × 1/42MHz = 47.6ns
    // 1 bit = 1 + 9 + 6 = 16 tq = 762ns → ~1.31MHz
    CAN1->BTR = (1 << 0) |    // SJW = 1
                (6 << 4) |    // BS2 = 6
                (9 << 8) |    // BS1 = 9
                (2 << 16);    // Prescaler = 2

    // Activer des filtres (banque 0, 32-bit, standard)
    CAN1->FMR |= CAN_FMR_FINIT;  // Init filter mode
    CAN1->sFilterRegister[0].FR1 = 0x00000000;  // ID mask
    CAN1->sFilterRegister[0].FR2 = 0x00000000;  // Accept all
    CAN1->FA1R |= CAN_FA1R_FACT0;  // Activer filtre 0
    CAN1->FMR &= ~CAN_FMR_FINIT;   // Quit init mode

    // Normal mode
    CAN1->MCR &= ~CAN_MCR_INRQ;
    while (CAN1->MSR & CAN_MSR_INAK);
}

// Envoyer trame
bool can_send(uint32_t id, uint8_t *data, uint8_t len) {
    uint32_t mailbox = CAN1->TSR & CAN_TSR_TME0 ? 0 :
                       CAN1->TSR & CAN_TSR_TME1 ? 1 :
                       CAN1->TSR & CAN_TSR_TME2 ? 2 : 3;
    if (mailbox == 3) return false;  // No mailbox

    CAN1->sTxMailBox[mailbox].TIR = (id << 21) | CAN_TI0R_TXRQ;
    CAN1->sTxMailBox[mailbox].TDTR = len;
    CAN1->sTxMailBox[mailbox].TDLR = data[0] | (data[1] << 8) |
                                      (data[2] << 16) | (data[3] << 24);
    CAN1->sTxMailBox[mailbox].TDHR = data[4] | (data[5] << 8) |
                                      (data[6] << 16) | (data[7] << 24);
    return true;
}
```

## LIN (Local Interconnect Network)

### Spécifications

```
Topologie : Maître ↔ Esclave(s), 1 fil
Signaux  : LIN bus (sur UART, 1 fil + GND)
Vitesse  : 1 kbps - 20 kbps (typ. 19.2 kbps)
Trames   : 8 octets de données, ID 6-bit
Voltages : 12V (batterie)
Basé sur : UART/SCI (Serial Communication Interface)
```

### Trame LIN

```
┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│ BREAK    │ SYNC     │ ID (PID)  │ DATA (8)  │ CRC      │          │
│ 13 bits  │ 0x55     │ 6-bit+par │ max 8    │ 8-bit    │          │
│ (maître) │          │          │          │          │          │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

## 1-Wire (Dallas / Maxim)

### Spécifications

```
Topologie : Bus, 1 fil + GND (parasite power possible)
Signaux  : DQ (data), GND
Vitesse  : Standard (15.4 kbps), Overdrive (125 kbps)
Devices  : DS18B20 (température), DS2431 (EEPROM), iButton
Longueur : 100m max (standard), 10m (parasite)
```

### Timing 1-Wire

```c
// Reset et présence
bool ow_reset(void) {
    DQ_LOW(); delay_us(480);  // Reset pulse
    DQ_IN();  delay_us(70);   // Release + wait
    bool present = !DQ_READ(); // 0 = device présent
    delay_us(410);            // Pull-up recovery
    return present;
}

// Write bit
void ow_write_bit(bool bit) {
    DQ_LOW();
    delay_us(bit ? 1 : 60);  // 1=1µs, 0=60µs
    if (bit) DQ_HIGH(); else DQ_LOW();
    delay_us(bit ? 60 : 10);  // Slot restant
    DQ_HIGH();
}

// Read bit
bool ow_read_bit(void) {
    bool bit;
    DQ_LOW(); delay_us(2);    // Read slot
    DQ_IN();  delay_us(10);   // Échantillonner
    bit = DQ_READ();
    delay_us(50);             // Slot restant
    DQ_OUT(); DQ_HIGH();
    return bit;
}
```

## Comparatif des Protocoles

| Protocole | Fils | Vitesse max | Distance | Topologie | Adressage | CRC |
|-----------|------|------------|----------|-----------|-----------|-----|
| UART      | 2    | 4 Mbps     | 1.5m TTL, 1.2km RS-485 | Point-à-point | Aucun | Optionnel |
| I2C       | 2    | 3.4 MHz    | 1m       | Bus multi-maître | 7/10-bit | Non |
| SPI       | 4    | 80 MHz     | 1m       | Maître-esclave | SS (chip select) | Non |
| I2S       | 3    | 12 MHz     | 0.5m     | Point-à-point | WS (canal) | Non |
| CAN       | 2    | 1 Mbps     | 40m@1M, 500m@125k | Bus multi-maître | 11/29-bit | Oui (15-bit) |
| LIN       | 1    | 20 kbps    | 40m      | Maître-esclave | 6-bit ID | Oui (8-bit) |
| 1-Wire    | 1    | 125 kbps   | 100m     | Bus | ROM 64-bit | Oui (8-bit) |

## Pitfalls

1. **UART baud rate error** : Max 2% d'erreur — bien calculer BRR avec les horloges réelles
2. **I2C bus lock** : SDA bloqué à 0 si un esclave n'a pas fini — reset avec 9 pulses SCL
3. **SPI mode mismatch** : Maître et esclave doivent avoir le même CPOL/CPHA
4. **I2C pull-up** : Trop fort → signaux ronds (lent), trop faible → pas de signal
5. **CAN ACK** : Chaque nœud ACK dans le champ ACK — si pas d'ACK, l'émetteur retransmet
6. **CAN bit timing** : mal configuré → erreurs de synchronisation, trames perdues
7. **1-Wire parasite power** : Le device tire l'énergie du bus — nécessite strong pull-up
8. **RS-485 direction** : Le délai de commutation DE/RE doit être mesuré (5µs typique)
9. **SPI CS** : Certains esclaves exigent CS haut entre les octets (latch)

## Ressources

- I2C Bus Specification : https://www.nxp.com/docs/en/user-guide/UM10204.pdf
- SPI Block Guide : https://www.motorola.com/files/microcontrollers/doc/ref_manual/SPIRM.pdf
- CAN 2.0 Specification : https://www.can-cia.org/
- LIN Specification Package : https://www.lin-cia.org/
- 1-Wire Application Note : https://www.analog.com/en/technical-articles/1wire-communication-through-software.html