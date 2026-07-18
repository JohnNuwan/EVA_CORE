(* DFB_MotorStandard *)
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
q_Ready := i_PermissiveOk AND NOT stat_Fault;
