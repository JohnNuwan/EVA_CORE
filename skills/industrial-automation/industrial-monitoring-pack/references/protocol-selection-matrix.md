# Matrice de sélection protocolaire monitoring

| Contexte | Protocole à privilégier | Pourquoi | Risques / vigilance |
|---|---|---|---|
| Plateforme multi-constructeurs avec modèle de données exposé | OPC UA | standard, structuré, extensible | certificats, profondeur de browse, qualité du modèle |
| Siemens sans exposition OPC UA suffisante | S7 / Snap7 | accès direct automate | PUT/GET, DB optimisés, rack/slot |
| Rockwell Logix | EtherNet/IP / CIP | lecture tags native | slot CPU, polling excessif |
| Beckhoff TwinCAT | ADS | accès natif aux variables | AMS Net ID, stabilité des noms |
| Compteurs / utilités / variateurs génériques | Modbus TCP | très répandu, simple | mapping registres, endianness, unités |
| Remontée vers couche data / UNS | MQTT / Sparkplug B | diffusion, découplage, IIoT | gouvernance topics, qualité payload |
| Robot sans accès ouvert natif ou contexte cellule | Interface robot ↔ PLC | robuste, standardisable, maintenable | granularité limitée si contrat faible |

## Règles de décision
1. Privilégier le protocole le plus stable et maintenable, pas le plus « puissant » sur le papier.
2. Préférer un contrat de données robuste à une collecte fragile mais riche.
3. Si le robot ou le drive est déjà correctement représenté dans le PLC, commencer par cette couche.
4. Séparer toujours protocole terrain et protocole de remontée data.
