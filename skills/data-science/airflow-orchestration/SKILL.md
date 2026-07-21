---
name: airflow-orchestration
description: "Apache Airflow: orchestration de pipelines de données (DAGs, operators, sensors, TaskFlow, execution environments, alerting)."
version: 1.0.0
author: EVA & The Hive
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [airflow, dag, orchestration, etl, taskflow, scheduler, celery, docker-operator, kubernetes-pod-operator]
    homepage: https://airflow.apache.org/
    related_skills: [data-pipelines, apache-spark, data-quality-testing, data-warehouse, data-lakes-lakehouse]
prerequisites:
  commands: [python3, pip, docker]
  pip_packages: [apache-airflow, apache-airflow-providers-docker, apache-airflow-providers-cncf-kubernetes, apache-airflow-providers-postgres, apache-airflow-providers-amazon]
---

# Compétence Apache Airflow : Orchestration de Pipelines de Données

## Vue d'ensemble

**Apache Airflow** est la plateforme d'orchestration la plus utilisée en data engineering. Elle permet de définir, planifier et monitorer des pipelines de données complexes sous forme de **DAGs** (Directed Acyclic Graphs).

Architecture clé :

- **Scheduler** : planifie les exécutions des DAGs.
- **Worker (Executor)** : exécute les tâches (LocalExecutor, CeleryExecutor, KubernetesExecutor).
- **Web Server** : interface utilisateur pour le monitoring.
- **Metastore** : base de données (PostgreSQL) pour l'état des DAGs/tâches.
- **Queue** (Celery) : file de messages pour la distribution des tâches.

Cette compétence couvre : TaskFlow API (2.0+), operators custom, sensors, Dynamic Task Mapping, execution environments (Docker / K8s Pod operator), gestion des secrets (Airflow Connections / Variables), alerting et SLA.

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :

- Veut orchestrer des pipelines ETL/ELT complexes multi-systèmes.
- A besoin de planification, retry, alerting pour des jobs batch.
- Demande d'interagir avec Spark, Kafka, dbt, Snowflake via Airflow.
- Veut gérer des dépendances inter-DAG ou intra-DAG.
- Pose des questions sur le choix de l'executor (Celery vs Kubernetes), les pools, les SLAs.

---

## Prérequis

```bash
pip install "apache-airflow[celery,postgres,amazon,docker,kubernetes]==2.10"
```

Démarrer en local :

```bash
export AIRFLOW_HOME=~/airflow
airflow db init
airflow users create --username eva --password eva --role Admin \
    --email eva@thehive.local --firstname EVA --lastname Admin
airflow standalone  # scheduler + webserver en un
```

---

## 1. Structures de DAG

### 1.1 DAG Classique (Context Manager)

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'eva',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': ['alerts@thehive.local'],
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
    'sla': timedelta(hours=1),     # Alerte si > 1h d'exécution
}

with DAG(
    dag_id='sensors_etl_pipeline',
    default_args=default_args,
    description='Pipeline ETL données capteurs industriels',
    schedule_interval='*/15 * * * *',    # Toutes les 15 minutes
    start_date=datetime(2026, 7, 1),
    catchup=False,
    tags=['sensors', 'etl', 'production'],
) as dag:

    def extract_sensors(**context):
        # Extraction depuis Kafka/API
        execution_date = context['execution_date']
        print(f"Extraction des capteurs pour {execution_date}")
        return {"count": 15000, "sources": ["M-001", "M-002"]}

    def transform_data(ti, **context):
        result = ti.xcom_pull(task_ids='extract_sensors')
        print(f"Transformation de {result['count']} relevés")
        return {"processed": result['count']}

    extract = PythonOperator(
        task_id='extract_sensors',
        python_callable=extract_sensors,
    )

    transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
    )

    load = BashOperator(
        task_id='load_to_warehouse',
        bash_command='python3 /opt/scripts/load_to_dw.py --date {{ ds }}',
    )

    extract >> transform >> load
