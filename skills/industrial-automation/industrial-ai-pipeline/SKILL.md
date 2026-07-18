---
name: industrial-ai-pipeline
description: "Pipeline IA réutilisable pour données industrielles."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
metadata:
  EVA:
    maturity: production
    tags: [industrial-ai, pipeline, plc, s7-communication, scl, grafana, api-integration]
    related_skills: [siemens-scl-expert, opc-ua-nodeset-architect]
---

# Pipeline IA Industriel : Données → Modèle → API → PLC → Grafana

## Rôle et Identité
Vous êtes un ingénieur principal en automatisation industrielle et un architecte en IA Edge. Votre rôle est de concevoir et de déployer des pipelines d'intégration de modèles d'apprentissage automatique (comme la détection d'anomalies visuelles ou vibratoires) au sein d'architectures d'atelier, assurant la communication temps réel avec les automates (PLC) et la visualisation des métriques sur Grafana.

## Vue d'ensemble
L'intégration de l'IA dans l'industrie exige des garanties de temps de cycle, de robustesse réseau, et de traçabilité. Ce skill fournit un template standardisé de bout en bout pour connecter un modèle prédictif Edge à un automate de contrôle (Siemens/Beckhoff) et à une plateforme de supervision opérationnelle.

---

## 1. Architecture Réseau et Flux de Données

```
[Capteurs Physiques] ──► Automate (PLC) 
                                │ (OPC UA / TCP)
                                ▼
                        [Passerelle FastAPI] (Inférence locale)
                                │ 
        ┌───────────────────────┴───────────────────────┐
        ▼ (Rétroaction Automate)                       ▼ (Supervision)
  [Commande PLC / Arrêt]                          [Base InfluxDB / Grafana]
```

---

## 2. Code Python de Référence : API d'Inférence FastAPI (Edge)

Ce script expose le modèle de détection d'anomalies sous forme de service web REST accessible par l'automate.

```python
# Inference Gateway API
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np

app = FastAPI(title="Edge Industrial AI Gateway", version="1.0.0")

class SensorPayload(BaseModel):
    device_id: str
    readings: list[float]

class PredictionResponse(BaseModel):
    anomaly_flag: bool
    confidence_score: float

# Fonction d'inférence statistique (remplaçable par un modèle ONNX)
def analyze_vibrations(readings: np.ndarray) -> tuple[bool, float]:
    if len(readings) == 0:
        return False, 0.0
    rms = np.sqrt(np.mean(readings**2))
    peak = np.max(np.abs(readings))
    score = float(rms * 0.7 + peak * 0.3)
    return score > 2.8, score

@app.post("/api/v1/predict", response_model=PredictionResponse)
def get_prediction(payload: SensorPayload):
    try:
        data = np.array(payload.readings)
        anomaly, score = analyze_vibrations(data)
        return PredictionResponse(anomaly_flag=anomaly, confidence_score=score)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

---

## 3. Code Siemens SCL de Référence : Requête HTTP Synchrone (Automate)

Ce bloc fonctionnel Structured Control Language (SCL) pour automate Siemens S7-1500 gère l'appel à l'API Edge à l'aide de la bibliothèque standard LHTTP.

```scl
FUNCTION_BLOCK "FB_Inference_Sync"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 1.0
   VAR_INPUT 
      Trigger : Bool;
      URL : String;
      Sensor_Values : Array[0..4] of Real;
   END_VAR

   VAR_OUTPUT 
      Anomaly_Detected : Bool;
      Inference_Score : Real;
      Error : Bool;
      Error_Status : Word;
   END_VAR

   VAR 
      inst_HTTP_Post : "LHTTP_Post";
      send_Data : Array[0..512] of Byte;
      recv_Data : Array[0..512] of Byte;
      json_Request : String;
      json_Response : String;
      step : Int := 0;
   END_VAR

BEGIN
   IF #Trigger AND #step = 0 THEN
      #step := 1;
   END_IF;

   CASE #step OF
      1: // Construction du payload JSON
         #json_Request := CONCAT(IN1:='{"device_id": "motor_01", "readings": [', 
                                 IN2:=REAL_TO_STRING(#Sensor_Values[0]));
         #json_Request := CONCAT(IN1:=#json_Request, IN2:=',');
         #json_Request := CONCAT(IN1:=#json_Request, IN2:=REAL_TO_STRING(#Sensor_Values[1]));
         #json_Request := CONCAT(IN1:=#json_Request, IN2:=']}');
         
         StringToChars(IN:=#json_Request, OUT:=#send_Data);
         #step := 2;
         
      2: // Exécution de la requête HTTP
         #inst_HTTP_Post(execute := TRUE,
                         url := #URL,
                         data := #send_Data,
                         response => #recv_Data,
                         error => #Error,
                         status => #Error_Status);
                         
         IF #inst_HTTP_Post.done THEN
            #step := 3;
         ELSIF #Error THEN
            #step := 99;
         END_IF;
         
      3: // Extraction des résultats du JSON
         CharsToString(IN:=#recv_Data, OUT:=#json_Response);
         
         IF FIND(IN1:=#json_Response, IN2:='"anomaly_flag":true') > 0 THEN
            #Anomaly_Detected := TRUE;
         ELSE
            #Anomaly_Detected := FALSE;
         END_IF;
         
         #step := 0;
         
      99: // Gestion des erreurs de communication
         #Anomaly_Detected := FALSE;
         IF NOT #Trigger THEN
            #step := 0;
         END_IF;
   END_CASE;
END_FUNCTION_BLOCK
```

---

## 4. Pièges Courants (Common Pitfalls)
*   **Temps de cycle automate dépassé (Watchdog)** : Exécuter des requêtes HTTP synchrones directement dans la tâche cyclique principale (OB1) de l'automate. Les requêtes réseau prennent de quelques millisecondes à plusieurs secondes. **Solution** : Toujours exécuter les blocs de communication dans une tâche asynchrone ou via une machine d'état (case structure) cadencée à basse priorité.
*   **Encodage de Caractères** : Les chaînes de caractères Siemens (`String`) possèdent un en-tête de longueur sur 2 octets. Toujours utiliser `StringToChars` pour convertir en tableau d'octets brut (`Array of Byte`) avant l'envoi.

---

## 5. Liste de vérification (Checklist)
- [ ] Développer et packager l'API d'inférence sous FastAPI.
- [ ] Définir la structure d'échange de données (JSON Payload).
- [ ] Intégrer la machine d'état asynchrone (SCL / ST) dans l'automate pour la requête HTTP.
- [ ] Configurer la source de données Grafana (Telegraf/InfluxDB) pour logger les anomalies.
- [ ] Mesurer et valider le temps de réponse global du pipeline (cible < 100ms).
