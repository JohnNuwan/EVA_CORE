# Template DDT analogique Schneider

TYPE T_Analog_Standard :
STRUCT
    iRawValue : INT;
    rPv : REAL;
    rSp : REAL;
    bFault : BOOL;
    bHiAlarm : BOOL;
    bLoAlarm : BOOL;
END_STRUCT
END_TYPE
