// AOI / routine moteur standard Rockwell
// Inputs attendus: StartCmd, StopCmd, ResetCmd, PermissiveOk, RunFb, FaultFb
// Outputs attendus: RunCmd, Fault, Ready

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
