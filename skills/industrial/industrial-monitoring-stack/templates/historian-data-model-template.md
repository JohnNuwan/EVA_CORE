# Template de modèle de données Historian

## Option A — InfluxDB
### Bucket brut
- `machine_states`
- `machine_analogs`
- `machine_alarms`
- `robot_states`
- `energy_meters`

### Tags recommandés
- `site`
- `atelier`
- `ligne`
- `machine`
- `robot`
- `equipment_type`
- `state_family`

### Fields recommandés
- `value_bool`
- `value_int`
- `value_float`
- `fault_code`
- `cycle_time_s`
- `quality`

## Option B — TimescaleDB
### Tables recommandées
- `telemetry_raw`
- `events_alarms`
- `robot_events`
- `energy_readings`
- `kpi_oee_hourly`

### Colonnes minimales
- `ts_utc`
- `site`
- `atelier`
- `ligne`
- `machine`
- `equipment`
- `point_name`
- `family`
- `value_num`
- `value_text`
- `quality`

## Règles communes
- tous les timestamps en UTC ;
- stocker la qualité quand disponible ;
- séparer événements et mesures continues ;
- prévoir agrégation minute / heure / jour ;
- garder un nom canonique unique par point.
