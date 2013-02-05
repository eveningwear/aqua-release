for %%i in (c, d ,e) do if exist %%i:\QMSClient\restAdm.py set PARTITION=%%i
echo set path=%path%;%SystemDrive%\Python25; > %PARTITION%:\QMSClient\startup.cmd
echo echo Please wait for network configuration for about 10 seconds >> %PARTITION%:\QMSClient\startup.cmd
echo ping 127.0.0.1 -n 10 -w 1000 >> %PARTITION%:\QMSClient\startup.cmd
echo %PARTITION%: >> %PARTITION%:\QMSClient\startup.cmd
echo ipconfig /renew >> %PARTITION%:\QMSClient\startup.cmd
echo cd \QMSClient >> %PARTITION%:\QMSClient\startup.cmd
echo %SystemDrive%\Python25\python.exe restAdm.py >> %PARTITION%:\QMSClient\startup.cmd
reg add HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v RestoreTool /d %PARTITION%:\QMSClient\startup.cmd /f
start /min %PARTITION%:\QMSClient\startup.cmd
del %SystemDrive%\runonce.cmd
exit