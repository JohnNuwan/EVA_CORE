# Template RAPID ABB pick and place

MODULE MainModule
    PROC main()
        WaitDI di_PLC_Start, 1;
        SetDO do_Robot_Busy, 1;
        MoveJ pHome, v1000, fine, tTool;
        MoveJ Offs(pPick,0,0,100), v1000, z50, tTool;
        MoveL pPick, v500, fine, tTool;
        SetDO do_GripperClose, 1;
        WaitDI di_GripperClosed, 1;
        MoveL Offs(pPick,0,0,100), v1000, z50, tTool;
        MoveJ Offs(pDrop,0,0,100), v1000, z50, tTool;
        MoveL pDrop, v500, fine, tTool;
        SetDO do_GripperClose, 0;
        SetDO do_Robot_Busy, 0;
        SetDO do_Robot_Done, 1;
    ENDPROC
ENDMODULE
