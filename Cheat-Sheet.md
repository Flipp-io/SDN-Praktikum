# Wichtige Mininet-Befehle und hilfreiche Informationen

Login für die Mininet-VM:  
- Username: mininet
- Passwort: mininet  
---


Wenn ein Befehl mit "mininet>" beginnt, ist er in der Mininet-CLI auszuführen (in dem Terminal-Fester, in dem die Mininet-Topologie gestartet wurde). Wenn er mit "h1>" beginnt, ist er im Terminal-Fenster des Hosts h1 auszuführen.

Zwischen allen Hosts pingen:
```bash
mininet> pingall
```

Die Flowtable des Switches ausgeben:
```bash
mininet> dpctl dump-flows --color=always
```

Die Topologie beenden:
```bash
mininet> exit
```

