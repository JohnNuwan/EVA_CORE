# Matrice rapide de filtres Wireshark / tshark

- Profinet DCP : `udp.port == 34964`
- Profinet RT : `eth.type == 0x8892`
- Siemens S7 : `tcp.port == 102`
- Modbus TCP : `tcp.port == 502`
- EtherNet/IP : `tcp.port == 44818 or udp.port == 2222`
- OPC UA : `tcp.port == 4840`
- MQTT : `tcp.port == 1883 or tcp.port == 8883`

Questions à poser systématiquement :
1. Le protocole observé est-il attendu sur cette cellule ?
2. Les conversations sont-elles stables ou bursty ?
3. Les flux critiques coïncident-ils avec l'horodatage du défaut ?
4. L'anomalie est-elle applicative, transport ou couche 2 ?
