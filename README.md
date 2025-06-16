# SDN-Praktikum: SDN mit Mininet und POX
---

Dieses Repo pullen um die Dateien nicht händisch kopieren zu müssen.

## A. Mininet mit POX verwenden
Dieses erste Szenario soll helfen euch mit Mininet und Pox vertraut zu machen. Das Prinzip von SDN wird hier zunächst auf Layer 2 umgesetzt, indem ein Switch neue Flowtable-Einträge von einem Controller zugewiesen bekommt.

### 1. POX-Controller starten
```bash
cd ~/pox
./pox.py forwarding.l2_learning  samples.pretty_log --DEBUG
```

### 2. Mininet starten
In einer zweiten Bash:
```bash
sudo mn --topo=single,2 --controller=remote --mac
```
Die option "--mac" sorgt dafür, dass die Hosts einfach lesbare MAC-Adressen erhalten.

### 3. Testen mit `ping`
```bash
mininet> pingall
```
Achtet auch auf die Ausgabe des Controllers.

### 4. Flowtable des Switches ausgeben lassen
```bash
mininet> dpctl dump-flows
```
Findet ihr die MAC- und IP-Adressen der Hosts wieder? 
Was soll der Switch mit den Paketen dieses Flows machen?

---

## B. SDN-Firewall mit statischer ACL
In diesem Versuch sollt ihr eine einfache Firewall mit statischen Regeln implementieren, die eingehenden und ausgehenden Verkehr basierend auf IP-Adressen, Protokollen und Ports blockiert oder erlaubt. Die Filter-Regeln sollt ihr selbst festlegen und im Code umsetzen.

### Vorbereitung

#### Mininet-Topologie
Speichert folgendes als "custom_topo.py" ab oder pullt die Datei aus diesem Repo:
```bash
from mininet.topo import Topo

class SDNFirewallTopo(Topo):
    def build(self):
        # Switch
        s1 = self.addSwitch('s1')

        # Hosts
        h1 = self.addHost('h1', ip='10.0.0.1/24')  # interner Client
        h2 = self.addHost('h2', ip='10.0.0.2/24')  # Server
        h3 = self.addHost('h3', ip='10.0.0.3/24')  # externer Client

        # Links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)

topos = { 'sdnfirewall': (lambda: SDNFirewallTopo()) }
```
Diese Topologie enthält einen internen Client, einen Server und einen externen Client. Alle Hosts befinden sich im selben Subnetz (10.0.0.0/24).
Die Topologie kann mit diesem Befehl gestartet werden:
```bash
sudo mn --custom custom_topo.py --topo sdnfirewall --controller=remote --mac -x
```
Hinweis: 
'--mac' -> die Hosts erhalten einfcher zu lesende MAC-Adressen
'-x' -> Öffnet jeden Host in einem eigenem Terminal-Fenster.


