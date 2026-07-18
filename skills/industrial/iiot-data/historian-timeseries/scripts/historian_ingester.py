#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Historian Ingester - Script de collecte industrielle avec cache de sécurité (Store & Forward).
Lit des données OPC UA et les historise dans InfluxDB avec résilience locale SQLite.
"""

import sys
import os
import time
import json
import sqlite3
import asyncio
import subprocess
import argparse
from datetime import datetime, timezone

def install_dependencies():
    """Tente d'installer les dépendances requises dans l'environnement virtuel actif."""
    try:
        import asyncua
        import influxdb_client
    except ImportError:
        print("Dépendances manquantes. Tentative d'installation de asyncua et influxdb-client...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "asyncua", "influxdb-client"])
            print("Dépendances installées avec succès.")
        except Exception as e:
            print(f"Erreur d'installation des dépendances : {e}")
            sys.exit(1)

# Lancer la vérification/installation des dépendances
install_dependencies()

from asyncua import Client as OPCUAClient
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

class StoreAndForwardCache:
    """Gère une base SQLite locale temporaire pour stocker les points en cas de perte de connexion InfluxDB."""
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.create_table()
        
    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS data_buffer (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    tag_name TEXT,
                    tag_value REAL,
                    equipment TEXT,
                    area TEXT
                )
            """)
            
    def store_point(self, timestamp: str, name: str, val: float, eq: str, area: str):
        with self.conn:
            self.conn.execute(
                "INSERT INTO data_buffer (timestamp, tag_name, tag_value, equipment, area) VALUES (?, ?, ?, ?, ?)",
                (timestamp, name, val, eq, area)
            )
            
    def get_cached_count(self) -> int:
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM data_buffer")
        return cursor.fetchone()[0]
        
    def fetch_and_delete_batch(self, limit: int = 100) -> list:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, timestamp, tag_name, tag_value, equipment, area FROM data_buffer ORDER BY id LIMIT ?", (limit,))
        rows = cursor.fetchall()
        
        if rows:
            ids = [r[0] for r in rows]
            # Supprimer les lignes récupérées
            placeholder = ",".join("?" for _ in ids)
            with self.conn:
                self.conn.execute(f"DELETE FROM data_buffer WHERE id IN ({placeholder})", ids)
                
        return rows

class InfluxDBIngester:
    def __init__(self, url: str, token: str, org: str, bucket: str, cache_db: str):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.cache = StoreAndForwardCache(cache_db)
        
        # Initialiser le client InfluxDB
        self.influx_client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
        
    def write_points(self, points_data: list) -> bool:
        """Tente d'écrire une liste de dictionnaires dans InfluxDB. Retourne False en cas d'erreur."""
        points = []
        for p in points_data:
            dt = datetime.fromisoformat(p["timestamp"])
            point = (
                Point("plc_data")
                .tag("equipment", p["equipment"])
                .tag("area", p["area"])
                .field(p["name"], float(p["value"]))
                .time(dt)
            )
            points.append(point)
            
        try:
            self.write_api.write(bucket=self.bucket, record=points)
            return True
        except Exception as e:
            print(f"[ERROR] Impossible de pousser sur InfluxDB ({e}). Ingestion en cache local...")
            return False

    def process_data(self, tag_name: str, value: float, eq: str, area: str):
        """Prend une valeur lue et tente de l'écrire. En cas d'échec, la stocke localement."""
        ts_now = datetime.now(timezone.utc).isoformat()
        point = {
            "timestamp": ts_now,
            "name": tag_name,
            "value": value,
            "equipment": eq,
            "area": area
        }
        
        # Tenter d'écrire en direct
        success = self.write_points([point])
        if not success:
            self.cache.store_point(ts_now, tag_name, value, eq, area)
            
    def flush_cache(self) -> int:
        """Tente de vider le cache local vers InfluxDB si la connexion est rétablie."""
        count = self.cache.get_cached_count()
        if count == 0:
            return 0
            
        print(f"[INFO] Restauration réseau : {count} points en cache local. Tentative de transfert...")
        batch_size = 100
        transferred = 0
        
        while True:
            rows = self.cache.fetch_and_delete_batch(batch_size)
            if not rows:
                break
                
            points = []
            # Conversion en format dict pour write_points
            for r in rows:
                points.append({
                    "timestamp": r[1],
                    "name": r[2],
                    "value": r[3],
                    "equipment": r[4],
                    "area": r[5]
                })
                
            success = self.write_points(points)
            if success:
                transferred += len(points)
            else:
                # Ré-enregistrer les points en cas d'échec
                for p in points:
                    self.cache.store_point(p["timestamp"], p["name"], p["value"], p["equipment"], p["area"])
                print("[WARNING] Échec de transfert en cours de vidage. Transfert suspendu.")
                break
                
        return transferred