```

### 1.2 DAG avec TaskFlow API (Décorateurs, Airflow 2.0+)

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(
    schedule_interval='0 6 * * *',   # 6h du matin
    start_date=datetime(2026, 7, 1),
    catchup=False,
    tags=['daily', 'reporting'],
)
def daily_report_pipeline():

    @task(multiple_outputs=True)
    def fetch_sensor_data():
        """Extraction des données capteurs"""
        import pandas as pd
        df = pd.read_parquet("/data/raw/sensors/")
        return {
            "total_readings": len(df),
            "avg_temp": float(df['temperature'].mean()),
            "max_temp": float(df['temperature'].max()),
        }

    @task(retries=3, retry_delay=timedelta(minutes=2))
    def compute_kpis(data: dict) -> dict:
        """Calcul des KPI quotidiens"""
        return {
            "oee_score": 0.87,
            "availability": 0.95,
            "performance": 0.92,
            "quality": 0.99,
            "total_readings": data['total_readings'],
        }

    @task
    def generate_report(kpis: dict):
        """Génération du rapport PDF"""
        from jinja2 import Template
        print(f"Rapport OEE: {kpis['oee_score']:.1%}")
        return {"report_url": f"/reports/{datetime.now():%Y%m%d}_oee.pdf"}

    @task
    def notify_slack(report: dict):
        """Notification sur Slack"""
        print(f"Rapport disponible: {report['report_url']}")

    # Chaînage avec valeurs de retour
    data = fetch_sensor_data()
    kpis = compute_kpis(data)
    report = generate_report(kpis)
    notify_slack(report)

dag = daily_report_pipeline()
```

### 1.3 Dynamic Task Mapping (Airflow 2.3+)

```python
@dag(...)
def multi_machine_etl():

    @task
    def list_machines() -> list:
        return [f"M-{i:03d}" for i in range(1, 51)]  # 50 machines

    @task(map_index_template="{{ machine }}")
    def process_machine(machine: str) -> dict:
        """Tâche parallélisée par machine"""
        return {"machine_id": machine, "processed": True}

    @task
    def aggregate_results(results: list[dict]) -> dict:
        total = sum(1 for r in results if r['processed'])
        return {"machines_processed": total, "total": len(results)}

    machines = list_machines()
    # 50 tâches lancées en parallèle
    results = process_machine.expand(machine=machines)
    aggregate = aggregate_results(results)

dag = multi_machine_etl()
```

---

## 2. Sensors : Attente et Déclenchement Conditionnel

### 2.1 Sensors Intégrés

```python
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.time_delta import TimeDeltaSensor
from airflow.sensors.sql import SqlSensor

# Attendre qu'un fichier arrive sur S3
wait_for_file = S3KeySensor(
    task_id='wait_for_sensor_file',
    bucket_key='s3://data-lake/raw/sensors/{{ ds_nodash }}/*.parquet',
    wildcard_match=True,
    aws_conn_id='aws_default',
    timeout=3600,        # Timeout après 1h
    poke_interval=60,    # Vérification toutes les 60s
    mode='poke',          # poke = polling, reschedule = libère le worker
)

# Attendre qu'une table PostgreSQL soit prête
wait_for_table = SqlSensor(
    task_id='wait_for_staging_table',
    conn_id='postgres_dw',
    sql="SELECT COUNT(*) FROM staging.import_status WHERE date = '{{ ds }}' AND status = 'READY'",
    success=lambda x: x[0][0] > 0,
    timeout=600,
)
```

### 2.2 Sensor Personnalisé

```python
from airflow.sensors.base import BaseSensorOperator
from typing import Any

class KafkaTopicSensor(BaseSensorOperator):
    template_fields = ('topic',)

    def __init__(self, topic: str, kafka_conn_id: str, **kwargs):
        super().__init__(**kwargs)
        self.topic = topic
        self.kafka_conn_id = kafka_conn_id

    def poke(self, context: Any) -> bool:
        from kafka import KafkaAdminClient
        from airflow.hooks.base import BaseHook

        conn = BaseHook.get_connection(self.kafka_conn_id)
        client = KafkaAdminClient(
            bootstrap_servers=conn.host,
            client_id='airflow-sensor'
        )
        topics = client.list_topics()
        return self.topic in topics

# Utilisation
wait_for_kafka = KafkaTopicSensor(
    task_id='wait_for_topic',
    topic='sensors-aggregated',
    kafka_conn_id='kafka_default',
    timeout=300,
)
```

---

## 3. Execution Environments

### 3.1 DockerOperator (Isolation Conteneur)

```python
from airflow.providers.docker.operators.docker import DockerOperator

run_spark_job = DockerOperator(
    task_id='spark_transform',
    image='eva/spark-job:latest',
    container_name='spark-transform-{{ run_id }}',
    api_version='auto',
    auto_remove=True,                                # Nettoie le conteneur
    docker_url='unix://var/run/docker.sock',
    network_mode='bridge',
    environment={
        'SPARK_MASTER': 'spark://spark-master:7077',
        'INPUT_PATH': '/data/raw/',
        'OUTPUT_PATH': '/data/curated/',
    },
    mounts=[
        Mount(source='/data', target='/data', type='bind'),
    ],
    working_dir='/app',
    force_pull=False,
    user='1000:1000',
    mem_limit='4g',
    shm_size='2g',
)
```

