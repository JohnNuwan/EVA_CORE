---
name: fpga-verilog-vhdl
description: "Programmer des FPGA avec Verilog et VHDL — logique combinatoire et séquentielle, machines d'état, traitement numérique (DSP), interfaces (SPI, I²C, UART, AXI), simulation et synthèse."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [fpga, verilog, vhdl, logique-programmable, rtl, synthèse, simulation, vivado, quartus, icestorm, yosys, nextpnr, dsp, axi, spi, i2c, uart, pcie, sérielle, sdf, timing, contrainte, xilinx, intel, lattice]
    related_skills: [signal-processing-digital, pcb-design-electronique, embedded-systems-firmware, electronique-analogique]
---

# Programmation FPGA (Verilog / VHDL)

## Vue d'ensemble

Un FPGA (Field-Programmable Gate Array) est un circuit intégré logique programmable dont la configuration peut être modifiée après fabrication. Contrairement à un microcontrôleur (exécution séquentielle d'instructions), un FPGA implémente des circuits matériels parallèles qui fonctionnent à la vitesse des horloges. Cette compétence couvre la conception en langage de description matérielle (HDL), la simulation, la synthèse, le placement-routage et le déploiement sur FPGA.

### Paradigme : CPU vs FPGA

```
CPU (séquentiel) :
┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐
│ Instr │→│ Instr │→│ Instr │→│ Instr │→ ...
│   A   │  │   B   │  │   C   │  │   D   │
└───────┘  └───────┘  └───────┘  └───────┘
  Temps → t1          t2          t3          t4

FPGA (parallèle) :
┌───────┐ ──────────────────────────────────────► Sortie A
│ Bloc  │  (opération indépendante)
│  A    │
└───────┘
┌───────┐ ──────────────────────────────────────► Sortie B
│ Bloc  │
│  B    │
└───────┘
┌───────┐ ──────────────────────────────────────► Sortie C
│ Bloc  │
│  C    │
└───────┘
  Temps → t1 (les trois blocs s'exécutent simultanément)
```

### Familles FPGA courantes

| Fabricant | Série | Logiciel | Prix | Usage |
|:---|---|---:|---:|
| **Xilinx (AMD)** | Artix-7, Kintex, Virtex, Zynq (ARM+FPGA) | Vivado / ISE | $$-$$$$ | Professionnel, hautes performances |
| **Intel (Altera)** | Cyclone, MAX, Arria, Stratix | Quartus Prime | $$-$$$$ | Professionnel, faible consommation |
| **Lattice** | iCE40, ECP5, CrossLink | Lattice Diamond, nextpnr | $-$$ | Prototypage, faible coût, open source |
| **Gowin** | GW1N, GW2A | Gowin EDA | $ | Entrée de gamme, chinois |
| **QuickLogic** | EOS S3 | Symbiflow | $ | IoT, sensor hub |

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Concevoir un circuit numérique en Verilog ou VHDL pour un FPGA.
- Implémenter une interface de communication personnalisée (SPI, I²C, UART, AXI, PCIe, DDR).
- Créer un processeur de signal numérique haute vitesse (filtre FIR parallélisé, FFT pipeline, corrélation).
- Accélérer un algorithme par matériel (hardware acceleration) — vision, cryptographie, réseau.
- Synchroniser des signaux asynchrones (métastabilité) et gérer des domaines d'horloge multiples (CDC).
- Contrôler des périphériques haute vitesse (caméra MIPI, écran HDMI, ADC/DAC RF, Ethernet 10 GbE).
- Simuler et vérifier formellement un design RTL avant synthèse.
- Utiliser les outils open source : Yosys (synthèse), Verilator (simulation), nextpnr (placement-routage).

Ne pas utiliser pour : du développement logiciel séquentiel (utiliser un microcontrôleur), des algorithmes qui bénéficient d'une exécution en pipeline sur CPU (GPU), des tâches qui tiennent sur un microcontrôleur bas coût.

---

## 1. Fondamentaux du HDL

### 1.1 Verilog vs VHDL — Comparaison

| Critère | Verilog (IEEE 1364) | VHDL (IEEE 1076) |
|:---|---|---|
| **Syntaxe** | Proche du C | Proche d'Ada/Pascal |
| **Typage** | Faible, permissif | Fort, très strict |
| **Construction** | `module` / `endmodule` | `entity` / `architecture` |
| **Concurrence** | `always @(posedge clk)` | `process(clk)` |
| **Signaux** | `wire`, `reg` | `signal`, `variable` |
| **Génériques** | `parameter` | `generic` |
| **IP** | Très abondant | Standard militaire/aéro |
| **Apprentissage** | Plus facile | Plus rigoureux |

### 1.2 Structure de base (Verilog)

```verilog
// ─── Module basique : bascule D (D flip-flop) ───
module d_flip_flop (
    input  wire       clk,    // Horloge
    input  wire       rst_n,  // Reset asynchrone, actif bas
    input  wire       d,      // Entrée de données
    output reg        q,      // Sortie
    output reg        q_n     // Sortie inversée
);

    // Bloc séquentiel : sensible au front montant de l'horloge
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            q   <= 1'b0;      // Reset : q = 0
            q_n <= 1'b1;      // Reset : q_n = 1
        end else begin
            q   <= d;          // Recopie synchrone de d sur q
            q_n <= ~d;         // Sortie inversée
        end
    end
endmodule
```

### 1.3 Structure de base (VHDL)

```vhdl
-- ─── Module basique : bascule D (D flip-flop) ───
library ieee;
use ieee.std_logic_1164.all;

entity d_flip_flop is
    port (
        clk   : in  std_logic;      -- Horloge
        rst_n : in  std_logic;      -- Reset asynchrone, actif bas
        d     : in  std_logic;      -- Entrée
        q     : out std_logic;      -- Sortie
        q_n   : out std_logic       -- Sortie inversée
    );
end entity;

architecture rtl of d_flip_flop is
begin
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            q   <= '0';
            q_n <= '1';
        elsif rising_edge(clk) then
            q   <= d;
            q_n <= not d;
        end if;
    end process;
end architecture;
```

### 1.4 Types de données et assignations

```verilog
// Verilog : types de base
wire a;                 // Fil simple (combinatoire)
reg  b;                 // Registre (séquentiel ou combinatoire)
wire [7:0] bus_c;      // Bus 8 bits
reg  [31:0] counter;   // Compteur 32 bits

// Assignations
assign a = b & c;       // Assignation continue (combinatoire)
always @(*) begin       // Bloc combinatoire (tout signal sensible)
    b = a | c;          // Assignation bloquante (=) — exécution séquentielle
end
always @(posedge clk) begin
    counter <= counter + 1;  // Assignation non-bloquante (<=) — parallèle
end
```

---

## 2. Logique Combinatoire et Séquentielle

### 2.1 Opérateurs combinatoires

```verilog
module alu_8bit (
    input  wire [7:0] a, b,
    input  wire [2:0] op,       // Opcode : 000 = ADD, 001 = SUB, etc.
    output reg  [7:0] result,
    output reg        carry,    // Retenue
    output reg        zero      // Flag zéro
);

    always @(*) begin
        case (op)
            3'b000: {carry, result} = a + b;           // Addition
            3'b001: {carry, result} = a - b;           // Soustraction
            3'b010: result = a & b;                    // ET logique
            3'b011: result = a | b;                    // OU logique
            3'b100: result = a ^ b;                    // XOR
            3'b101: result = a << b[2:0];              // Décalage gauche
            3'b110: result = a >> b[2:0];              // Décalage droite
            default: result = 8'b0;
        endcase
        zero = (result == 8'b0);
    end
endmodule
```

### 2.2 Compteurs et diviseurs de fréquence

```verilog
// ─── Compteur modulo N avec enable ───
module counter_n (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        enable,      // Active le comptage
    output reg  [15:0] count,       // Valeur du compteur
    output reg         overflow     // Flag quand count atteint N-1
);

    parameter N = 50000;  // Module du compteur

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            count    <= 16'b0;
            overflow <= 1'b0;
        end else if (enable) begin
            if (count == N - 1) begin
                count    <= 16'b0;
                overflow <= 1'b1;
            end else begin
                count    <= count + 1;
                overflow <= 1'b0;
            end
        end
    end
endmodule
```

### 2.3 Machine d'état (FSM — Finite State Machine)

```verilog
// ─── Machine d'état de type Moore : détection de séquence "101" ───
module seq_detector (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       data_in,
    output reg        detected
);

    // Encodage des états (one-hot pour la simplicité et la vitesse)
    localparam [3:0]
        S0 = 4'b0001,   // Attente d'un '1'
        S1 = 4'b0010,   // Reçu '1'
        S2 = 4'b0100,   // Reçu '10'
        S3 = 4'b1000;   // Reçu '101' (séquence détectée)

    reg [3:0] state, next_state;

    // Registre d'état (séquentiel)
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= S0;
        else
            state <= next_state;
    end

    // Logique de prochain état (combinatoire)
    always @(*) begin
        next_state = state;  // Défaut : maintien de l'état
        case (state)
            S0: if (data_in) next_state = S1;
            S1: if (!data_in) next_state = S2;
                else next_state = S1;
            S2: if (data_in) next_state = S3;
                else next_state = S0;
            S3: if (data_in) next_state = S1;
                else next_state = S2;
        endcase
    end

    // Sortie (combinatoire)
    always @(*) begin
        detected = (state == S3);
    end
endmodule
```

---

## 3. Simulation et Vérification

### 3.1 Testbench Verilog

```verilog
// ─── Testbench pour la bascule D ───
`timescale 1ns / 1ps

module tb_d_flip_flop;

    reg  clk;
    reg  rst_n;
    reg  d;
    wire q, q_n;

    // Instanciation du module à tester (DUT)
    d_flip_flop uut (
        .clk  (clk),
        .rst_n(rst_n),
        .d    (d),
        .q    (q),
        .q_n  (q_n)
    );

    // Génération d'horloge : période 10 ns (100 MHz)
    always #5 clk = ~clk;

    initial begin
        // Initialisation
        clk   = 0;
        rst_n = 0;
        d     = 0;

        // Reset
        #20 rst_n = 1;

        // Test : bascule sur chaque front montant
        #10 d = 1;
        #10 d = 0;
        #10 d = 1;
        #10 d = 1;
        #10 d = 0;

        #20 $finish;
    end

    // Surveillance des signaux
    initial begin
        $monitor("t=%0t: clk=%b rst=%b d=%b q=%b q_n=%b",
                 $time, clk, rst_n, d, q, q_n);
    end
endmodule
```

### 3.2 Simulation avec Verilator (open source, ultra-rapide)

```bash
# Verilator convertit le Verilog synthétisable en C++,
# compile et exécute la simulation (10-100× plus rapide que Vivado)

# Installation
sudo apt install verilator

# Compilation du testbench
verilator --cc --exe --build -j \
    --top-module d_flip_flop \
    d_flip_flop.v tb_d_flip_flop.v \
    --Mdir obj_dir

# Exécution
./obj_dir/Vd_flip_flop

# Sortie VCD pour GTKWave
verilator --cc --exe --build -j --trace \
    --top-module d_flip_flop \
    d_flip_flop.v tb_d_flip_flop.v
./obj_dir/Vd_flip_flop
gtkwave trace.vcd
```

### 3.3 Vérification formelle (SymbiYosys)

```bash
# Installation de SymbiYosys (sby)
# Vérification formelle : prouve que le design respecte des assertions
# (SVA — SystemVerilog Assertions)

# Fichier .sby :
# [options]
# mode prove
# depth 20
# [engines]
# smtbmc
# [script]
# read -formal top.v
# prep -top top
# [files]
# top.v

# Exécution
sby -f top.sby
```

---

## 4. Interfaces de Communication

### 4.1 Interface SPI Maître

```verilog
// ─── SPI Master (mode 0 : CPOL=0, CPHA=0) ───
module spi_master (
    input  wire        clk,        // Horloge système (50 MHz)
    input  wire        rst_n,
    input  wire        start,      // Déclenchement de la transaction
    input  wire [7:0]  data_in,    // Octet à envoyer
    output reg  [7:0]  data_out,   // Octet reçu
    output reg         busy,       // Transaction en cours
    // Interface SPI
    output reg         sck,        // Horloge SPI
    output reg         cs_n,       // Chip Select (actif bas)
    output reg         mosi,       // Master Out Slave In
    input  wire        miso        // Master In Slave Out
);

    localparam DIV = 50;  // Division d'horloge pour SCK = 1 MHz (50 MHz / 50)

    reg [5:0]  clk_div;
    reg [2:0]  bit_cnt;     // Compteur de bits (0-7)
    reg [7:0]  shift_reg;

    typedef enum {IDLE, ACTIVE, DONE} state_t;
    state_t state;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state    <= IDLE;
            sck      <= 0;
            cs_n     <= 1;
            mosi     <= 0;
            busy     <= 0;
            data_out <= 8'b0;
            clk_div  <= 0;
            bit_cnt  <= 0;
        end else begin
            case (state)
                IDLE: begin
                    cs_n <= 1;
                    busy <= 0;
                    if (start) begin
                        state    <= ACTIVE;
                        cs_n     <= 0;
                        shift_reg <= data_in;
                        bit_cnt  <= 0;
                        clk_div  <= 0;
                        sck      <= 0;
                    end
                end

                ACTIVE: begin
                    busy <= 1;
                    // Diviseur d'horloge pour SCK
                    if (clk_div == DIV - 1) begin
                        clk_div <= 0;
                        sck     <= ~sck;

                        // Sur front descendant de SCK : échantillonner MISO
                        if (sck) begin
                            shift_reg <= {shift_reg[6:0], miso};
                        // Sur front montant de SCK : émettre MOSI
                        end else begin
                            mosi <= shift_reg[7];
                            // Fin de la transmission
                            if (bit_cnt == 7) begin
                                state   <= DONE;
                                data_out <= shift_reg;
                            end
                            bit_cnt <= bit_cnt + 1;
                        end
                    end else begin
                        clk_div <= clk_div + 1;
                    end
                end

                DONE: begin
                    cs_n <= 1;
                    busy <= 0;
                    state <= IDLE;
                end
            endcase
        end
    end
endmodule
```

### 4.2 UART Récepteur

```verilog
// ─── UART Receiver (8N1, 115200 bauds) ───
module uart_rx (
    input  wire        clk,        // 50 MHz
    input  wire        rst_n,
    input  wire        rx,         // Ligne série
    output reg  [7:0]  data,       // Octet reçu
    output reg         data_valid  // Signal de validation
);

    localparam BIT_CYCLES = 434;  // 50 MHz / 115200 bauds

    reg [8:0]  baud_counter;
    reg [3:0]  bit_index;      // 0=start, 1-8=data, 9=stop
    reg [7:0]  shift_reg;
    reg        rx_sync, rx_prev;

    typedef enum {IDLE, START, DATA, STOP} state_t;
    state_t state;

    // Synchronisation de l'entrée asynchrone
    always @(posedge clk) begin
        rx_sync <= rx;
        rx_prev <= rx_sync;
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state      <= IDLE;
            baud_counter <= 0;
            data       <= 8'b0;
            data_valid <= 1'b0;
        end else begin
            data_valid <= 1'b0;  // Un seul cycle

            case (state)
                IDLE: begin
                    if (rx_sync == 1'b0 && rx_prev == 1'b1) begin
                        // Détection du front descendant (start bit)
                        state        <= START;
                        baud_counter <= 0;
                    end
                end

                START: begin
                    // Attendre le milieu du start bit
                    if (baud_counter == BIT_CYCLES / 2) begin
                        if (rx_sync == 1'b0) begin
                            state        <= DATA;
                            bit_index    <= 0;
                            baud_counter <= 0;
                        end else begin
                            state <= IDLE;  // Fausse alerte
                        end
                    end else begin
                        baud_counter <= baud_counter + 1;
                    end
                end

                DATA: begin
                    if (baud_counter == BIT_CYCLES - 1) begin
                        baud_counter <= 0;
                        shift_reg <= {rx_sync, shift_reg[7:1]};  // LSB first
                        if (bit_index == 7) begin
                            state <= STOP;
                        end
                        bit_index <= bit_index + 1;
                    end else begin
                        baud_counter <= baud_counter + 1;
                    end
                end

                STOP: begin
                    if (baud_counter == BIT_CYCLES - 1) begin
                        data       <= shift_reg;
                        data_valid <= 1'b1;
                        state      <= IDLE;
                    end else begin
                        baud_counter <= baud_counter + 1;
                    end
                end
            endcase
        end
    end
endmodule
```

---

## 5. Synthèse et Contraintes Temporelles

### 5.1 Fichier de contraintes XDC (Xilinx)

```tcl
# ─── Contraintes temporelles XDC pour Vivado ───

# Horloge primaire (50 MHz sur pin E3)
create_clock -period 20.000 -name sys_clk [get_ports clk]

# Contrainte d'entrée : données arrivent 2 ns après le front d'horloge
set_input_delay -clock sys_clk -max 2.0 [get_ports data_in]
set_input_delay -clock sys_clk -min 1.0 [get_ports data_in]

# Contrainte de sortie : données valides 3 ns avant le front d'horloge
set_output_delay -clock sys_clk -max 3.0 [get_ports data_out]
set_output_delay -clock sys_clk -min 0.5 [get_ports data_out]

# Contrainte de faux chemin (asynchrone, CDC)
set_false_path -from [get_clocks sys_clk] -to [get_clocks uart_clk]

# Contrainte multicycle (chemin lent)
set_multicycle_path 2 -setup -from [get_pins counter_reg/C] -to [get_pins display_reg/D]
set_multicycle_path 1 -hold -from [get_pins counter_reg/C] -to [get_pins display_reg/D]
```

### 5.2 Analyse des temps de propagation

```verilog
// Le timing du FPGA doit respecter :
//   T_clk2q + T_logic + T_routing + T_setup ≤ T_period

// Si le design ne tient pas les temps (negative slack) :
// 1. Pipeline : insérer des registres intermédiaires
// 2. Réduire la logique combinatoire entre deux registres
// 3. Augmenter la période d'horloge (réduire la fréquence)
// 4. Utiliser des primitives de retiming (register balancing)
// 5. Optimiser le placement (floorplanning)

// Exemple : pipeline sur 3 cycles pour une addition complexe
// Sans pipeline : 1 cycle, fréquence max = 50 MHz
// Avec pipeline : 3 cycles, fréquence max = 150 MHz, latence = 3 cycles
module adder_pipeline (
    input  wire        clk,
    input  wire [15:0] a, b, c, d,
    output reg  [15:0] result
);

    reg [15:0] p1, p2;

    always @(posedge clk) begin
        p1     <= a + b;        // Étape 1
        p2     <= c + d;        // Étape 1 (parallèle)
        result <= p1 + p2;      // Étape 2
    end
endmodule
```

---

## 6. Traitement DSP sur FPGA

### 6.1 Filtre FIR en pipeline

```verilog
// ─── Filtre FIR 4 taps (coefficients symétriques) ───
module fir_4tap (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [7:0]  din,      // Échantillon d'entrée
    output reg  [15:0] dout      // Échantillon filtré
);

    // Coefficients prédéfinis (passe-bas, fc = 0.25 fs)
    localparam [7:0] coeff[0:3] = '{8'd12, 8'd34, 8'd50, 8'd34};

    reg [7:0]  delay_line[0:3];  // Ligne à retard 4 taps
    reg [15:0] mac;

    integer i;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < 4; i = i + 1)
                delay_line[i] <= 8'b0;
            dout <= 16'b0;
        end else begin
            // Décalage de la ligne à retard
            delay_line[0] <= din;
            for (i = 1; i < 4; i = i + 1)
                delay_line[i] <= delay_line[i-1];

            // MAC (Multiply-Accumulate) en pipeline
            mac <= delay_line[0] * coeff[0] +
                   delay_line[1] * coeff[1] +
                   delay_line[2] * coeff[2] +
                   delay_line[3] * coeff[3];
            dout <= mac;
        end
    end
endmodule
```

---

## 7. Outils Open Source (Yosys + nextpnr)

### 7.1 Flux de synthèse open source

```bash
# Installation des outils
sudo apt install yosys nextpnr-ice40 fpga-icestorm

# Synthèse Verilog → netlist
yosys -p "
    read_verilog top.v
    synth_ice40 -top top -json top.json
"

# Placement et routage (Lattice iCE40)
nextpnr-ice40 --hx8k --package ct256 \
    --json top.json --pcf top.pcf \
    --asc top.asc

# Génération du bitstream
icepack top.asc top.bin

# Programmation du FPGA
iceprog top.bin
```

### 7.2 Simulation avec Icarus Verilog (iverilog)

```bash
# Compilation et simulation
iverilog -o tb_top.vvp top.v tb_top.v
vvp tb_top.vvp -lxt2

# Visualisation
gtkwave dump.vcd
```

---

## Pièges Courants

1. **Métastabilité des signaux asynchrones :** Un signal externe non synchronisé avec l'horloge du FPGA peut entrer en métastabilité. Toujours synchroniser les entrées asynchrones par au moins deux bascules en cascade (double flopping).

2. **Latches non désirés :** Un `always @(*)` (Verilog) ou `process(all)` (VHDL) qui n'assigne pas toutes les sorties dans tous les chemins génère des latches (mémoire non désirée). Toujours assigner des valeurs par défaut en début de bloc.

3. **Inferer des registres au lieu de la logique combinatoire :** Utiliser `=` (bloquant) en Verilog dans un `always @(posedge clk)` est correct pour les registres, mais `<=` (non-bloquant) est la règle pour les designs séquentiels. Les deux mélangés dans le même bloc causent des bugs subtils.

4. **Trop de logique combinatoire entre deux registres :** Un chemin combinatoire long (Addition 64 bits + comparaison + multiplexeur) peut ne pas tenir la fréquence d'horloge cible. Pipelliner en plusieurs étages.

5. **Domaines d'horloge multiples (CDC) non gérés :** Transférer un signal d'un domaine d'horloge à un autre sans synchroniseur crée de la métastabilité. Utiliser des synchroniseurs à 2 bascules, des FIFO asynchrones, ou des pointeurs Gray.

6. **Ressources DSP non utilisées :** Les FPGA contiennent des blocs DSP matériels (multiplieurs 18×25, accumulateurs 48 bits). Pour les applications de traitement du signal, les utiliser explicitement via `(* use_dsp = "yes" *)` ou en instanciant les primitives DSP48E.

7. **Consommation excessive :** Laisser les signaux inutilisés commuter à chaque cycle d'horloge augmente la consommation dynamique. Utiliser des clock enables et mettre les sorties inutilisées à zéro.

---

## Liste de vérification (Checklist)

- [ ] Les entrées asynchrones sont synchronisées (double flopping).
- [ ] Aucun latch n'est inféré (tous les chemins dans `always @(*)` sont couverts).
- [ ] Les assignations non-bloquantes (`<=`) sont utilisées pour les registres séquentiels.
- [ ] Les contraintes temporelles (XDC/SDC) sont définies pour toutes les horloges.
- [ ] Le design passe la simulation fonctionnelle (RTL) et post-synthèse.
- [ ] Les domaines d'horloge multiples (CDC) sont correctement gérés.
- [ ] Les blocs DSP matériels sont utilisés pour les multiplications.
- [ ] La consommation de ressources (LUT, FF, BRAM, DSP) est documentée.
- [ ] Le timing slack est positif (tous les chemins respectent le setup/hold).
- [ ] Le bitstream est programmé et le design fonctionne sur la cible.
- [ ] Les outils open source (Yosys, nextpnr) sont utilisables pour les FPGA Lattice.