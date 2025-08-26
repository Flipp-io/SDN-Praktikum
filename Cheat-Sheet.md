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

Falls hängen geblieben:
```bash
sudo mn -c
```

## Orientierung in der Mininet-CLI
```bash
mininet> help          # Überblick
mininet> nodes         # Hosts/Switches
mininet> net           # Links
mininet> intfs         # Interfaces
mininet> dump          # Details (IP/MAC/Intfs)
mininet> sh <cmd>      # Shell-Befehl aus Mininet heraus
mininet> py <expr>     # Kurz-Python (z.B. net.hosts)
```

## Arbeiten im Host-Namespace
```bash
mininet> h1 ip addr             # IP/MAC prüfen
mininet> h1 ip route            # Routing
mininet> h1 ip neigh            # ARP
mininet> h1 ip neigh flush all  # ARP leeren
```