### 3.2 KubernetesPodOperator (Élasticité Native)

```python
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator

k8s_spark = KubernetesPodOperator(
    task_id='spark_k8s_job',
    name='spark-transform-{{ ds }}',
    namespace='data-pipelines',
    image='eva/spark-job:latest',
    cmds=['spark-submit'],
    arguments=[
        '--master', 'k8s://https://kubernetes.default:443',
        '--deploy-mode', 'cluster',
        '--conf', 'spark.executor.instances=4',
        '--conf', 'spark.driver.memory=4g',
        '--conf', 'spark.executor.memory=8g',
        'local:///app/etl/transform.py',
        '--date', '{{ ds }}',
    ],
    image_pull_policy='Always',
    in_cluster=True,
    get_logs=True,
    is_delete_operator_pod=True,
    startup_timeout_seconds=300,
    resources={
        'request_cpu': '2',
        'request_memory': '4G',
        'limit_cpu': '4',
        'limit_memory': '8G',
    },
    env_vars={
        'ENVIRONMENT': 'production',
        'LOG_LEVEL': 'INFO',
    },
)
```

---

## 4. Exécuteurs (Executors)

### 4.1 Choix de l'Executor

| Executor | Cas d'Usage | Scaling | Isolation | Latence |
|----------|-------------|---------|-----------|---------|
| **LocalExecutor** | Développement / 1 machine | Par processus | Faible | Immédiate |
| **CeleryExecutor** | Production multi-worker | Par machine (pré-alloué) | Process | 1-2s |
| **KubernetesExecutor** | Cloud / scaling dynamique | Par tâche (pods) | Forte (conteneur) | 5-15s |
| **CeleryKubernetesExecutor** | Hybrid (base + burst) | Mixte | Mixte | Variables |

### 4.2 Configuration Celery (Production)

```yaml
# docker-compose.yml pour Airflow Celery
version: '3.8'
services:
  airflow-scheduler:
    image: apache/airflow:2.10
    command: scheduler
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor
      AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
      AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres:5432/airflow
      AIRFLOW__CELERY__WORKER_CONCURRENCY: 8

  airflow-worker:
    image: apache/airflow:2.10
    command: celery worker
    deploy:
      replicas: 3
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor

  redis:
    image: redis:7-alpine

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: airflow
```

---

## 5. Gestion des Secrets et Variables

### 5.1 Airflow Connections

```python
from airflow.models import Connection
from airflow.settings import Session

# Créer une connexion programmatique
conn = Connection(
    conn_id='postgres_dw',
    conn_type='postgres',
    host='postgres-1.data.internal',
    login='airflow',
    password='${AIRFLOW_SECRET_POSTGRES_PW}',
    port=5432,
    extra={
        "sslmode": "require",
        "keepalives_idle": 30,
    }
)

# Utiliser en Variable d'environnement
# export AIRFLOW_CONN_POSTGRES_DW='postgres://airflow:pass@host:5432/dw'
```

### 5.2 Variables et Paramètres de DAG

```python
from airflow.models import Variable

# Définir
Variable.set("slack_webhook", "https://hooks.slack.com/services/...")
Variable.set("data_config", {
    "batch_size": 10000,
    "retention_days": 90,
    "output_format": "parquet"
})

# Utiliser dans un DAG
class ConfigurableDAG:
    @task
    def use_config():
        config = Variable.get("data_config", deserialize_json=True)
        print(f"Batch size: {config['batch_size']}")
```

### 5.3 Paramètres (Airflow 2.4+)

```python
from airflow.models.param import Param

@dag(
    params={
        'date_range': Param(
            default='2026-07-01,2026-07-22',
            type='string',
            description='Plage de dates (YYYY-MM-DD,YYYY-MM-DD)'
        ),
        'full_refresh': Param(
            default=False,
            type='boolean',
        ),
    }
)
def configurable_etl():
    @task
    def extract(params):
        dates = params['date_range'].split(',')
        print(f"Extraction du {dates[0]} au {dates[1]}")
```

---

## 6. Alerting et Observabilité

### 6.1 Alerting Multi-Canal

