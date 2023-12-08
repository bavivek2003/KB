@echo off

@echo Disabling driver security prompts
c:\drivers\driversignpolicy 0 > nul

@echo Installing device drivers...
c:\drivers\devcon install c:\drivers\netkvm.inf "PCI\VEN_1AF4&DEV_1000&SUBSYS_00011AF4&REV_00" > nul
c:\drivers\devcon install c:\drivers\balloon.inf "PCI\VEN_1AF4&DEV_1002&SUBSYS_00051AF4&REV_00" > nul
@echo Drivers installed

@echo Re-enabling driver security prompts
c:\drivers\driversignpolicy 1 > nul

@echo We are now going to change the name of the network connection. Please check the current name of the connection.
@echo Please enter connection info

SET /P "old=Connection to be renamed: "
SET /P "new=New connection name: "
SET /P "ip=IP: "
SET /P "mask=Mask: "
SET /P "gw=Gateway: "
SET /P "dns1=DNS: "

netsh int set int name = "%old%" newname = "%new%" > nul
netsh int ip set add name="%new%" static %ip% %mask% %gw% 1 > nul
netsh int ip set dns "%new%" static %dns1% > nul

@echo Done!
@pause