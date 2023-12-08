@echo off
@echo installing Qemu agent...
msiexec /i c:\drivers\qemu-ga-x86.msi /quiet /qn /norestart
@echo Done!

@echo Disabling driver security prompts
c:\drivers\driversignpolicy 0 > nul

@echo Installing device drivers...
c:\drivers\devcon install c:\drivers\vioscsi.inf "PCI\VEN_1AF4&DEV_1004&SUBSYS_00081AF4&REV_00" > nul
@echo Drivers installed

@echo Re-enabling driver security prompts
c:\drivers\driversignpolicy 1 > nul


@echo Quitting. Please shutdown before migration.
pause  
exit