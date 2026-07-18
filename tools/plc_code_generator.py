#!/usr/bin/env python3
"""Module PLC Code Generator - Génère du code automate en ST à partir de templates."""
import json
import logging

logger = logging.getLogger(__name__)

_TEMPLATES = {
    "motor_start_stop": {
        "name": "Moteur Start/Stop",
        "language": "st",
        "description": "Bloc fonctionnel commande moteur avec interlocks",
        "code": (
            "FUNCTION_BLOCK FB_MotorControl\n"
            "VAR_INPUT\n"
            "    StartCmd : BOOL;\n"
            "    StopCmd : BOOL;\n"
            "    AutoMode : BOOL;\n"
            "    SafetyOK : BOOL;\n"
            "    ThermalOK : BOOL;\n"
            "END_VAR\n"
            "VAR_OUTPUT\n"
            "    Running : BOOL;\n"
            "    Fault : BOOL;\n"
            "    Status : WORD;\n"
            "END_VAR\n"
            "VAR\n"
            "    State : INT := 0;\n"
            "END_VAR\n"
            "BEGIN\n"
            "    CASE State OF\n"
            "    0: \n"
            "        Running := FALSE;\n"
            "        IF StartCmd AND AutoMode AND SafetyOK AND ThermalOK THEN\n"
            "            State := 1;\n"
            "        END_IF;\n"
            "    1:\n"
            "        Running := TRUE;\n"
            "        Status := 16#0001;\n"
            "        IF StopCmd OR NOT SafetyOK OR NOT ThermalOK THEN\n"
            "            State := 2;\n"
            "            Fault := TRUE;\n"
            "        END_IF;\n"
            "    2:\n"
            "        Running := FALSE;\n"
            "        Status := 16#0002;\n"
            "        IF SafetyOK AND ThermalOK AND NOT StopCmd THEN\n"
            "            State := 0;\n"
            "            Fault := FALSE;\n"
            "        END_IF;\n"
            "    END_CASE;\n"
            "END_FUNCTION_BLOCK"
        )
    },
    "pid_loop": {
        "name": "Boucle PID",
        "language": "st",
        "description": "Implémentation PID",
        "code": (
            "FUNCTION_BLOCK FB_PID\n"
            "VAR_INPUT\n"
            "    PV : REAL;\n"
            "    SP : REAL;\n"
            "    Gain : REAL;\n"
            "    Ti : REAL;\n"
            "    Td : REAL;\n"
            "    CycleTime : TIME := T#1S;\n"
            "END_VAR\n"
            "VAR_OUTPUT\n"
            "    Output : REAL := 0.0;\n"
            "    OutputMin : REAL;\n"
            "    OutputMax : REAL;\n"
            "END_VAR\n"
            "VAR\n"
            "    Error : REAL;\n"
            "    Integral : REAL;\n"
            "    Derivative : REAL;\n"
            "    PrevError : REAL;\n"
            "    dt : REAL;\n"
            "END_VAR\n"
            "BEGIN\n"
            "    dt := TIME_TO_REAL(CycleTime);\n"
            "    Error := SP - PV;\n"
            "    Integral := Integral + Error * dt;\n"
            "    Derivative := (Error - PrevError) / dt;\n"
            "    Output := Gain * (Error + Integral / Ti + Td * Derivative);\n"
            "    Output := MAX(OutputMin, MIN(OutputMax, Output));\n"
            "    PrevError := Error;\n"
            "END_FUNCTION_BLOCK"
        )
    },
    "analog_scaling": {
        "name": "Scaling Analogique",
        "language": "st",
        "description": "Conversion 4-20mA vers engineering",
        "code": (
            "FUNCTION FC_ScaleAnalog : REAL\n"
            "VAR_INPUT\n"
            "    RawValue : INT;\n"
            "    RawMin : INT := 0;\n"
            "    RawMax : INT := 27648;\n"
            "    EngMin : REAL;\n"
            "    EngMax : REAL;\n"
            "END_VAR\n"
            "BEGIN\n"
            "    FC_ScaleAnalog := INT_TO_REAL(RawValue - RawMin) / INT_TO_REAL(RawMax - RawMin) * (EngMax - EngMin) + EngMin;\n"
            "END_FUNCTION"
        )
    },
    "valve_control": {
        "name": "Commande Vanne",
        "language": "st",
        "description": "Bloc fonctionnel de commande de vanne tout-ou-rien avec capteurs de fin de course",
        "code": (
            "FUNCTION_BLOCK FB_ValveControl\n"
            "VAR_INPUT\n"
            "    OpenCmd : BOOL;\n"
            "    CloseCmd : BOOL;\n"
            "    FbkOpen : BOOL;\n"
            "    FbkClosed : BOOL;\n"
            "    SafetyInterlock : BOOL;\n"
            "END_VAR\n"
            "VAR_OUTPUT\n"
            "    CtrlOpen : BOOL;\n"
            "    CtrlClose : BOOL;\n"
            "    Fault : BOOL;\n"
            "    Status : WORD;\n"
            "END_VAR\n"
            "VAR\n"
            "    TimerLimit : TON;\n"
            "END_VAR\n"
            "BEGIN\n"
            "    IF NOT SafetyInterlock THEN\n"
            "        CtrlOpen := FALSE;\n"
            "        CtrlClose := FALSE;\n"
            "        Fault := TRUE;\n"
            "        Status := 16#0003;\n"
            "    ELSE\n"
            "        CtrlOpen := OpenCmd AND NOT CloseCmd;\n"
            "        CtrlClose := CloseCmd AND NOT OpenCmd;\n"
            "        TimerLimit(IN := (CtrlOpen AND NOT FbkOpen) OR (CtrlClose AND NOT FbkClosed), PT := T#5S);\n"
            "        Fault := TimerLimit.Q;\n"
            "        IF Fault THEN\n"
            "            Status := 16#0002;\n"
            "        ELIF FbkOpen AND NOT FbkClosed THEN\n"
            "            Status := 16#0001;\n"
            "        ELIF FbkClosed AND NOT FbkOpen THEN\n"
            "            Status := 16#0000;\n"
            "        ELSE\n"
            "            Status := 16#0004;\n"
            "        END_IF;\n"
            "    END_IF;\n"
            "END_FUNCTION_BLOCK"
        )
    },
    "alarm_management": {
        "name": "Gestion Alarme",
        "language": "st",
        "description": "Gestionnaire d'alarmes industrielles avec acquittement et réinitialisation",
        "code": (
            "FUNCTION_BLOCK FB_AlarmManager\n"
            "VAR_INPUT\n"
            "    Trigger : BOOL;\n"
            "    Ack : BOOL;\n"
            "    Reset : BOOL;\n"
            "END_VAR\n"
            "VAR_OUTPUT\n"
            "    Active : BOOL;\n"
            "    Unacknowledged : BOOL;\n"
            "    OutputCmd : BOOL;\n"
            "END_VAR\n"
            "VAR\n"
            "    TriggeredState : BOOL;\n"
            "END_VAR\n"
            "BEGIN\n"
            "    IF Trigger THEN\n"
            "        IF NOT TriggeredState THEN\n"
            "            TriggeredState := TRUE;\n"
            "            Unacknowledged := TRUE;\n"
            "        END_IF;\n"
            "    END_IF;\n"
            "    IF Ack AND Unacknowledged THEN\n"
            "        Unacknowledged := FALSE;\n"
            "    END_IF;\n"
            "    IF Reset AND NOT Trigger THEN\n"
            "        TriggeredState := FALSE;\n"
            "        Unacknowledged := FALSE;\n"
            "    END_IF;\n"
            "    Active := TriggeredState;\n"
            "    OutputCmd := Active;\n"
            "END_FUNCTION_BLOCK"
        )
    },
    "em_eph_udt": {
        "name": "UDT EM/EPH Interface",
        "language": "st",
        "description": "Type de données utilisateur UDT structurant les échanges EM/EPH",
        "code": (
            "TYPE UDT_EM_EPH_Interface :\n"
            "STRUCT\n"
            "    Command_Word : WORD;\n"
            "    Mode : INT;\n"
            "    Setpoint : REAL;\n"
            "    Status_Word : WORD;\n"
            "    Actual_Value : REAL;\n"
            "    Alarm_Active : BOOL;\n"
            "END_STRUCT\n"
            "END_TYPE"
        )
    }
}


