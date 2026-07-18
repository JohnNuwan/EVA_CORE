# Template UDT moteur Rockwell (texte)

TYPE UDT_MOTOR :
STRUCT
    Cmd_Start : BOOL;
    Cmd_Stop : BOOL;
    Cmd_Reset : BOOL;
    Sts_Run : BOOL;
    Sts_Ready : BOOL;
    Sts_Fault : BOOL;
END_STRUCT;
END_TYPE;
