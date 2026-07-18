#!/usr/bin/env python3
"""Génère des artefacts multi-constructeurs à partir d'un JSON métier riche.

Fonctionnalités v4 :
- Types supportés : motor, valve, analog
- Vendors supportés : siemens, rockwell, schneider, beckhoff, omron, wago
- Génère code logique + structures type + échanges XML lorsque pertinent
- Supporte un contrat unitaire OU un lot d'équipements
- Produit mapping PLC ↔ SCADA ↔ MES, tags Ignition, PackML et safety metadata
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

SUPPORTED_TYPES = {"motor", "valve", "analog"}
VENDORS_WITH_PLCOPEN = {"beckhoff", "omron", "wago"}
CORE_VENDORS = {"siemens", "rockwell", "schneider"}
ALL_VENDORS = CORE_VENDORS | VENDORS_WITH_PLCOPEN


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def cdata(text: str) -> str:
    return f"<![CDATA[{text}]]>"


def normalize_name(name: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in name)
    return safe[:40] if safe else "Device01"


def get_contracts(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if "equipment" in payload:
        return payload["equipment"]
    return [payload]


def default_scada(name: str) -> dict[str, Any]:
    return {
        "platform": "ignition",
        "provider": "default",
        "tag_root": f"AreaA/{name}",
        "cmd_path": f"AreaA/{name}/Cmd",
        "sts_path": f"AreaA/{name}/Sts",
        "alm_path": f"AreaA/{name}/Alm",
    }


def default_mes(name: str, device_type: str) -> dict[str, Any]:
    return {
        "equipment_id": name.upper(),
        "class": device_type,
        "line": "LineA",
    }


def default_safety() -> dict[str, Any]:
    return {
        "enabled": False,
        "zone": "ZONE_01",
        "plr": "PLd",
        "sil": "SIL1",
        "sto": False,
        "ss1": False,
        "sls": False,
        "reset_required": True,
    }


def default_packml() -> dict[str, Any]:
    return {
        "enabled": False,
        "mode": "basic",
        "state_model": "packml",
        "unit_mode": "production",
    }


def ensure_contract(contract: dict[str, Any]) -> dict[str, Any]:
    contract = dict(contract)
    contract["device_type"] = contract.get("device_type", "motor")
    if contract["device_type"] not in SUPPORTED_TYPES:
        raise ValueError(f"Unsupported device_type: {contract['device_type']}")
    contract["name"] = normalize_name(contract.get("name", "Device01"))
    contract["vendors"] = [v for v in contract.get("vendors", ["siemens", "rockwell", "schneider"]) if v in ALL_VENDORS]
    contract.setdefault("io", {})
    contract.setdefault("alarms", [])
    contract.setdefault("permissives", [])
    contract.setdefault("timers", {})
    contract.setdefault("units", {})
    contract["scada"] = {**default_scada(contract["name"]), **contract.get("scada", {})}
    contract["mes"] = {**default_mes(contract["name"], contract["device_type"]), **contract.get("mes", {})}
    contract["safety"] = {**default_safety(), **contract.get("safety", {})}
    contract["packml"] = {**default_packml(), **contract.get("packml", {})}
    return contract


def safety_comment(contract: dict[str, Any]) -> str:
    s = contract["safety"]
    return (
        f"Safety: enabled={s['enabled']}, zone={s['zone']}, PLr={s['plr']}, "
        f"SIL={s['sil']}, STO={s['sto']}, SS1={s['ss1']}, SLS={s['sls']}, reset={s['reset_required']}"
    )


def safety_fields_text(contract: dict[str, Any], style: str) -> str:
    s = contract["safety"]
    if style == "siemens":
        return (
            f"Safety_Enabled : Bool := {str(bool(s['enabled'])).upper()};\n"
            f"    Safety_ResetRequired : Bool := {str(bool(s['reset_required'])).upper()};\n"
            f"    Safety_STO : Bool := {str(bool(s['sto'])).upper()};\n"
            f"    Safety_SS1 : Bool := {str(bool(s['ss1'])).upper()};\n"
            f"    Safety_SLS : Bool := {str(bool(s['sls'])).upper()};"
        )
    if style == "rockwell":
        return (
            f"Safety_Enabled : BOOL;\n"
            f"    Safety_ResetRequired : BOOL;\n"
            f"    Safety_STO : BOOL;\n"
            f"    Safety_SS1 : BOOL;\n"
            f"    Safety_SLS : BOOL;"
        )
    return (
        f"bSafetyEnabled : BOOL;\n"
        f"    bSafetyResetRequired : BOOL;\n"
        f"    bSafetySTO : BOOL;\n"
        f"    bSafetySS1 : BOOL;\n"
        f"    bSafetySLS : BOOL;"
    )


# ---------------- Siemens ----------------
def siemens_motor_fb(contract: dict[str, Any]) -> str:
    name = contract["name"]
    return f'''// {safety_comment(contract)}
FUNCTION_BLOCK "FB_{name}"
{{ S7_Optimized_Access := 'TRUE' }}
VERSION : 0.1
VAR_INPUT
    i_Start : Bool;
    i_Stop : Bool;
    i_Reset : Bool;
    i_PermissiveOk : Bool;
    i_RunFb : Bool;
    i_FaultFb : Bool;
END_VAR
VAR_OUTPUT
    q_RunCmd : Bool;
    q_Fault : Bool;
    q_Ready : Bool;
END_VAR
VAR
    stat_RunReq : Bool;
    stat_StartTon : TON_TIME;
END_VAR
BEGIN
    IF #i_Reset THEN
        #q_Fault := FALSE;
        #stat_RunReq := FALSE;
    END_IF;
    IF #i_Start AND #i_PermissiveOk AND NOT #q_Fault THEN
        #stat_RunReq := TRUE;
    ELSIF #i_Stop OR NOT #i_PermissiveOk THEN
        #stat_RunReq := FALSE;
    END_IF;
    #stat_StartTon(IN := #stat_RunReq AND NOT #i_RunFb, PT := T#3s);
    IF #stat_StartTon.Q OR #i_FaultFb THEN
        #q_Fault := TRUE;
        #stat_RunReq := FALSE;
    END_IF;
    #q_RunCmd := #stat_RunReq;
    #q_Ready := #i_PermissiveOk AND NOT #q_Fault;
END_FUNCTION_BLOCK
'''


def siemens_valve_fb(contract: dict[str, Any]) -> str:
    name = contract["name"]
    return f'''// {safety_comment(contract)}
FUNCTION_BLOCK "FB_{name}"
{{ S7_Optimized_Access := 'TRUE' }}
VERSION : 0.1
VAR_INPUT
    i_OpenCmd : Bool;
    i_CloseCmd : Bool;
    i_OpenFb : Bool;
    i_CloseFb : Bool;
END_VAR
VAR_OUTPUT
    q_OpenCmd : Bool;
    q_Fault : Bool;
END_VAR
BEGIN
    IF #i_OpenCmd AND NOT #i_CloseCmd THEN
        #q_OpenCmd := TRUE;
    ELSIF #i_CloseCmd THEN
        #q_OpenCmd := FALSE;
    END_IF;
    IF (#q_OpenCmd AND NOT #i_OpenFb AND #i_CloseFb) OR (NOT #q_OpenCmd AND NOT #i_CloseFb AND #i_OpenFb) THEN
        #q_Fault := TRUE;
    END_IF;
END_FUNCTION_BLOCK
'''


def siemens_analog_fb(contract: dict[str, Any]) -> str:
    name = contract["name"]
    return f'''// {safety_comment(contract)}
FUNCTION_BLOCK "FB_{name}"
{{ S7_Optimized_Access := 'TRUE' }}
VERSION : 0.1
VAR_INPUT
    i_Raw : Real;
    i_RawMin : Real;
    i_RawMax : Real;
    i_EuMin : Real;
    i_EuMax : Real;
END_VAR
VAR_OUTPUT
    q_Pv : Real;
    q_Fault : Bool;
END_VAR
VAR_TEMP
    temp_RawSpan : Real;
    temp_EuSpan : Real;
END_VAR
BEGIN
    #temp_RawSpan := #i_RawMax - #i_RawMin;
    #temp_EuSpan := #i_EuMax - #i_EuMin;
    IF #temp_RawSpan = 0.0 THEN
        #q_Pv := #i_EuMin;
        #q_Fault := TRUE;
    ELSE
        #q_Pv := ((#i_Raw - #i_RawMin) / #temp_RawSpan) * #temp_EuSpan + #i_EuMin;
        #q_Fault := FALSE;
    END_IF;
END_FUNCTION_BLOCK
'''


def siemens_udt(contract: dict[str, Any]) -> str:
    name = contract["name"]
    dtype = contract["device_type"]
    if dtype == "motor":
        body = """Cmd_Start : Bool;\n    Cmd_Stop : Bool;\n    Cmd_Reset : Bool;\n    Sts_Run : Bool;\n    Sts_Ready : Bool;\n    Sts_Fault : Bool;"""
    elif dtype == "valve":
        body = """Cmd_Open : Bool;\n    Cmd_Close : Bool;\n    Sts_Opened : Bool;\n    Sts_Closed : Bool;\n    Sts_Fault : Bool;"""
    else:
        unit = contract.get("units", {}).get("pv", "EU")
        body = f"""RawValue : Real;\n    Pv : Real;\n    Sp : Real;\n    UnitText : String[16] := '{unit}';\n    Fault : Bool;"""
    return f'''TYPE "UDT_{name}"\nVERSION : 0.1\n   STRUCT\n    {body}\n    {safety_fields_text(contract, 'siemens')}\n   END_STRUCT\nEND_TYPE\n'''


# ---------------- Rockwell ----------------
def rockwell_motor_code(contract: dict[str, Any]) -> str:
    name = contract["name"]
    return f'''// {safety_comment(contract)}
// AOI / routine moteur standard {name}
IF ResetCmd THEN
    Fault := 0;
    RunCmd := 0;
END_IF;
IF StartCmd AND PermissiveOk AND NOT Fault THEN
    RunCmd := 1;
END_IF;
IF StopCmd OR NOT PermissiveOk THEN
    RunCmd := 0;
END_IF;
StartTmr.PRE := 3000;
StartTmr.TimerEnable := RunCmd AND NOT RunFb;
TON(StartTmr);
IF StartTmr.DN OR FaultFb THEN
    Fault := 1;
    RunCmd := 0;
END_IF;
Ready := PermissiveOk AND NOT Fault;
'''


def rockwell_valve_code(contract: dict[str, Any]) -> str:
    name = contract["name"]
    return f'''// {safety_comment(contract)}
// AOI / routine vanne standard {name}
IF OpenCmd AND NOT CloseCmd THEN
    OpenOut := 1;
ELSIF CloseCmd THEN
    OpenOut := 0;
END_IF;
IF (OpenOut AND NOT OpenFb AND CloseFb) OR (NOT OpenOut AND NOT CloseFb AND OpenFb) THEN
    Fault := 1;
END_IF;
'''


def rockwell_analog_code(contract: dict[str, Any]) -> str:
    name = contract["name"]
    return f'''// {safety_comment(contract)}
// Routine analogique standard {name}
RawSpan := RawMax - RawMin;
EuSpan := EuMax - EuMin;
IF RawSpan <> 0.0 THEN
    Pv := ((RawValue - RawMin) / RawSpan) * EuSpan + EuMin;
    Fault := 0;
ELSE
    Pv := EuMin;
    Fault := 1;
END_IF;
'''


def rockwell_udt(contract: dict[str, Any]) -> str:
    name = contract["name"]
    dtype = contract["device_type"]
    if dtype == "motor":
        body = """Cmd_Start : BOOL;\n    Cmd_Stop : BOOL;\n    Cmd_Reset : BOOL;\n    Sts_Run : BOOL;\n    Sts_Ready : BOOL;\n    Sts_Fault : BOOL;"""
    elif dtype == "valve":
        body = """Cmd_Open : BOOL;\n    Cmd_Close : BOOL;\n    Sts_Opened : BOOL;\n    Sts_Closed : BOOL;\n    Sts_Fault : BOOL;"""
    else:
        body = """RawValue : REAL;\n    Pv : REAL;\n    Sp : REAL;\n    Fault : BOOL;"""
    return f'''TYPE UDT_{name} :\nSTRUCT\n    {body}\n    {safety_fields_text(contract, 'rockwell')}\nEND_STRUCT;\nEND_TYPE;\n'''


def make_l5x_routine(name: str, code: str) -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="35.00" TargetName="{name}" TargetType="Routine">
  <Controller Name="GeneratedController">
    <Programs>
      <Program Name="MainProgram">
        <Routines>
          <Routine Name="{name}" Type="StructuredText">
            <Content>{cdata(code)}</Content>
          </Routine>
        </Routines>
      </Program>
    </Programs>
  </Controller>
</RSLogix5000Content>
'''


def make_l5x_udt(name: str, udt_text: str) -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="35.00" TargetName="UDT_{name}" TargetType="DataType">
  <Controller Name="GeneratedController">
    <DataTypes>
      <DataType Name="UDT_{name}">
        <Description>{cdata(udt_text)}</Description>
      </DataType>
    </DataTypes>
  </Controller>
</RSLogix5000Content>
'''


# ---------------- Schneider ----------------
def schneider_motor_code(contract: dict[str, Any]) -> str:
    name = contract["name"]
    return f'''(* {safety_comment(contract)} *)
(* DFB_{name} *)
IF i_Reset THEN
    stat_Fault := FALSE;
    stat_RunReq := FALSE;
END_IF;
IF i_Start AND i_PermissiveOk AND NOT stat_Fault THEN
    stat_RunReq := TRUE;
ELSIF i_Stop OR NOT i_PermissiveOk THEN
    stat_RunReq := FALSE;
END_IF;
stat_Timer_Feedback(IN := stat_RunReq AND NOT i_RunFb, PT := t#3s);
IF stat_Timer_Feedback.Q OR i_FaultFb THEN
    stat_Fault := TRUE;
    stat_RunReq := FALSE;
END_IF;
q_RunCmd := stat_RunReq;
q_Fault := stat_Fault;
'''


def schneider_valve_code(contract: dict[str, Any]) -> str:
    name = contract["name"]
    return f'''(* {safety_comment(contract)} *)
(* DFB_{name} *)
IF i_OpenCmd AND NOT i_CloseCmd THEN
    q_OpenCmd := TRUE;
ELSIF i_CloseCmd THEN
    q_OpenCmd := FALSE;
END_IF;
IF (q_OpenCmd AND NOT i_OpenFb AND i_CloseFb) OR (NOT q_OpenCmd AND NOT i_CloseFb AND i_OpenFb) THEN
    q_Fault := TRUE;
END_IF;
'''


def schneider_analog_code(contract: dict[str, Any]) -> str:
    name = contract["name"]
    return f'''(* {safety_comment(contract)} *)
(* DFB_{name} *)
temp_RawSpan := i_RawMax - i_RawMin;
temp_EuSpan := i_EuMax - i_EuMin;
IF temp_RawSpan = 0.0 THEN
    q_Pv := i_EuMin;
    q_Fault := TRUE;
ELSE
    q_Pv := ((i_Raw - i_RawMin) / temp_RawSpan) * temp_EuSpan + i_EuMin;
    q_Fault := FALSE;
END_IF;
'''


def schneider_ddt(contract: dict[str, Any]) -> str:
    name = contract["name"]
    dtype = contract["device_type"]
    if dtype == "motor":
        body = """bCmd_Start : BOOL;\n    bCmd_Stop : BOOL;\n    bCmd_Reset : BOOL;\n    bSts_Run : BOOL;\n    bSts_Ready : BOOL;\n    bSts_Fault : BOOL;"""
    elif dtype == "valve":
        body = """bCmd_Open : BOOL;\n    bCmd_Close : BOOL;\n    bSts_Opened : BOOL;\n    bSts_Closed : BOOL;\n    bSts_Fault : BOOL;"""
    else:
        body = """rRawValue : REAL;\n    rPv : REAL;\n    rSp : REAL;\n    bFault : BOOL;"""
    return f'''TYPE T_{name} :\nSTRUCT\n    {body}\n    {safety_fields_text(contract, 'schneider')}\nEND_STRUCT\nEND_TYPE\n'''


def make_xmy(name: str, code: str) -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<FBExchangeFile>
  <fileHeader company="Schneider Automation" product="Unity Pro" version="14.1"/>
  <contentHeader name="{name}" version="1.0.0">
    <comment>Generated from JSON contract</comment>
  </contentHeader>
  <FBBlock nameType="{name}" FBKind="UserAssociated">
    <STSource name="Logic">{cdata(code)}</STSource>
  </FBBlock>
</FBExchangeFile>
'''


# ---------------- PLCopen vendors: Beckhoff / Omron / WAGO ----------------
def plcopen_generic_code(contract: dict[str, Any]) -> str:
    dtype = contract["device_type"]
    name = contract["name"]
    if dtype == "motor":
        return f'''(* {safety_comment(contract)} *)
(* FB_{name} *)
IF i_Reset THEN
    q_Fault := FALSE;
    stat_RunReq := FALSE;
END_IF;
IF i_Start AND i_PermissiveOk AND NOT q_Fault THEN
    stat_RunReq := TRUE;
ELSIF i_Stop OR NOT i_PermissiveOk THEN
    stat_RunReq := FALSE;
END_IF;
q_RunCmd := stat_RunReq;
'''
    if dtype == "valve":
        return f'''(* {safety_comment(contract)} *)
(* FB_{name} *)
IF i_OpenCmd AND NOT i_CloseCmd THEN
    q_OpenCmd := TRUE;
ELSIF i_CloseCmd THEN
    q_OpenCmd := FALSE;
END_IF;
'''
    return f'''(* {safety_comment(contract)} *)
(* FB_{name} *)
rawSpan := i_RawMax - i_RawMin;
IF rawSpan = 0.0 THEN
    q_Pv := i_EuMin;
    q_Fault := TRUE;
ELSE
    q_Pv := ((i_Raw - i_RawMin) / rawSpan) * (i_EuMax - i_EuMin) + i_EuMin;
    q_Fault := FALSE;
END_IF;
'''


def plcopen_struct(contract: dict[str, Any], vendor: str) -> str:
    name = contract["name"]
    dtype = contract["device_type"]
    if dtype == "motor":
        body = """bCmdStart : BOOL;\n    bCmdStop : BOOL;\n    bCmdReset : BOOL;\n    bRun : BOOL;\n    bFault : BOOL;"""
    elif dtype == "valve":
        body = """bCmdOpen : BOOL;\n    bCmdClose : BOOL;\n    bOpened : BOOL;\n    bClosed : BOOL;\n    bFault : BOOL;"""
    else:
        body = """rRawValue : REAL;\n    rPv : REAL;\n    rSp : REAL;\n    bFault : BOOL;"""
    return f'''TYPE ST_{vendor.upper()}_{name} :\nSTRUCT\n    {body}\n    {safety_fields_text(contract, 'schneider')}\nEND_STRUCT\nEND_TYPE\n'''


def make_plcopen(name: str, code: str) -> str:
    return f'''<?xml version="1.0" encoding="utf-8"?>
<project xmlns="http://www.plcopen.org/xml/tc6_0201"
         xmlns:xhtml="http://www.w3.org/1999/xhtml"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <fileHeader companyName="Actemium" productName="Helios Agent" productVersion="1.0" creationDateTime="2026-06-30T12:00:00"/>
  <contentHeader name="{name}"/>
  <types>
    <pous>
      <pou name="{name}" pouType="functionBlock">
        <interface/>
        <body>
          <ST>
            <xhtml:p>{cdata(code)}</xhtml:p>
          </ST>
        </body>
      </pou>
    </pous>
  </types>
  <instances><configurations/></instances>
</project>
'''


# ---------------- Ignition / SCADA generation ----------------
def ignition_tags(contract: dict[str, Any]) -> list[dict[str, Any]]:
    name = contract["name"]
    dtype = contract["device_type"]
    scada = contract["scada"]
    safety = contract["safety"]
    packml = contract["packml"]

    tags = [
        {
            "name": name,
            "tagType": "Folder",
            "tags": [
                {"name": "Cmd", "tagType": "Folder", "tags": []},
                {"name": "Sts", "tagType": "Folder", "tags": []},
                {"name": "Alm", "tagType": "Folder", "tags": [{"name": a, "tagType": "Memory", "dataType": "Boolean", "value": False} for a in contract.get("alarms", [])]},
                {"name": "Safety", "tagType": "Folder", "tags": [
                    {"name": "Enabled", "tagType": "Memory", "dataType": "Boolean", "value": bool(safety["enabled"])},
                    {"name": "ResetRequired", "tagType": "Memory", "dataType": "Boolean", "value": bool(safety["reset_required"])},
                    {"name": "Zone", "tagType": "Memory", "dataType": "String", "value": safety["zone"]},
                    {"name": "PLr", "tagType": "Memory", "dataType": "String", "value": safety["plr"]},
                    {"name": "SIL", "tagType": "Memory", "dataType": "String", "value": safety["sil"]},
                ]},
            ],
        }
    ]

    if dtype == "motor":
        tags[0]["tags"][0]["tags"] = [{"name": "Start", "tagType": "Memory", "dataType": "Boolean", "value": False}, {"name": "Stop", "tagType": "Memory", "dataType": "Boolean", "value": False}, {"name": "Reset", "tagType": "Memory", "dataType": "Boolean", "value": False}]
        tags[0]["tags"][1]["tags"] = [{"name": "Run", "tagType": "Memory", "dataType": "Boolean", "value": False}, {"name": "Ready", "tagType": "Memory", "dataType": "Boolean", "value": True}, {"name": "Fault", "tagType": "Memory", "dataType": "Boolean", "value": False}]
    elif dtype == "valve":
        tags[0]["tags"][0]["tags"] = [{"name": "Open", "tagType": "Memory", "dataType": "Boolean", "value": False}, {"name": "Close", "tagType": "Memory", "dataType": "Boolean", "value": False}]
        tags[0]["tags"][1]["tags"] = [{"name": "Opened", "tagType": "Memory", "dataType": "Boolean", "value": False}, {"name": "Closed", "tagType": "Memory", "dataType": "Boolean", "value": True}, {"name": "Fault", "tagType": "Memory", "dataType": "Boolean", "value": False}]
    else:
        tags[0]["tags"][0]["tags"] = [{"name": "Sp", "tagType": "Memory", "dataType": "Float4", "value": 0.0}]
        tags[0]["tags"][1]["tags"] = [{"name": "Pv", "tagType": "Memory", "dataType": "Float4", "value": 0.0}, {"name": "Fault", "tagType": "Memory", "dataType": "Boolean", "value": False}, {"name": "Unit", "tagType": "Memory", "dataType": "String", "value": contract.get("units", {}).get("pv", "EU")}]

    if packml.get("enabled"):
        tags[0]["tags"].append({
            "name": "PackML",
            "tagType": "Folder",
            "tags": [
                {"name": "StateCurrent", "tagType": "Memory", "dataType": "Int4", "value": 2},
                {"name": "StateName", "tagType": "Memory", "dataType": "String", "value": "STOPPED"},
                {"name": "UnitMode", "tagType": "Memory", "dataType": "String", "value": packml.get("unit_mode", "production")},
                {"name": "ProdProcessedCount", "tagType": "Memory", "dataType": "Int4", "value": 0},
                {"name": "ProdDefectiveCount", "tagType": "Memory", "dataType": "Int4", "value": 0},
                {"name": "RunTimeMin", "tagType": "Memory", "dataType": "Float4", "value": 0.0},
                {"name": "StopTimeMin", "tagType": "Memory", "dataType": "Float4", "value": 0.0},
                {"name": "AvailabilityPct", "tagType": "Memory", "dataType": "Float4", "value": 0.0},
                {"name": "PerformancePct", "tagType": "Memory", "dataType": "Float4", "value": 0.0},
                {"name": "QualityPct", "tagType": "Memory", "dataType": "Float4", "value": 0.0},
                {"name": "OEEPct", "tagType": "Memory", "dataType": "Float4", "value": 0.0},
            ],
        })

    tags[0]["metadata"] = {"provider": scada.get("provider", "default"), "tag_root": scada.get("tag_root")}
    return tags


def ignition_udt_stub(contract: dict[str, Any]) -> dict[str, Any]:
    name = contract["name"]
    dtype = contract["device_type"]
    return {
        "name": f"UDT_{name}",
        "device_type": dtype,
        "members": list(contract.get("io", {}).keys()) + ["alarms", "permissives", "safety", "packml"],
    }


def ignition_sequence_stub(contract: dict[str, Any]) -> str:
    name = contract["name"]
    packml = contract["packml"]
    if not packml.get("enabled"):
        return "# PackML disabled\n"
    return (
        f"# PackML / Sequence stub for {name}\n\n"
        f"- State model: {packml.get('state_model', 'packml')}\n"
        f"- Unit mode: {packml.get('unit_mode', 'production')}\n"
        f"- Recommended states: STOPPED -> RESETTING -> IDLE -> STARTING -> EXECUTE\n"
        f"- OEE counters: ProdProcessedCount / ProdDefectiveCount / RunTime / StopTime\n"
    )


def wincc_unified_stub(contract: dict[str, Any]) -> str:
    name = contract["name"]
    dtype = contract["device_type"]
    scada = contract["scada"]
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<WinCCUnifiedExport>
  <Faceplate name="FP_{name}">
    <Header title="{name}" subtitle="{dtype}" />
    <Tag name="CmdPath" value="{scada.get('cmd_path', '')}" />
    <Tag name="StsPath" value="{scada.get('sts_path', '')}" />
    <Tag name="AlmPath" value="{scada.get('alm_path', '')}" />
    <Section name="Summary" />
    <Section name="Commands" />
    <Section name="Status" />
    <Section name="Alarms" />
    <Section name="Safety" />
    <Section name="Diagnostics" />
  </Faceplate>
</WinCCUnifiedExport>
'''


def wincc_alarm_classes_stub(contract: dict[str, Any]) -> str:
    name = contract["name"]
    alarms = contract.get("alarms", [])
    rows = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>", "<AlarmClasses>"]
    for alarm in alarms:
        rows.append(f'  <AlarmClass equipment="{name}" name="{alarm}" priority="Medium" ackRequired="true" />')
    rows.append("</AlarmClasses>")
    return "\n".join(rows) + "\n"


def wincc_navigation_stub(contract: dict[str, Any]) -> str:
    name = contract["name"]
    rows = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>", "<Navigation>"]
    rows.append(f'  <Screen name="{name}_Overview" type="overview" equipment="{name}" />')
    rows.append(f'  <Screen name="{name}_Detail" type="detail" equipment="{name}" />')
    rows.append(f'  <Screen name="{name}_Alarms" type="alarms" equipment="{name}" />')
    rows.append(f'  <Screen name="{name}_OEE" type="oee" equipment="{name}" />')
    rows.append(f'  <Screen name="{name}_Historian" type="historian" equipment="{name}" />')
    rows.append("</Navigation>")
    return "\n".join(rows) + "\n"


def wincc_historian_view_stub(contract: dict[str, Any]) -> str:
    name = contract["name"]
    unit = contract.get("units", {}).get("pv", "EU")
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<HistorianView equipment="{name}">
  <Trend name="{name}_PV" unit="{unit}" />
  <Trend name="{name}_State" unit="state" />
  <Trend name="{name}_OEE" unit="percent" />
</HistorianView>
'''


def wincc_oee_view_stub(contract: dict[str, Any]) -> str:
    name = contract["name"]
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<OEEView equipment="{name}">
  <Metric name="AvailabilityPct" />
  <Metric name="PerformancePct" />
  <Metric name="QualityPct" />
  <Metric name="OEEPct" />
  <Counter name="ProdProcessedCount" />
  <Counter name="ProdDefectiveCount" />
</OEEView>
'''


def intouch_csv_stub(contract: dict[str, Any]) -> str:
    name = contract["name"]
    scada = contract["scada"]
    rows = [
        'TagName,AccessName,ItemName,Comment',
        f'{name}_Cmd,PLC,{scada.get("cmd_path", "")},Command path',
        f'{name}_Sts,PLC,{scada.get("sts_path", "")},Status path',
        f'{name}_Alm,PLC,{scada.get("alm_path", "")},Alarm path',
        f'{name}_Safety,PLC,{scada.get("tag_root", "")}/Safety,Safety faceplate root',
        f'{name}_OEE,PLC,{scada.get("tag_root", "")}/PackML/OEEPct,OEE value',
    ]
    return "\n".join(rows) + "\n"


def intouch_alarm_classes_csv(contract: dict[str, Any]) -> str:
    name = contract["name"]
    rows = ['AlarmClass,Priority,AckRequired,Tag']
    for alarm in contract.get('alarms', []):
        rows.append(f'{name}_{alarm},Medium,Yes,{name}_Alm')
    return "\n".join(rows) + "\n"


def intouch_navigation_csv(contract: dict[str, Any]) -> str:
    name = contract['name']
    rows = [
        'Screen,Type,Equipment,Target',
        f'{name}_Overview,overview,{name},{name}_Detail',
        f'{name}_Detail,detail,{name},{name}_Alarms',
        f'{name}_Alarms,alarms,{name},{name}_OEE',
        f'{name}_OEE,oee,{name},{name}_Historian',
        f'{name}_Historian,historian,{name},{name}_Overview',
    ]
    return "\n".join(rows) + "\n"


def intouch_historian_csv(contract: dict[str, Any]) -> str:
    name = contract['name']
    unit = contract.get('units', {}).get('pv', 'EU')
    rows = [
        'Trend,Tag,Unit',
        f'{name}_PV,{name}_Sts,{unit}',
        f'{name}_State,{name}_Sts,state',
        f'{name}_OEE,{name}_OEE,percent',
    ]
    return "\n".join(rows) + "\n"


def intouch_oee_csv(contract: dict[str, Any]) -> str:
    name = contract['name']
    rows = [
        'Metric,Source',
        'AvailabilityPct,PackML/AvailabilityPct',
        'PerformancePct,PackML/PerformancePct',
        'QualityPct,PackML/QualityPct',
        'OEEPct,PackML/OEEPct',
        'ProdProcessedCount,PackML/ProdProcessedCount',
        'ProdDefectiveCount,PackML/ProdDefectiveCount',
    ]
    return "\n".join(rows) + "\n"


def safety_faceplate_stub(contract: dict[str, Any]) -> str:
    name = contract["name"]
    safety = contract["safety"]
    return (
        f"# Faceplate Safety - {name}\n\n"
        f"- Zone: {safety.get('zone')}\n"
        f"- PLr: {safety.get('plr')}\n"
        f"- SIL: {safety.get('sil')}\n"
        f"- STO: {safety.get('sto')}\n"
        f"- SS1: {safety.get('ss1')}\n"
        f"- SLS: {safety.get('sls')}\n"
        f"- Reset required: {safety.get('reset_required')}\n"
        f"- Standard HMI sections: summary / diagnostics / reset / acknowledgements\n"
    )


def hmi_mapping_stub(contract: dict[str, Any]) -> str:
    name = contract['name']
    scada = contract['scada']
    return (
        f"# Mapping HMI standardisé - {name}\n\n"
        f"- Cmd: {scada.get('cmd_path', '')}\n"
        f"- Sts: {scada.get('sts_path', '')}\n"
        f"- Alm: {scada.get('alm_path', '')}\n"
        f"- Provider: {scada.get('provider', 'default')}\n"
        f"- Platform: {scada.get('platform', 'ignition')}\n"
    )


# ---------------- PackML generation ----------------
def siemens_packml(contract: dict[str, Any]) -> str:
    name = contract["name"]
    return f'''FUNCTION_BLOCK "FB_{name}_PackML"
{{ S7_Optimized_Access := 'TRUE' }}
VERSION : 0.1
VAR_INPUT
    i_SC_Reset : Bool;
    i_SC_Start : Bool;
    i_SC_Stop : Bool;
    i_SC_Hold : Bool;
    i_SC_Unhold : Bool;
    i_SC_Abort : Bool;
    i_StateComplete : Bool;
END_VAR
VAR_OUTPUT
    q_StateCurrent : Int;
    q_StateName : String[20];
END_VAR
VAR
    stat_State : Int := 2;
END_VAR
BEGIN
    CASE #stat_State OF
        2: IF #i_SC_Reset THEN #stat_State := 15; END_IF;
        15: IF #i_StateComplete THEN #stat_State := 4; END_IF;
        4: IF #i_SC_Start THEN #stat_State := 3; END_IF;
        3: IF #i_StateComplete THEN #stat_State := 6; END_IF;
        6: IF #i_SC_Stop THEN #stat_State := 7; ELSIF #i_SC_Hold THEN #stat_State := 10; ELSIF #i_SC_Abort THEN #stat_State := 8; END_IF;
        7: IF #i_StateComplete THEN #stat_State := 2; END_IF;
        10: IF #i_StateComplete THEN #stat_State := 11; END_IF;
        11: IF #i_SC_Unhold THEN #stat_State := 12; END_IF;
        12: IF #i_StateComplete THEN #stat_State := 6; END_IF;
        8: IF #i_StateComplete THEN #stat_State := 9; END_IF;
    ELSE
        #stat_State := 2;
    END_CASE;
    #q_StateCurrent := #stat_State;
END_FUNCTION_BLOCK
'''


def rockwell_packml(contract: dict[str, Any]) -> str:
    name = contract["name"]
    return f'''// PackML skeleton for {name}
IF SC_Reset AND StateCurrent = 2 THEN
    StateCurrent := 15;
END_IF;
IF StateCurrent = 15 AND StateComplete THEN
    StateCurrent := 4;
END_IF;
IF StateCurrent = 4 AND SC_Start THEN
    StateCurrent := 3;
END_IF;
IF StateCurrent = 3 AND StateComplete THEN
    StateCurrent := 6;
END_IF;
IF StateCurrent = 6 AND SC_Stop THEN
    StateCurrent := 7;
END_IF;
'''


def schneider_packml(contract: dict[str, Any]) -> str:
    name = contract["name"]
    return f'''(* PackML skeleton for {name} *)
IF i_SC_Reset AND q_StateCurrent = 2 THEN
    q_StateCurrent := 15;
END_IF;
IF q_StateCurrent = 15 AND i_StateComplete THEN
    q_StateCurrent := 4;
END_IF;
IF q_StateCurrent = 4 AND i_SC_Start THEN
    q_StateCurrent := 3;
END_IF;
IF q_StateCurrent = 3 AND i_StateComplete THEN
    q_StateCurrent := 6;
END_IF;
IF q_StateCurrent = 6 AND i_SC_Stop THEN
    q_StateCurrent := 7;
END_IF;
'''


def plcopen_packml(contract: dict[str, Any], vendor: str) -> str:
    name = contract["name"]
    return f'''(* PackML skeleton for {vendor} / {name} *)
IF i_SC_Reset AND q_StateCurrent = 2 THEN
    q_StateCurrent := 15;
END_IF;
IF q_StateCurrent = 15 AND i_StateComplete THEN
    q_StateCurrent := 4;
END_IF;
IF q_StateCurrent = 4 AND i_SC_Start THEN
    q_StateCurrent := 3;
END_IF;
IF q_StateCurrent = 3 AND i_StateComplete THEN
    q_StateCurrent := 6;
END_IF;
'''


# ---------------- Mapping ----------------
def make_mapping(contract: dict[str, Any]) -> str:
    name = contract["name"]
    dtype = contract["device_type"]
    scada = contract.get("scada", {})
    mes = contract.get("mes", {})
    safety = contract.get("safety", {})
    packml = contract.get("packml", {})
    lines = [
        f"# Mapping généré - {name}",
        "",
        f"- Type: {dtype}",
        f"- Vendors: {', '.join(contract.get('vendors', []))}",
        "",
        "## PLC ↔ SCADA ↔ MES",
        "",
        "| Domaine | Champ | Valeur |",
        "|---|---|---|",
    ]
    for domain, payload in [("SCADA", scada), ("MES", mes)]:
        for key, value in payload.items():
            lines.append(f"| {domain} | {key} | {value} |")
    lines.extend(["", "## Permissifs"])
    for item in contract.get("permissives", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Alarmes"])
    for alarm in contract.get("alarms", []):
        lines.append(f"- {alarm}")
    lines.extend([
        "",
        "## Safety metadata",
        f"- enabled: {safety.get('enabled')}",
        f"- zone: {safety.get('zone')}",
        f"- PLr: {safety.get('plr')}",
        f"- SIL: {safety.get('sil')}",
        f"- STO: {safety.get('sto')}",
        f"- SS1: {safety.get('ss1')}",
        f"- SLS: {safety.get('sls')}",
        f"- reset_required: {safety.get('reset_required')}",
        "",
        "## PackML",
        f"- enabled: {packml.get('enabled')}",
        f"- mode: {packml.get('mode')}",
        f"- state_model: {packml.get('state_model')}",
        f"- unit_mode: {packml.get('unit_mode')}",
    ])
    return "\n".join(lines)


def generate_for_contract(contract: dict[str, Any], base_output: Path) -> None:
    name = contract["name"]
    dtype = contract["device_type"]
    vendors = contract["vendors"]
    packml_enabled = bool(contract.get("packml", {}).get("enabled"))

    if "siemens" in vendors:
        code = {"motor": siemens_motor_fb, "valve": siemens_valve_fb, "analog": siemens_analog_fb}[dtype](contract)
        write_file(base_output / "siemens" / f"FB_{name}.scl", code)
        write_file(base_output / "siemens" / f"UDT_{name}.scl", siemens_udt(contract))
        write_file(base_output / "siemens" / f"FB_{name}.xml", make_plcopen(name, code))
        if packml_enabled:
            packml_code = siemens_packml(contract)
            write_file(base_output / "siemens" / f"FB_{name}_PackML.scl", packml_code)
            write_file(base_output / "siemens" / f"FB_{name}_PackML.xml", make_plcopen(f"FB_{name}_PackML", packml_code))

    if "rockwell" in vendors:
        code = {"motor": rockwell_motor_code, "valve": rockwell_valve_code, "analog": rockwell_analog_code}[dtype](contract)
        write_file(base_output / "rockwell" / f"AOI_{name}.st", code)
        write_file(base_output / "rockwell" / f"UDT_{name}.st", rockwell_udt(contract))
        write_file(base_output / "rockwell" / f"AOI_{name}.l5x", make_l5x_routine(name, code))
        write_file(base_output / "rockwell" / f"UDT_{name}.l5x", make_l5x_udt(name, rockwell_udt(contract)))
        if packml_enabled:
            packml_code = rockwell_packml(contract)
            write_file(base_output / "rockwell" / f"AOI_{name}_PackML.st", packml_code)
            write_file(base_output / "rockwell" / f"AOI_{name}_PackML.l5x", make_l5x_routine(f"AOI_{name}_PackML", packml_code))

    if "schneider" in vendors:
        code = {"motor": schneider_motor_code, "valve": schneider_valve_code, "analog": schneider_analog_code}[dtype](contract)
        write_file(base_output / "schneider" / f"DFB_{name}.st", code)
        write_file(base_output / "schneider" / f"DDT_{name}.st", schneider_ddt(contract))
        write_file(base_output / "schneider" / f"DFB_{name}.xmy", make_xmy(name, code))
        if packml_enabled:
            packml_code = schneider_packml(contract)
            write_file(base_output / "schneider" / f"DFB_{name}_PackML.st", packml_code)
            write_file(base_output / "schneider" / f"DFB_{name}_PackML.xmy", make_xmy(f"DFB_{name}_PackML", packml_code))

    for vendor in sorted(VENDORS_WITH_PLCOPEN & set(vendors)):
        code = plcopen_generic_code(contract)
        write_file(base_output / vendor / f"FB_{name}.st", code)
        write_file(base_output / vendor / f"ST_{vendor.upper()}_{name}.st", plcopen_struct(contract, vendor))
        write_file(base_output / vendor / f"FB_{name}.xml", make_plcopen(name, code))
        if packml_enabled:
            packml_code = plcopen_packml(contract, vendor)
            write_file(base_output / vendor / f"FB_{name}_PackML.st", packml_code)
            write_file(base_output / vendor / f"FB_{name}_PackML.xml", make_plcopen(f"FB_{name}_PackML", packml_code))

    # Ignition / SCADA
    ignition_dir = base_output / "ignition"
    write_json(ignition_dir / f"tags_{name}.json", ignition_tags(contract))
    write_json(ignition_dir / f"udt_{name}.json", ignition_udt_stub(contract))
    write_file(ignition_dir / f"sequence_{name}.md", ignition_sequence_stub(contract))

    # WinCC / InTouch
    wincc_dir = base_output / "wincc"
    intouch_dir = base_output / "intouch"
    hmi_dir = base_output / "hmi"
    write_file(wincc_dir / f"faceplate_{name}.xml", wincc_unified_stub(contract))
    write_file(wincc_dir / f"alarm_classes_{name}.xml", wincc_alarm_classes_stub(contract))
    write_file(wincc_dir / f"navigation_{name}.xml", wincc_navigation_stub(contract))
    write_file(wincc_dir / f"oee_view_{name}.xml", wincc_oee_view_stub(contract))
    write_file(wincc_dir / f"historian_view_{name}.xml", wincc_historian_view_stub(contract))

    write_file(intouch_dir / f"tags_{name}.csv", intouch_csv_stub(contract))
    write_file(intouch_dir / f"alarm_classes_{name}.csv", intouch_alarm_classes_csv(contract))
    write_file(intouch_dir / f"navigation_{name}.csv", intouch_navigation_csv(contract))
    write_file(intouch_dir / f"oee_view_{name}.csv", intouch_oee_csv(contract))
    write_file(intouch_dir / f"historian_view_{name}.csv", intouch_historian_csv(contract))

    write_file(hmi_dir / f"safety_faceplate_{name}.md", safety_faceplate_stub(contract))
    write_file(hmi_dir / f"mapping_{name}.md", hmi_mapping_stub(contract))

    write_file(base_output / f"mapping_{name}.md", make_mapping(contract))


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: generate_standard_blocks.py <contract_or_batch.json>")
        return 1

    payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    contracts = [ensure_contract(c) for c in get_contracts(payload)]
    root_output = Path(payload.get("output_dir", contracts[0].get("output_dir", "./generated")))

    for contract in contracts:
        generate_for_contract(contract, root_output / contract["name"])

    print(f"Generated {len(contracts)} equipment contract(s) in {root_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
