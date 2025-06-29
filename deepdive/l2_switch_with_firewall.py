"""
L2 Learning Switch mit integrierter Firewall-Funktionalität

Dieser Controller kombiniert die Funktionalität eines L2 Learning Switches
mit einer statischen Firewall basierend auf ACL-Regeln.

Funktionen:
- MAC-Adress-Learning für effizientes Layer-2-Switching
- Firewall-Filterung basierend auf IP-Adressen, Protokollen und Ports
- Flow-Installation für erlaubte Pakete zur Performance-Optimierung

Verwendung:
    ~/pox/pox.py l2_learningSwitch samples.pretty_log --DEBUG

Topologie:
    sudo mn --custom custom_topo.py --topo sdnfirewall --controller=remote,ip=127.0.0.1,port=6633 --mac -x
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet import ethernet, ipv4, tcp, udp, icmp
from pox.lib.addresses import EthAddr, IPAddr

log = core.getLogger()

class LearningSwitchWithFirewall(object):
    """
    Kombinierter L2 Learning Switch mit Firewall-Funktionalität
    
    Diese Klasse implementiert:
    1. MAC-Adress-Learning für effizientes Layer-2-Switching
    2. Firewall-Filterung basierend auf statischen ACL-Regeln
    3. Flow-Installation für Performance-Optimierung
    """
    
    def __init__(self, connection):
        """
        Initialisiert den Learning Switch mit Firewall
        
        Args:
            connection: OpenFlow-Verbindung zum Switch
        """
        self.connection = connection
        self.mac_to_port = {}  # Zuordnung MAC-Adresse → Port
        connection.addListeners(self)
        log.info("LearningSwitch mit Firewall verbunden mit %s", connection)

    def _handle_PacketIn(self, event):
        """
        Hauptmethode zur Paketverarbeitung
        
        Verarbeitet eingehende Pakete in folgender Reihenfolge:
        1. MAC-Adress-Learning
        2. Firewall-Prüfung für IP-Pakete
        3. L2-Switching basierend auf gelernten MAC-Adressen
        
        Args:
            event: OpenFlow PacketIn-Event
        """
        packet = event.parsed

        if not packet.parsed:
            log.warning("Unverständliches Paket - wird verworfen")
            return

        eth = packet.find('ethernet')
        if not eth:
            log.warning("Kein Ethernet-Frame gefunden - wird verworfen")
            return
            
        src_mac = eth.src
        dst_mac = eth.dst
        in_port = event.port

        # --- Sektion A: MAC-Adresse lernen ---
        self._learn_mac_address(src_mac, in_port)

        # --- Sektion B: Firewall-Prüfung für IP-Pakete ---
        if self._should_check_firewall(packet):
            if self._is_packet_blocked(packet):
                log.info("Firewall: Paket blockiert von %s nach %s", 
                        packet.find('ipv4').srcip, packet.find('ipv4').dstip)
                return  # Paket wird nicht weitergeleitet

        # --- Sektion C: L2-Switching basierend auf gelernten MAC-Adressen ---
        self._handle_l2_switching(packet, src_mac, dst_mac, in_port, event)

    def _learn_mac_address(self, src_mac, in_port):
        """
        Lernt die Zuordnung von MAC-Adresse zu Port
        
        Args:
            src_mac: Quell-MAC-Adresse
            in_port: Eingangsport
        """
        self.mac_to_port[src_mac] = in_port
        log.debug("MAC-Adresse gelernt: %s → Port %s", src_mac, in_port)

    def _should_check_firewall(self, packet):
        """
        Prüft ob ein Paket Firewall-Prüfung benötigt
        
        Args:
            packet: Zu prüfendes Paket
            
        Returns:
            bool: True wenn IP-Paket gefunden wurde
        """
        return packet.find('ipv4') is not None

    def _is_packet_blocked(self, packet):
        """
        Firewall-Logik: Prüft ob ein IP-Paket blockiert werden soll
        
        Extrahiert relevante Felder aus dem IP-Paket und wendet ACL-Regeln an.
        
        Args:
            packet: Zu prüfendes IP-Paket
            
        Returns:
            bool: True wenn Paket blockiert werden soll
        """
        ip_packet = packet.find('ipv4')
        src_ip = ip_packet.srcip
        dst_ip = ip_packet.dstip
        proto = ip_packet.protocol

        # Ports extrahieren basierend auf Protokoll
        dst_port = self._extract_dst_port(packet, proto)

        # Firewall-Regeln anwenden
        return self._is_blocked_by_acl(src_ip, dst_ip, proto, dst_port)

    def _extract_dst_port(self, packet, proto):
        """
        Extrahiert den Zielport basierend auf dem Protokoll
        
        Args:
            packet: IP-Paket
            proto: Protokoll-ID
            
        Returns:
            int: Zielport oder None
        """
        if proto == ipv4.ICMP_PROTOCOL:
            return None  # ICMP → keine Ports
        elif proto == ipv4.TCP_PROTOCOL:
            tcp_packet = packet.find('tcp')
            return tcp_packet.dstport if tcp_packet else None
        elif proto == ipv4.UDP_PROTOCOL:
            udp_packet = packet.find('udp')
            return udp_packet.dstport if udp_packet else None
        return None

    def _is_blocked_by_acl(self, src, dst, proto, dport):
        """
        Statische ACL-Regeln
        
        Implementiert die Firewall-Logik basierend auf:
        - Quell-IP-Adresse
        - Ziel-IP-Adresse  
        - Protokoll (TCP, UDP, ICMP)
        - Zielport
        
        Args:
            src: Quell-IP-Adresse
            dst: Ziel-IP-Adresse
            proto: Protokoll-ID
            dport: Zielport
            
        Returns:
            bool: True wenn Paket blockiert werden soll
        """
        # --- Beispielhafter Regelsatz ---
        # Regel 1: HTTP-Zugriff (Port 80) zu h2 von allen Hosts erlauben
        if dst == IPAddr("10.0.0.2") and proto == ipv4.TCP_PROTOCOL and dport == 80:
            log.debug("ACL: HTTP-Zugriff zu h2 erlaubt")
            return False

        # Regel 2: Gesamten Traffic von externem Client (h3) blockieren
        if src == IPAddr("10.0.0.3"):
            log.debug("ACL: Traffic von externem Client h3 blockiert")
            return True

        # Regel 3: SSH-Zugriff (Port 22) von internem Client (h1) zu h2 blockieren
        if src == IPAddr("10.0.0.1") and dst == IPAddr("10.0.0.2") and proto == ipv4.TCP_PROTOCOL and dport == 22:
            log.debug("ACL: SSH von h1 zu h2 blockiert")
            return True

        # Standard: Paket erlauben
        log.debug("ACL: Paket erlaubt (Standard-Regel)")
        return False

    def _handle_l2_switching(self, packet, src_mac, dst_mac, in_port, event):
        """
        Führt L2-Switching basierend auf gelernten MAC-Adressen durch
        
        Args:
            packet: Zu verarbeitendes Paket
            src_mac: Quell-MAC-Adresse
            dst_mac: Ziel-MAC-Adresse
            in_port: Eingangsport
            event: OpenFlow-Event
        """
        if dst_mac in self.mac_to_port:
            # Ziel bekannt → direktes Switching
            out_port = self.mac_to_port[dst_mac]
            log.info("L2-Switching: %s -> %s über Port %s", src_mac, dst_mac, out_port)
            self._install_flow_and_forward(packet, in_port, out_port, event)
        else:
            # Ziel unbekannt → Flood
            log.info("Unbekanntes Ziel %s – Flood an alle Ports", dst_mac)
            self._flood_packet(event, in_port)

    def _install_flow_and_forward(self, packet, in_port, out_port, event):
        """
        Installiert Flow-Regel und leitet Paket weiter
        
        Args:
            packet: Zu verarbeitendes Paket
            in_port: Eingangsport
            out_port: Ausgangsport
            event: OpenFlow-Event
        """
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet, in_port)
        msg.idle_timeout = 30  # Flow-Regel wird nach Inaktivität gelöscht
        msg.hard_timeout = 300  # max. Lebenszeit der Flow-Regel
        msg.actions.append(of.ofp_action_output(port=out_port))
        msg.data = event.ofp  # sendet auch gleich das aktuelle Paket
        self.connection.send(msg)
        log.debug("Flow installiert: %s -> %s", in_port, out_port)

    def _flood_packet(self, event, in_port):
        """
        Leitet Paket an alle Ports weiter (Flood)
        
        Args:
            event: OpenFlow-Event
            in_port: Eingangsport (wird ausgeschlossen)
        """
        msg = of.ofp_packet_out(data=event.ofp)
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        msg.in_port = in_port
        self.connection.send(msg)
        log.debug("Paket geflutet von Port %s", in_port)

def launch():
    """
    Startet den Learning Switch mit Firewall
    
    Registriert einen Event-Listener für neue OpenFlow-Verbindungen
    """
    def start_switch(event):
        log.info("Starte LearningSwitch mit Firewall auf %s", event.connection)
        LearningSwitchWithFirewall(event.connection)
    
    core.openflow.addListenerByName("ConnectionUp", start_switch)
