echo save logs to './Push&Shutdown.log'
del ./Push&Shutdown.log

echo %date% %time%: shutdown > ./Push&Shutdown.log
shutdown -s -t 0
