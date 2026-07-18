#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Industrial Sensor Simulator - Outil de simulation de capteurs et d'équipements.
Démarre localement un serveur OPC UA et un serveur Modbus TCP pour simuler des variables d'usine.
"""

import sys
import os
import time
import math
import random
import asyncio
import argparse
import subprocess

def install_dependencies():
    """Tente d'installer les dépendances requises dans l'environnement virtuel actif."""
    try:
        import asyncua
        import pymodbus
    except ImportError:
        print("Dépendances manquantes. Tentative d'installation de asyncua et pymodbus...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "asyncua", "pymodbus"])
            print("Dépendances installées avec succès.")
        except Exception as e:
            print(f"Erreur d'installation des dépendances : {e}")
            sys.exit(1)

# Lancer la vérification/installation des dépendances
install_dependencies()

from asyncua import Server as OPCUAServer
from asyncua import ua
from pymodbus.server import StartAsyncTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext

class SimulatorState:
    """Conserve l'état partagé des capteurs simulés."""
    def __init__(self):
        self.temperature = 20.0
        self.pressure = 1.0
        self.fault_active = False
        self.cycle_count = 0

    def update(self):
        """Met à jour les signaux avec des variations réalistes (ondes sinusoïdales, bruit et défauts)."""
        self.cycle_count += 1
        
        # Simulation d'un défaut toutes les 45 secondes (durant 5 secondes)
        if self.cycle_count % 45 in range(40, 45):
            self.fault_active = True
        else:
            self.fault_active = False

        if self.fault_active:
            # En cas de défaut, la température et la pression s'emballent
            self.temperature += random.uniform(2.0, 5.0)
            self.pressure += random.uniform(0.2, 0.5)
        else:
            # Reprise graduelle ou oscillation normale
            base_temp = 75.0  # Température de consigne nominale
            # Oscillation sinusoïdale + bruit
            self.temperature = base_temp + (5.0 * math.sin(self.cycle_count / 10.0)) + random.uniform(-0.5, 0.5)
            
            # La pression est corrélée à la température
            self.pressure = 1.5 + (self.temperature - base_temp) * 0.05 + random.uniform(-0.02, 0.02)
            
            # Limiter les valeurs minimales
            self.temperature = max(15.0, self.temperature)
            self.pressure = max(0.1, self.pressure)

async def run_opcua_server(state: SimulatorState, port: int):
    """Démarre et met à jour le serveur OPC UA."""
    server = OPCUAServer()
    await server.init()
    server.set_endpoint(f"opc.tcp://0.0.0.0:{port}/freeopc/server/")
    server.set_server_name("Helios Industrial Sensor Simulator")
    
    # Enregistrer un namespace
    uri = "http://actemium.com/sensor/simulator"
    idx = await server.register_namespace(uri)
    
    # Créer l'objet parent Boiler
    boiler_obj = await server.nodes.objects.add_object(idx, "Boiler01")
    
    # Ajouter les variables
    temp_node = await boiler_obj.add_variable(idx, "Temperature", state.temperature, ua.VariantType.Float)
    press_node = await boiler_obj.add_variable(idx, "Pressure", state.pressure, ua.VariantType.Float)
    fault_node = await boiler_obj.add_variable(idx, "Fault_Active", state.fault_active, ua.VariantType.Boolean)
    
    # Rendre les variables accessibles en écriture
    await temp_node.set_writable()
    await press_node.set_writable()
    await fault_node.set_writable()

    print(f"[OPC UA] Serveur actif sur opc.tcp://0.0.0.0:{port}/")
    
    async with server:
        while True:
            # Mettre à jour les variables OPC UA avec l'état global
            await temp_node.write_value(ua.Variant(float(state.temperature), ua.VariantType.Float))
            await press_node.write_value(ua.Variant(float(state.pressure), ua.VariantType.Float))
            await fault_node.write_value(ua.Variant(bool(state.fault_active), ua.VariantType.Boolean))
            await asyncio.sleep(1.0)

async def run_modbus_server(state: SimulatorState, port: int):
    """Démarre et met à jour le serveur Modbus TCP."""
    # Créer le magasin de données Modbus
    # Registres Holding :
    # 40001 (adresse 0) : Température (multipliée par 100 pour l'encodage entier)
    # 40002 (adresse 1) : Pression (multipliée par 100)
    # 40003 (adresse 2) : Statut défaut (0=OK, 1=Défaut)
    store = ModbusSequentialDataBlock(0, [0] * 100)
    slave_context = ModbusSlaveContext(hr=store, zero_mode=True)
    context = ModbusServerContext(slaves=slave_context, single=True)
    
    # Métadonnées d'identification
    identity = ModbusDeviceIdentification()
    identity.VendorName = "Actemium"
    identity.ProductCode = "SIM-999"
    identity.VendorUrl = "http://actemium.com"
    identity.ProductName = "Helios Sensor Simulator"
    identity.ModelName = "Simulated PLC"
    
    # Tâche en arrière-plan pour actualiser le magasin de données Modbus
    async def update_modbus_store():
        while True:
            # Multiplier par 100 pour conserver 2 décimales sous forme d'entier 16 bits
            temp_int = int(state.temperature * 100)
            press_int = int(state.pressure * 100)
            fault_int = 1 if state.fault_active else 0
            
            # Écrire dans les registres Holding à partir de l'adresse 0
            store.setValues(1, [temp_int, press_int, fault_int])
            await asyncio.sleep(1.0)
            
    asyncio.create_task(update_modbus_store())
    
    print(f"[Modbus TCP] Serveur actif sur port {port} (Holding Registers 40001-40003)...")
    await StartAsyncTcpServer(context=context, identity=identity, address=("0.0.0.0", port))

async def main_loop(update_rate: float, opc_port: int, modbus_port: int):
    """Boucle principale de cadencement et de mise à jour de l'état."""
    state = SimulatorState()
    
    # Démarrer les serveurs de communication industriels
    asyncio.create_task(run_opcua_server(state, opc_port))
    asyncio.create_task(run_modbus_server(state, modbus_port))
    
    print(f"\nSimulation lancée. Fréquence de mise à jour : {update_rate}s.")
    print("Appuyez sur Ctrl+C pour arrêter le simulateur.\n")
    
    while True:
        state.update()
        # Affichage discret dans la console
        status = "DÉFAUT" if state.fault_active else "NOMINAL"
        print(f"[SIMULATOR] Temp={state.temperature:5.2f} °C | Press={state.pressure:4.2f} Bar | Status={status}", end="\r")
        await asyncio.sleep(update_rate)

def main():
    parser = argparse.ArgumentParser(description="Simulateur de capteurs et protocoles industriels.")
    parser.add_argument("--opcua-port", type=int, default=4840, help="Port du serveur OPC UA (défaut: 4840)")
    parser.add_argument("--modbus-port", type=int, default=5020, help="Port du serveur Modbus TCP (défaut: 5020 pour éviter les privilèges root)")
    parser.add_argument("--rate", type=float, default=1.0, help="Fréquence de mise à jour de la simulation en secondes (défaut: 1.0)")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main_loop(args.rate, args.opcua_port, args.modbus_port))
    except KeyboardInterrupt:
        print("\nArrêt des simulateurs industriels.")

if __name__ == "__main__":
    main()
