# SDN Deepdive: L3-Switch mit Firewall

Dieses Verzeichnis enthält fortgeschrittene SDN-Beispiele für Mininet und POX, insbesondere einen Layer-3-Switch mit integrierter Firewall und eine realistische Enterprise-Topologie.

## Features
- **L3-Switch mit Firewall:** Routing zwischen Subnetzen, ARP-Handling, zentrale ACL/Firewall-Logik, Flow-Installation
- **Enterprise-Topologie:** Mehrere Subnetze (intern, DMZ, extern, Server, Management) mit jeweils eigenem Switch und zentralem Router-Switch
- **Zentrale, dynamische Steuerung:** SDN-typische Policy-Änderungen im laufenden Betrieb

## Dateien
- `l3_switch_with_firewall.py`: POX-Controller mit L3-Routing und Firewall-Logik
- `enterprise_network_topo.py`: Mininet-Topologie mit mehreren Subnetzen und zentralem Router
- `firewall_help.py`: Beispiele und Hilfestellungen für Firewall/ACL-Regeln

## Nutzung
1. **Mininet-Topologie starten:**
   ```sh
   sudo mn --custom deepdive/enterprise_network_topo.py --topo enterprise --controller=remote,ip=127.0.0.1,port=6633 --mac -x
   ```
2. **POX-Controller starten:**
   ```sh
   ~/pox/pox.py l3_switch_with_firewall samples.pretty_log --DEBUG
   ```
3. **Hosts konfigurieren:**
   - Die Default-Gateways sind in der Topologie bereits gesetzt.
   - Prüfe mit `h1 route -n` etc.

4. **Tests:**
   - `h1 ping h2` (innerhalb Subnetz)
   - `h1 ping h8` (zwischen Subnetzen)
   - `h1 curl 10.2.1.100` (HTTP zu DMZ)
   - `h15 ping 10.1.1.10` (aus externem Netz, sollte geblockt werden)
   - `h1 ssh 10.2.1.100` (SSH zu DMZ, sollte geblockt werden)

## Beispiel: Firewall-Regeln
Die ACL-Regeln werden zentral im Controller gesetzt (siehe `_is_blocked_by_acl`).

```python
# HTTP zu DMZ erlauben
if dst == IPAddr("10.2.1.100") and proto == ipv4.TCP_PROTOCOL and dport == 80:
    return False
# Traffic aus externem Netz blockieren
if src.inNetwork("10.3.1.0/24"):
    return True
# SSH von intern zu DMZ blockieren
if src.inNetwork("10.1.1.0/24") and dst.inNetwork("10.2.1.0/24") and proto == ipv4.TCP_PROTOCOL and dport == 22:
    return True
```

## Vorteile von SDN (für die Demo)
- **Zentrale Steuerung:** Eine Codezeile im Controller ändert das Verhalten des gesamten Netzes.
- **Dynamik:** Regeln können im laufenden Betrieb angepasst werden.
- **Effizienz:** Geblockte Flows werden direkt auf Switch-Ebene installiert (Drop-Flow).

## Hinweise für Studierende
- Ihr könnt beliebige ACL-Regeln ergänzen oder ändern.
- Nutzt das Log für Debugging (`--DEBUG`).
- Probiert verschiedene Szenarien (HTTP, SSH, Ping, Subnetze, ...).
- Die Topologie und der Controller sind modular und können leicht erweitert werden.

## Vergleich L2 vs L3 Switch

| Feature | L2 Switch | L3 Switch |
|---------|-----------|-----------|
| **Routing** | MAC-basiert | IP-basiert |
| **Subnetze** | Ein Subnetz | Mehrere Subnetze |
| **ARP-Handling** | Einfach | Vollständig |
| **Firewall** | IP-basiert | Subnetz-basiert |
| **Skalierbarkeit** | Begrenzt | Hoch |
| **Komplexität** | Niedrig | Mittel |

## Sicherheitsfeatures

### Firewall-Funktionalität
- **ACL-Regeln:** Statische Zugriffskontrolllisten
- **Protokoll-Filterung:** TCP, UDP, ICMP
- **Port-basierte Regeln:** Spezifische Services
- **Subnetz-basierte Regeln:** Netzwerk-Segmentierung
- **Logging:** Detaillierte Firewall-Logs

### Enterprise-Sicherheit
- **DMZ-Isolation:** Öffentliche Server abgeschottet
- **Server-Farm-Schutz:** Datenbanken nur für Anwendungen
- **Management-Netzwerk:** Nur IT-Admins
- **Externe Zugriffe:** Eingeschränkt auf DMZ
- **Interne Kommunikation:** Rollenbasierte Zugriffe

## Anpassung der Firewall-Regeln

1. **Regeln kopieren:** Aus `enterprise_firewall_rules.py` in Controller
2. **IP-Adressen anpassen:** An deine Topologie anpassen
3. **Ports konfigurieren:** Services-spezifische Regeln
4. **Testen:** Mit Mininet-Szenarien validieren

---

## Deepdive: Erweiterte SDN-Implementierungen

Für fortgeschrittene Anwender und zusätzliche Experimente haben wir erweiterte SDN-Implementierungen im `deepdive/` Ordner erstellt.

### Verfügbare Erweiterungen

#### L2 Learning Switch mit Firewall
- **Datei:** `deepdive/l2_switch_with_firewall.py`
- **Features:** MAC-Learning + IP-basierte Firewall
- **Verwendung:** `~/pox/pox.py deepdive.l2_switch_with_firewall samples.pretty_log --DEBUG`

#### Layer 3 Switch mit Firewall  
- **Datei:** `deepdive/l3_switch_with_firewall.py`
- **Features:** IP-Routing + ARP-Handling + Subnetz-basierte Firewall
- **Verwendung:** `~/pox/pox.py deepdive.l3_switch_with_firewall samples.pretty_log --DEBUG`

#### Enterprise-Netzwerk Topologie
- **Datei:** `deepdive/enterprise_network_topo.py`
- **Features:** 27 Hosts in 5 Subnetzen (Büros, DMZ, Server-Farm, Management)
- **Verwendung:** `sudo mn --custom deepdive.enterprise_network_topo --topo enterprise --controller=remote,ip=127.0.0.1,port=6633 --mac -x`

### Hilfedateien
- **`deepdive/firewall_help.py`:** Umfassende Firewall-Regel Beispiele
- **`deepdive/enterprise_firewall_rules.py`:** Enterprise-spezifische Sicherheitsrichtlinien

### Dokumentation
Siehe `deepdive/README.md` für detaillierte Anleitungen, Demo-Szenarien und Vergleichstabellen.

### Demo-Szenarien
```bash
# Enterprise-Topologie mit L3 Switch
~/pox/pox.py l3_switch_with_firewall samples.pretty_log --DEBUG
sudo mn --custom enterprise_network_topo --topo enterprise --controller=remote,ip=127.0.0.1,port=6633 --mac -x

# Tests
mininet> h15 ping h8      # Externer → Webserver (erlaubt)
mininet> h15 ping h19     # Externer → MySQL (blockiert)
mininet> h1 ping h8       # Büro-Client → Webserver (erlaubt)
mininet> h6 ping h25      # IT-Admin → Monitoring (erlaubt)
```

Diese Erweiterungen demonstrieren die vollen möglichkeiten von SDN mit realistischen Enterprise-Szenarien und erweiterten Sicherheitsfunktionen.