def list_templates() -> str:
    """Liste tous les templates de code PLC disponibles.

    Returns:
        str: Liste des templates sérialisés au format JSON.
    """
    return json.dumps([{"key": k, **v} for k, v in _TEMPLATES.items()], indent=2, ensure_ascii=False)


def generate_st_code(template: str) -> str:
    """Génère le code Structured Text (ST) associé à un template donné.

    Args:
        template: Clé d'identification du template.

    Returns:
        str: Le code généré ou un dictionnaire d'erreur au format JSON.
    """
    if template not in _TEMPLATES:
        return json.dumps({"error": f"Template inconnu : {template}"}, ensure_ascii=False)
    return json.dumps({"template": template, "code": _TEMPLATES[template]["code"]}, indent=2, ensure_ascii=False)


from tools.registry import registry

registry.register(
    name="plc_code_list_templates",
    toolset="industrial",
    schema={
        "name": "plc_code_list_templates",
        "description": "Liste les templates code PLC.",
        "parameters": {"type": "object", "properties": {}}
    },
    handler=lambda a, **kw: list_templates(),
    is_async=False,
    description="Lister les templates PLC.",
    emoji="📚",
)

registry.register(
    name="plc_code_generate",
    toolset="industrial",
    schema={
        "name": "plc_code_generate",
        "description": "Génère du code Structured Text IEC 61131-3.",
        "parameters": {
            "type": "object",
            "properties": {
                "template": {
                    "type": "string",
                    "enum": list(_TEMPLATES.keys()),
                    "description": "Template à générer"
                }
            },
            "required": ["template"]
        }
    },
    handler=lambda a, **kw: generate_st_code(a.get("template", "")),
    is_async=False,
    description="Générer du code PLC ST.",
    emoji="⚡",
)