#### POX-Modul
Der Großteil des Controller-Codes ist bereits für euch vorbereitet. Speichert folgendes als "pox_firewall_acl.py" ab (oder pullt es aus diesem Repo):
```bash
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet import ethernet, ipv4, tcp, udp, icmp
from pox.lib.addresses import IPAddr

log = core.getLogger()

class SimpleFirewall (object):
    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)
        log.info("Firewall-Controller verbunden mit %s", connection)

    def _handle_PacketIn(self, event):
        packet = event.parsed

        if not packet.parsed:
            log.warning("Unverständliches Paket")
            return

        ip_packet = packet.find('ipv4')
        if ip_packet is None:
            # Kein IP-Paket → z. B. ARP → durchlassen
            self._allow_packet(event)
            return

        # --- Sektion A: relevante Felder extrahieren ---
        # TODO: Studenten sollen Quell-/Ziel-IP, Protokoll, Ports extrahieren
        src_ip = ip_packet.srcip
        dst_ip = ip_packet.dstip
        proto = ip_packet.protocol

        src_port = None
        dst_port = None

        if proto == ipv4.ICMP_PROTOCOL:
            pass  # ICMP → keine Ports
        elif proto == ipv4.TCP_PROTOCOL:
            tcp_packet = packet.find('tcp')
            if tcp_packet:
                src_port = tcp_packet.srcport
                dst_port = tcp_packet.dstport
        elif proto == ipv4.UDP_PROTOCOL:
            udp_packet = packet.find('udp')
            if udp_packet:
                src_port = udp_packet.srcport
                dst_port = udp_packet.dstport

        # --- Sektion B: Entscheidung gemäß ACL ---
        # Sektion B: Entscheidung wird hier nur ausgeführt – keine Änderungen nötig.
        if self.is_blocked(src_ip, dst_ip, proto, dst_port):
            log.info("Blockiert: %s → %s (proto %s, port %s)", src_ip, dst_ip, proto, dst_port)
            return  # Paket wird nicht weitergeleitet
        else:
            log.info("Erlaubt: %s → %s", src_ip, dst_ip)
            self._allow_packet(event)

    # --- Sektion C: Statische ACL ---
    # TODO: Studenten sollen hier Regeln ergänzen
    def is_blocked(self, src, dst, proto, dport):
        # Beispiel: ICMP von externem Client blockieren
        if src == IPAddr("10.0.0.3") and proto == ipv4.ICMP_PROTOCOL:
            return True
        # Beispiel: TCP Port 22 (SSH) von extern blockieren
        if src == IPAddr("10.0.0.3") and proto == ipv4.TCP_PROTOCOL and dport == 22:
            return True
        return False

    def _allow_packet(self, event):
        # Flow installieren, damit Paket durchgeht
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(event.parsed)
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        msg.data = event.ofp
        self.connection.send(msg)

def launch():
    def start_switch(event):
        log.info("Starte Firewall auf %s", event.connection)
        SimpleFirewall(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)

```
Der Controller kann mit diesem Befehl gestartet werden:
```bash
./pox.py log.level --DEBUG pox_firewall_acl
```

### Durchführung

- Startet den Controller
```bash
./pox.py log.level --DEBUG pox_firewall_acl
```
- Startet die Mininet-Topologie
```bash
sudo mn --custom custom_topo.py --topo sdnfirewall --controller=remote --mac -x
```
- Startet einen HTTP-Server auf h2:
```bash
h2 python3 -m http.server 80 &
```
- Prüft die Erreichbarkeit der Hosts untereinander mit Ping:
```bash
pingall
```

- Schaut euch den Code des POX-Controllers an und versucht ihn nachzuvollziehen
- Überlegt euch sinnvolle Regeln, die die Sicherheit im Netzwerk erhöhen
    - möglicher Regelsatz:
    - ICMP (Ping) von h3 zu h2 blockieren
    - SSH von h3 zu h2 blockieren
    - aber HTTP von h3 zu h2 erlaubt
    - ICMP und SSH und HTTP von h1 zu h2 erlaubt
- Implementiert die Regeln im Code (in der 'is_blocked'-Methode)
- Überprüft, ob die Regeln wirksam sind

### Fragen
1. Was sind typische Merkmale einer SDN-basierten Firewall im Vergleich zu einer traditionellen?
2. Welche Vorteile bietet eine zentrale Regelverwaltung via Controller?
3. Was fällt euch auf wenn ihr euch die Flowtable ausgeben lasst? (Befehl in Mininet: dpctl dump-flows)
   - Antwort: Alle erlaubten Pakete werden geflutet statt an einen gezielten Port weitergeleitet.

### Bonus falls noch Zeit
- Erweitert die Logik-Regeln, sodass sie auf ganze Subnetze angewendet werden und nicht nur auf einzelne Hosts. Dafür müssen ggf andere IP-Adressen an die Hosts vergeben werden (anzupassen in der Mininet-Topologie).
- fügt einen weiteren Host in der Topologie hinzu oder ändert die IP-Adressen der vorhandenen Hosts. Prüft, ob die Regeln weiterhin wie gewünscht angewendet werden

### weiterer Bonus falls noch Zeit
...
