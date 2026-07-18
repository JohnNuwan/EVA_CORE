#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sparkplug B MQTT Client - Script d'assistance pour publier de la télémétrie structurée.
Permet d'envoyer des messages de Naissance (NBIRTH), de Données (NDATA) et de Décès (NDEATH).
"""

import sys
import os
import time
import argparse
import json
import subprocess

def install_dependencies():
    """Tente d'installer les dépendances requises dans l'environnement virtuel actif."""
    try:
        import paho.mqtt
        # Note: tahu est le package Eclipse Sparkplug B en Python
        # Il se nomme 'eclipse-tahu' sur PyPI
        import sparkplug_b
    except ImportError:
        print("Dépendances manquantes. Tentative d'installation de paho-mqtt et eclipse-tahu...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "paho-mqtt", "eclipse-tahu"])
            print("Dépendances installées avec succès.")
        except Exception as e:
            print(f"Erreur d'installation des dépendances : {e}")
            sys.exit(1)

# Lancer la vérification/installation des dépendances
install_dependencies()

import paho.mqtt.client as mqtt
import sparkplug_b as sparkplug
from sparkplug_b import MetricDataType

class SparkplugBClient:
    def __init__(self, broker: str, port: int, group_id: str, edge_node_id: str, device_id: str = None):
        self.broker = broker
        self.port = port
        self.group_id = group_id
        self.edge_node_id = edge_node_id
        self.device_id = device_id
        self.seq = 0
        
        self.client = mqtt.Client()
        # Configuration du message testament (Last Will)
        self.setup_will()
        
    def setup_will(self):
        """Configure le testament (NDEATH) envoyé automatiquement par le broker sur déconnexion."""
        will_topic = f"spBv1.0/{self.group_id}/NDEATH/{self.edge_node_id}"
        
        # Le payload NDEATH contient simplement le numéro de séquence courant
        death_payload = sparkplug.Payload()
        death_payload.seq = self.seq
        
        # Sérialisation
        binary_death = death_payload.SerializeToString()
        self.client.will_set(will_topic, binary_death, qos=1, retain=False)
        
    def connect(self):
        """Se connecte au broker MQTT."""
        print(f"Connexion au broker MQTT à l'adresse {self.broker}:{self.port}...")
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()
        # Attendre que la connexion s'établisse
        time.sleep(1)

    def disconnect(self):
        """Se déconnecte proprement."""
        self.client.loop_stop()
        self.client.disconnect()
        print("Déconnecté du broker MQTT.")

    def publish_nbirth(self, initial_metrics: dict):
        """Publie le message de naissance du nœud (NBIRTH)."""
        topic = f"spBv1.0/{self.group_id}/NBIRTH/{self.edge_node_id}"
        self.seq = 0 # Le NBIRTH doit toujours avoir la séquence à 0
        
        payload = sparkplug.Payload()
        payload.seq = self.seq
        
        # Ajout du paramètre BdSeq requis pour gérer le redémarrage (de 0 à 255)
        bd_seq_metric = payload.metrics.add()
        bd_seq_metric.name = "bdSeq"
        bd_seq_metric.type = MetricDataType.Int64
        bd_seq_metric.int_value = int(time.time()) % 256
        
        # Ajout des métriques utilisateur
        for name, info in initial_metrics.items():
            metric = payload.metrics.add()
            metric.name = name
            val = info["value"]
            m_type = info["type"]
            
            # Affectation du bon type
            metric.type = m_type
            if m_type == MetricDataType.Float:
                metric.float_value = float(val)
            elif m_type == MetricDataType.Double:
                metric.double_value = float(val)
            elif m_type == MetricDataType.Int32:
                metric.int_value = int(val)
            elif m_type == MetricDataType.Int64:
                metric.int_value = int(val)
            elif m_type == MetricDataType.Boolean:
                metric.boolean_value = bool(val)
            elif m_type == MetricDataType.String:
                metric.string_value = str(val)
                
        binary_payload = payload.SerializeToString()
        self.client.publish(topic, binary_payload, qos=1, retain=False)
        print(f"NBIRTH publié avec succès sur {topic} ({len(initial_metrics)} métriques)")

    def publish_ndata(self, updated_metrics: dict):
        """Publie les mises à jour de variables (NDATA)."""
        topic = f"spBv1.0/{self.group_id}/NDATA/{self.edge_node_id}"
        
        # Incrémenter la séquence (de 1 à 255, boucle)
        self.seq = (self.seq + 1) % 256
        if self.seq == 0:
            self.seq = 1 # 0 est réservé au NBIRTH
            
        payload = sparkplug.Payload()
        payload.seq = self.seq
        
        for name, info in updated_metrics.items():
            metric = payload.metrics.add()
            metric.name = name
            val = info["value"]
            m_type = info["type"]
            
            metric.type = m_type
            if m_type == MetricDataType.Float:
                metric.float_value = float(val)
            elif m_type == MetricDataType.Double:
                metric.double_value = float(val)
            elif m_type == MetricDataType.Int32:
                metric.int_value = int(val)
            elif m_type == MetricDataType.Int64:
                metric.int_value = int(val)
            elif m_type == MetricDataType.Boolean:
                metric.boolean_value = bool(val)
            elif m_type == MetricDataType.String:
                metric.string_value = str(val)
                
        binary_payload = payload.SerializeToString()
        self.client.publish(topic, binary_payload, qos=1, retain=False)
        print(f"NDATA publié avec succès sur {topic} (Séquence: {self.seq})")

def main():
    parser = argparse.ArgumentParser(description="Client d'envoi de messages Sparkplug B.")
    parser.add_argument("--broker", default="localhost", help="Adresse du broker MQTT")
    parser.add_argument("--port", type=int, default=1883, help="Port MQTT (defaut: 1883)")
    parser.add_argument("--group-id", required=True, help="ID du groupe d'équipements")
    parser.add_argument("--node-id", required=True, help="ID du nœud Edge")
    parser.add_argument("--action", required=True, choices=["birth", "data"], help="Action d'envoi")
    parser.add_argument("--metrics", required=True, help="JSON des métriques : '{\"TagName\": {\"value\": X, \"type\": \"Float|Int32|Boolean|String\"}}'")
    
    args = parser.parse_args()
    
    # Parser les métriques
    try:
        raw_metrics = json.loads(args.metrics)
    except json.JSONDecodeError:
        print("Erreur : Le format du paramètre --metrics n'est pas un JSON valide.")
        sys.exit(1)
        
    type_map = {
        "Float": MetricDataType.Float,
        "Double": MetricDataType.Double,
        "Int32": MetricDataType.Int32,
        "Int64": MetricDataType.Int64,
        "Boolean": MetricDataType.Boolean,
        "String": MetricDataType.String
    }
    
    formatted_metrics = {}
    for name, data in raw_metrics.items():
        type_str = data.get("type", "String")
        val = data.get("value")
        if type_str not in type_map:
            print(f"Erreur : Type '{type_str}' non supporté. Types supportés: {list(type_map.keys())}")
            sys.exit(1)
        formatted_metrics[name] = {
            "value": val,
            "type": type_map[type_str]
        }
        
    client = SparkplugBClient(args.broker, args.port, args.group_id, args.node_id)
    client.connect()
    
    if args.action == "birth":
        client.publish_nbirth(formatted_metrics)
    elif args.action == "data":
        # Simuler un cycle
        client.publish_nbirth(formatted_metrics)
        time.sleep(1)
        # Puis envoyer les données mises à jour
        client.publish_ndata(formatted_metrics)
        
    time.sleep(1)
    client.disconnect()

if __name__ == "__main__":
    main()