async def collect_loop(opcua_url: str, nodes_config: list, ingester: InfluxDBIngester, interval: float):
    """Boucle principale de collecte depuis OPC UA."""
    while True:
        try:
            print(f"Connexion au serveur OPC UA : {opcua_url}...")
            async with OPCUAClient(url=opcua_url) as client:
                print("Connecté au serveur OPC UA.")
                
                while True:
                    start_time = time.time()
                    
                    # 1. Tenter de vider le cache local si la liaison InfluxDB est OK
                    flushed = ingester.flush_cache()
                    if flushed > 0:
                        print(f"[SUCCESS] {flushed} points transférés du cache local vers InfluxDB.")
                    
                    # 2. Lire les nœuds OPC UA et ingérer les données
                    for n_conf in nodes_config:
                        try:
                            node = client.get_node(n_conf["node_id"])
                            val = await node.read_value()
                            ingester.process_data(n_conf["name"], val, n_conf["equipment"], n_conf["area"])
                        except Exception as e:
                            print(f"[ERROR] Impossible de lire le nœud {n_conf['name']} ({n_conf['node_id']}): {e}")
                            
                    # Calcul du temps d'attente pour compenser la durée du cycle
                    elapsed = time.time() - start_time
                    sleep_time = max(0.1, interval - elapsed)
                    await asyncio.sleep(sleep_time)
                    
        except Exception as e:
            print(f"[WARNING] Perte de connexion avec le serveur OPC UA ({e}). Nouvelle tentative dans 5 secondes...")
            await asyncio.sleep(5)

def main():
    parser = argparse.ArgumentParser(description="Ingesteur Historian résilient avec support Store & Forward.")
    parser.add_argument("--opcua-url", required=True, help="URL du serveur OPC UA source")
    parser.add_argument("--influx-url", required=True, help="URL du serveur InfluxDB destination")
    parser.add_argument("--influx-token", required=True, help="Token d'authentification InfluxDB")
    parser.add_argument("--influx-org", required=True, help="Organisation InfluxDB")
    parser.add_argument("--influx-bucket", required=True, help="Bucket InfluxDB")
    parser.add_argument("--nodes", required=True, help="Liste JSON de nœuds: '[{\"node_id\": \"ns=2;i=10\", \"name\": \"temp\", \"equipment\": \"boiler\", \"area\": \"Line1\"}]'")
    parser.add_argument("--cache-db", default="historian_cache.db", help="Nom du fichier de cache local SQLite (défaut: historian_cache.db)")
    parser.add_argument("--interval", type=float, default=1.0, help="Intervalle d'échantillonnage en secondes (défaut: 1.0)")
    
    args = parser.parse_args()
    
    try:
        nodes_config = json.loads(args.nodes)
    except json.JSONDecodeError:
        print("Erreur : Le format du paramètre --nodes n'est pas un JSON valide.")
        sys.exit(1)
        
    ingester = InfluxDBIngester(args.influx_url, args.influx_token, args.influx_org, args.influx_bucket, args.cache_db)
    
    # Démarrage de la boucle asynchrone
    try:
        asyncio.run(collect_loop(args.opcua_url, nodes_config, ingester, args.interval))
    except KeyboardInterrupt:
        print("Arrêt de l'ingesteur.")

if __name__ == "__main__":
    main()