```python
from airflow.notifications.basenotifier import BaseNotifier

class SlackTeamsNotifier(BaseNotifier):
    template_fields = ('message',)

    def __init__(self, message: str = "", **kwargs):
        super().__init__(**kwargs)
        self.message = message

    def notify(self, context):
        self._send_slack(context)
        self._send_teams(context)

    def _send_slack(self, context):
        webhook = Variable.get("slack_webhook")
        dag_id = context['dag'].dag_id
        task_id = context['task'].task_id
        state = context['ti'].state
        import requests
        requests.post(webhook, json={
            "text": f"*{dag_id}* — `{task_id}` → *{state}*"
        })

# Utilisation dans un DAG
with DAG(...) as dag:
    t1 = PythonOperator(
        task_id='risky_operation',
        python_callable=do_something_risky,
        on_failure_callback=SlackTeamsNotifier(),
    )
```

### 6.2 SLAs et Timeouts

```python
with DAG(
    dag_id='sla_monitored_dag',
    sla_miss_callback=notify_sla_miss,  # Fonction appelée si SLA dépassé
    default_args={
        'sla': timedelta(minutes=30),   # Alerte si tâche > 30 min
        'execution_timeout': timedelta(hours=2),  # Tâche tuée après 2h
    },
):
    ...
```

---

## 7. Patterns Avancés

### 7.1 Backfill (Reprise Historique)

```bash
airflow dags backfill sensor_etl_pipeline \
    --start-date 2026-06-01 \
    --end-date 2026-06-30 \
    --reset-dagruns
```

### 7.2 DAG Runs Conditionnels (Branch Operators)

```python
from airflow.operators.python import BranchPythonOperator

def choose_branch(**context):
    if context['params'].get('full_refresh', False):
        return ['full_load']
    return ['incremental_load']

branch = BranchPythonOperator(
    task_id='choose_mode',
    python_callable=choose_branch,
)

full_load >> notify_done
incremental_load >> notify_done
```

### 7.3 Pools et Resource Pools

```python
# Limiter le parallélisme : 2 tâches Spark simultanées max
run_spark_1 = SparkSubmitOperator(
    task_id='spark_load_1',
    pool='spark_pool',
    ...
)
run_spark_2 = SparkSubmitOperator(
    task_id='spark_load_2',
    pool='spark_pool',
    ...
)

# Config du pool : airflow pools set spark_pool 2 "Pool pour les jobs Spark"
```

---

## Pièges Courants (Pitfalls)

1. **DAGs non idempotents.**  
   - *Erreur :* Un backfill ou un retry produit des doublons dans la base cible.  
   - *Correction :* Tous les DAGs doivent être idempotents. Utiliser `INSERT OVERWRITE`, `MERGE`, ou des clés déterministes.

2. **Dépendances extérieures sans gestion de timeout.**  
   - *Erreur :* Un Sensor attend indéfiniment un fichier qui n'arrive jamais → occupe un worker slot.  
   - *Correction :* Toujours configurer `timeout` et `mode='reschedule'` pour les sensors longue durée.

3. **Surcharge de la base de données metastore.**  
   - *Erreur :* Trop de DAGs actifs (500+) ou des tâches avec des logs énormes → PostgreSQL ralentit.  
   - *Correction :* Purger régulièrement : `airflow db clean --before-date 2026-01-01`. Optimiser les connexions avec PGBouncer.

4. **xcoms trop volumineux.**  
   - *Erreur :* Passer un DataFrame (plusieurs Mo) via xcom → sature la base et ralentit le scheduler.  
   - *Correction :* Stocker les données volumineuses dans S3/S3 et ne passer que le chemin via xcom.

5. **CeleryExecutor — perte de tâches sur restart worker.**  
   - *Erreur :* Un worker Celery redémarre pendant une tâche longue → la tâche est marquée en échec mais l'effet secondaire persiste.  
   - *Correction :* Configurer `task_acks_late=True` (ack après complétion) avec `task_reject_on_worker_lost=True`.

---

## Liste de Vérification (Checklist)

- [ ] DAGs idempotents (retry et backfill sans doublons).
- [ ] `catchup=False` sauf pour backfill explicite.
- [ ] Sensors avec timeout et `mode='reschedule'`.
- [ ] SLAs configurés pour les pipelines critiques.
- [ ] Pools définis pour limiter la concurrence.
- [ ] xcom limités aux métadonnées, pas aux données.
- [ ] Notifications sur échec (Slack/Teams/Email).
- [ ] `retries` configuré (au moins 2 pour la production).
- [ ] Metastore purgé régulièrement.
- [ ] Tests unitaires des DAGs avec `dag.test()`.