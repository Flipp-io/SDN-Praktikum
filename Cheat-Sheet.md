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
---

## Beispiel ACL-Regeln für POX-Firewall

### 1. Blockiere alle Verbindungen zu einer bestimmten IP-Adresse
```python
if dst == IPAddr("10.0.0.5"):
    return True
```
**Erläuterung:** Alle Pakete, die an die IP `10.0.0.5` gehen, werden blockiert.

### 2. Blockiere alle TCP-Verbindungen auf Port 22 (SSH)
```python
if proto == ipv4.TCP_PROTOCOL and dport == 22:
    return True
```
**Erläuterung:** Verhindert SSH-Zugriffe im Netzwerk.

### 3. Erlaube nur ICMP (Ping) innerhalb eines bestimmten Subnetzes
```python
if proto == ipv4.ICMP_PROTOCOL and src.inNetwork("192.168.1.0/24") and dst.inNetwork("192.168.1.0/24"):
    return False  # Durchlassen
elif proto == ipv4.ICMP_PROTOCOL:
    return True   # ICMP außerhalb des Subnetzes blockieren
```
**Erläuterung:** ICMP ist nur innerhalb des Subnetzes `192.168.1.0/24` erlaubt.

### 4. Blockiere alle UDP-Pakete mit Zielport 53 (DNS)
```python
if proto == ipv4.UDP_PROTOCOL and dport == 53:
    return True
```
**Erläuterung:** DNS-Anfragen werden blockiert.

### 5. Blockiere ausgehenden Traffic von einer bestimmten IP in ein anderes Subnetz
```python
if src == IPAddr("10.0.0.8") and dst.inNetwork("10.0.1.0/24"):
    return True
```
**Erläuterung:** Die IP `10.0.0.8` darf nicht ins Subnetz `10.0.1.0/24` kommunizieren.

### 6. Erlaube alles andere
```python
return False
```

_Weitere Beispiele finden sich im Deepdive!_

---

### Hinweise
- Die Reihenfolge der Bedingungen ist wichtig! Die erste zutreffende Regel entscheidet.
- Mit `src` und `dst` prüfst du Quell- und Ziel-IP.
- Mit `proto` prüfst du das Protokoll (TCP, UDP, ICMP, ...).
- Mit `dport` prüfst du den Ziel-Port (für TCP/UDP).
- Nutze `IPAddr("x.x.x.x")` und `.inNetwork("x.x.x.x/xx")` für IP- und Subnetzvergleiche.


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
