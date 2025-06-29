"""
Layer 3 Switch mit integrierter Firewall-Funktionalität

Dieser Controller implementiert einen vollständigen L3 Switch mit:
- IP-basiertem Routing zwischen Subnetzen
- ARP-Handling für MAC-Adress-Auflösung
- Firewall-Filterung basierend auf ACL-Regeln
- Flow-Installation für Performance-Optimierung
- MAC-Adress-Learning für lokale Subnetze

Funktionen:
- Routing zwischen verschiedenen IP-Subnetzen
- Automatische MAC-Adress-Auflösung via ARP
- Firewall-Filterung auf IP-Ebene
- Effiziente Flow-Installation
- Unterstützung für statische Routen

Verwendung:
    ~/pox/pox.py l3_switch samples.pretty_log --DEBUG

Topologie:
    sudo mn --custom custom_topo_subnets.py --topo sdnfirewall --controller=remote,ip=127.0.0.1,port=6633 --mac -x
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet import ethernet, ipv4, tcp, udp, icmp, arp
from pox.lib.addresses import EthAddr, IPAddr
import time
from pox.openflow.libopenflow_01 import ofp_action_dl_addr, OFPAT_SET_DL_SRC, OFPAT_SET_DL_DST

log = core.getLogger()

gateway_ips = {
    IPAddr("10.1.1.254"): EthAddr("00:aa:00:00:01:01"),
    IPAddr("10.2.1.254"): EthAddr("00:aa:00:00:02:01"),
    IPAddr("10.3.1.254"): EthAddr("00:aa:00:00:03:01"),
    IPAddr("10.4.1.254"): EthAddr("00:aa:00:00:04:01"),
    IPAddr("10.5.1.254"): EthAddr("00:aa:00:00:05:01"),
    # ... ggf. weitere Subnetze
}

class Layer3SwitchWithFirewall(object):
    """
    Vollständiger Layer 3 Switch mit Firewall-Funktionalität
    
    Diese Klasse implementiert:
    1. IP-basiertes Routing zwischen Subnetzen
    2. ARP-Handling für MAC-Adress-Auflösung
    3. Firewall-Filterung basierend auf ACL-Regeln
    4. Flow-Installation für Performance-Optimierung
    5. MAC-Adress-Learning für lokale Subnetze
    """
    
    def __init__(self, connection):
        """
        Initialisiert den Layer 3 Switch mit Firewall
        
        Args:
            connection: OpenFlow-Verbindung zum Switch
        """
        self.connection = connection
        self.mac_to_port = {}  # MAC-Adresse → Port (für lokale Subnetze)
        self.ip_to_mac = {}    # IP-Adresse → MAC-Adresse (ARP-Cache)
        self.mac_to_ip = {}    # MAC-Adresse → IP-Adresse (Reverse-ARP)
        self.arp_requests = {} # Ausstehende ARP-Requests
        self.static_routes = {} # Statische Routen: Netzwerk → Gateway
        self.gateway_ips = gateway_ips # Gateway-IPs
        
        # Statische Routen konfigurieren
        self._setup_static_routes()
        
        connection.addListeners(self)
        log.info("Layer 3 Switch mit Firewall verbunden mit %s", connection)

    def _setup_static_routes(self):
        """
        Konfiguriert statische Routen für die Topologie
        
        Für custom_topo_subnets.py:
        - 10.0.1.0/24 (internes Netz) → direkt verbunden
        - 10.0.2.0/24 (DMZ) → direkt verbunden  
        - 10.0.3.0/24 (externes Netz) → direkt verbunden
        """
        # Alle Subnetze sind direkt verbunden (gleicher Switch)
        # In einer komplexeren Topologie würden hier Gateways definiert
        self.static_routes = {
            "10.0.1.0/24": None,  # Direkt verbunden
            "10.0.2.0/24": None,  # Direkt verbunden
            "10.0.3.0/24": None   # Direkt verbunden
        }
        log.info("Statische Routen konfiguriert: %s", list(self.static_routes.keys()))

    def _handle_PacketIn(self, event):
        """
        Hauptmethode zur Paketverarbeitung
        
        Verarbeitet eingehende Pakete in folgender Reihenfolge:
        1. MAC-Adress-Learning
        2. Paket-Typ-Erkennung (ARP vs IP)
        3. Firewall-Prüfung für IP-Pakete
        4. L3-Routing oder L2-Switching
        
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

        # --- Sektion B: Paket-Typ bestimmen und verarbeiten ---
        if packet.find('arp'):
            self._handle_arp_packet(packet, src_mac, dst_mac, in_port, event)
        elif packet.find('ipv4'):
            self._handle_ip_packet(packet, src_mac, dst_mac, in_port, event)
        else:
            # Unbekanntes Protokoll → Flood
            log.debug("Unbekanntes Protokoll - Flood")
            self._flood_packet(event, in_port)

    def _learn_mac_address(self, src_mac, in_port):
        """
        Lernt die Zuordnung von MAC-Adresse zu Port
        
        Args:
            src_mac: Quell-MAC-Adresse
            in_port: Eingangsport
        """
        self.mac_to_port[src_mac] = in_port
        log.debug("MAC-Adresse gelernt: %s → Port %s", src_mac, in_port)

    def _handle_arp_packet(self, packet, src_mac, dst_mac, in_port, event):
        """
        Verarbeitet ARP-Pakete (Request und Reply)
        
        Args:
            packet: ARP-Paket
            src_mac: Quell-MAC-Adresse
            dst_mac: Ziel-MAC-Adresse
            in_port: Eingangsport
            event: OpenFlow-Event
        """
        arp_packet = packet.find('arp')
        
        if arp_packet.protosrc:  # IP-Adresse vorhanden
            # MAC-IP-Zuordnung lernen
            self.ip_to_mac[arp_packet.protosrc] = src_mac
            self.mac_to_ip[src_mac] = arp_packet.protosrc
            log.debug("ARP: IP %s → MAC %s gelernt", arp_packet.protosrc, src_mac)

        if arp_packet.opcode == arp.REQUEST:
            # ARP-Request verarbeiten
            self._handle_arp_request(arp_packet, src_mac, in_port, event)
        elif arp_packet.opcode == arp.REPLY:
            # ARP-Reply verarbeiten
            self._handle_arp_reply(arp_packet, event)

    def _handle_arp_request(self, arp_packet, src_mac, in_port, event):
        """
        Verarbeitet ARP-Requests
        
        Args:
            arp_packet: ARP-Paket
            src_mac: Quell-MAC-Adresse
            in_port: Eingangsport
            event: OpenFlow-Event
        """
        target_ip = arp_packet.protodst
        
        # Prüfe, ob die Ziel-IP eine Gateway-IP ist
        if target_ip in self.gateway_ips:
            gw_mac = self.gateway_ips[target_ip]
            self._send_arp_reply(target_ip, gw_mac, arp_packet.protosrc, src_mac, in_port)
            log.info("ARP: Gateway-Reply für %s → %s", target_ip, gw_mac)
            return

        if target_ip in self.ip_to_mac:
            # Ziel-IP bekannt → ARP-Reply senden
            target_mac = self.ip_to_mac[target_ip]
            self._send_arp_reply(target_ip, target_mac, arp_packet.protosrc, src_mac, in_port)
            log.info("ARP: Reply für %s → %s", target_ip, target_mac)
        else:
            # Ziel-IP unbekannt → Request weiterleiten
            log.info("ARP: Request für unbekannte IP %s - Flood", target_ip)
            self._flood_packet(event, in_port)

    def _handle_arp_reply(self, arp_packet, event):
        """
        Verarbeitet ARP-Replies
        
        Args:
            arp_packet: ARP-Paket
            event: OpenFlow-Event
        """
        # ARP-Reply an den ursprünglichen Requester weiterleiten
        requester_mac = arp_packet.protodst
        if requester_mac in self.mac_to_port:
            out_port = self.mac_to_port[requester_mac]
            self._install_flow_and_forward(event.parsed, event.port, out_port, event,
                set_src_mac=self.gateway_ips[event.parsed.find('ipv4').dstip],
                set_dst_mac=requester_mac)
            log.info("ARP: Reply weitergeleitet an %s über Port %s", requester_mac, out_port)
        else:
            log.warning("ARP: Reply für unbekannte MAC %s - Flood", requester_mac)
            self._flood_packet(event, event.port)

    def _send_arp_reply(self, target_ip, target_mac, requester_ip, requester_mac, out_port):
        """
        Sendet ARP-Reply
        
        Args:
            target_ip: IP-Adresse des Ziels
            target_mac: MAC-Adresse des Ziels
            requester_ip: IP-Adresse des Requesters
            requester_mac: MAC-Adresse des Requesters
            out_port: Ausgangsport
        """
        # ARP-Reply erstellen
        arp_reply = arp()
        arp_reply.hwsrc = target_mac
        arp_reply.hwdst = requester_mac
        arp_reply.protosrc = target_ip
        arp_reply.protodst = requester_ip
        arp_reply.opcode = arp.REPLY

        # Ethernet-Frame erstellen
        eth_frame = ethernet()
        eth_frame.src = target_mac
        eth_frame.dst = requester_mac
        eth_frame.type = ethernet.ARP_TYPE
        eth_frame.payload = arp_reply

        # Paket senden
        msg = of.ofp_packet_out()
        msg.data = eth_frame.pack()
        msg.actions.append(of.ofp_action_output(port=out_port))
        self.connection.send(msg)

    def _handle_ip_packet(self, packet, src_mac, dst_mac, in_port, event):
        """
        Verarbeitet IP-Pakete (Routing + Firewall)
        
        Args:
            packet: IP-Paket
            src_mac: Quell-MAC-Adresse
            dst_mac: Ziel-MAC-Adresse
            in_port: Eingangsport
            event: OpenFlow-Event
        """
        ip_packet = packet.find('ipv4')
        src_ip = ip_packet.srcip
        dst_ip = ip_packet.dstip

        # --- Sektion A: Firewall-Prüfung ---
        if self._is_packet_blocked(packet):
            log.info("Firewall: IP-Paket blockiert von %s nach %s", src_ip, dst_ip)
            # Drop-Flow installieren
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match.from_packet(packet, in_port)
            msg.idle_timeout = 30  # oder länger, je nach Bedarf
            msg.hard_timeout = 300
            # Keine Actions = Drop!
            self.connection.send(msg)
            return

        # --- Sektion B: Routing-Entscheidung ---
        if dst_mac.is_multicast or dst_mac.is_broadcast:
            # Broadcast/Multicast → Flood
            log.info("IP: Broadcast/Multicast - Flood")
            self._flood_packet(event, in_port)
        else:
            # Unicast → Routing
            self._route_ip_packet(packet, src_ip, dst_ip, in_port, event)

    def _is_packet_blocked(self, packet):
        """
        Firewall-Logik: Prüft ob ein IP-Paket blockiert werden soll
        
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
        Statische ACL-Regeln für L3-Switch
        
        Implementiert Firewall-Logik basierend auf:
        - Quell-IP-Adresse/Subnetz
        - Ziel-IP-Adresse/Subnetz
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
        # --- L3-Switch ACL-Regeln ---
        # --------------------- Hier die Regeln einfügen ---------------------
        
        # Regel 1: HTTP-Zugriff (Port 80) zu DMZ-Server erlauben
        if dst == IPAddr("10.0.2.2") and proto == ipv4.TCP_PROTOCOL and dport == 80:
            log.debug("ACL: HTTP-Zugriff zu DMZ-Server erlaubt")
            return False

        # Regel 2: Gesamten Traffic aus externem Netz blockieren
        if src.inNetwork("10.0.3.0/24"):
            log.debug("ACL: Traffic aus externem Netz blockiert")
            return True

        # Regel 3: SSH von internem Netz zur DMZ blockieren
        if src.inNetwork("10.0.1.0/24") and dst.inNetwork("10.0.2.0/24") and proto == ipv4.TCP_PROTOCOL and dport == 22:
            log.debug("ACL: SSH von internem zu DMZ-Netz blockiert")
            return True

        # Standard: Paket erlauben
        log.debug("ACL: Paket erlaubt (Standard-Regel)")
        return False

    def _route_ip_packet(self, packet, src_ip, dst_ip, in_port, event):
        """
        Führt IP-Routing durch
        
        Args:
            packet: IP-Paket
            src_ip: Quell-IP-Adresse
            dst_ip: Ziel-IP-Adresse
            in_port: Eingangsport
            event: OpenFlow-Event
        """
        # Ziel-MAC-Adresse ermitteln
        dst_mac = self._get_destination_mac(dst_ip)
        
        if dst_mac:
            # Ziel-MAC bekannt → direkt routen
            out_port = self._get_output_port(dst_mac, dst_ip)
            if out_port:
                log.info("L3-Routing: %s → %s über Port %s", src_ip, dst_ip, out_port)
                self._install_flow_and_forward(packet, in_port, out_port, event,
                    set_src_mac=self.gateway_ips[dst_ip],
                    set_dst_mac=dst_mac)
            else:
                log.warning("L3-Routing: Kein Ausgangsport für %s gefunden", dst_ip)
                self._flood_packet(event, in_port)
        else:
            # Ziel-MAC unbekannt → ARP-Request senden
            log.info("L3-Routing: MAC für %s unbekannt - ARP-Request", dst_ip)
            self._send_arp_request(dst_ip, in_port)

    def _get_destination_mac(self, dst_ip):
        """
        Ermittelt die MAC-Adresse für eine IP-Adresse
        
        Args:
            dst_ip: Ziel-IP-Adresse
            
        Returns:
            EthAddr: MAC-Adresse oder None
        """
        if dst_ip in self.ip_to_mac:
            return self.ip_to_mac[dst_ip]
        return None

    def _get_output_port(self, dst_mac, dst_ip):
        """
        Ermittelt den Ausgangsport für eine MAC-Adresse oder IP
        
        Args:
            dst_mac: Ziel-MAC-Adresse
            dst_ip: Ziel-IP-Adresse
            
        Returns:
            int: Ausgangsport oder None
        """
        # Zuerst MAC-basiert versuchen
        if dst_mac in self.mac_to_port:
            return self.mac_to_port[dst_mac]
        
        # Dann IP-basiert versuchen (falls IP gelernt wurde)
        if dst_ip in self.ip_to_mac:
            learned_mac = self.ip_to_mac[dst_ip]
            if learned_mac in self.mac_to_port:
                return self.mac_to_port[learned_mac]
        
        return None

    def _send_arp_request(self, target_ip, out_port):
        """
        Sendet ARP-Request für eine IP-Adresse
        
        Args:
            target_ip: Ziel-IP-Adresse
            out_port: Ausgangsport
        """
        # ARP-Request erstellen
        arp_req = arp()
        arp_req.hwsrc = EthAddr("00:00:00:00:00:01")  # Switch-MAC
        arp_req.hwdst = EthAddr("ff:ff:ff:ff:ff:ff")  # Broadcast
        arp_req.protosrc = IPAddr("0.0.0.0")  # Unbekannte Quell-IP
        arp_req.protodst = target_ip
        arp_req.opcode = arp.REQUEST

        # Ethernet-Frame erstellen
        eth_frame = ethernet()
        eth_frame.src = EthAddr("00:00:00:00:00:01")
        eth_frame.dst = EthAddr("ff:ff:ff:ff:ff:ff")
        eth_frame.type = ethernet.ARP_TYPE
        eth_frame.payload = arp_req

        # Paket senden
        msg = of.ofp_packet_out()
        msg.data = eth_frame.pack()
        msg.actions.append(of.ofp_action_output(port=out_port))
        self.connection.send(msg)
        
        log.debug("ARP-Request gesendet für %s über Port %s", target_ip, out_port)

    def _install_flow_and_forward(self, packet, in_port, out_port, event, set_src_mac=None, set_dst_mac=None):
        """
        Installiert Flow-Regel und leitet Paket weiter
        
        Args:
            packet: Zu verarbeitendes Paket
            in_port: Eingangsport
            out_port: Ausgangsport
            event: OpenFlow-Event
            set_src_mac: Quell-MAC-Adresse für Source-MAC-Rewrite
            set_dst_mac: Ziel-MAC-Adresse für Destination-MAC-Rewrite
        """
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet, in_port)
        msg.idle_timeout = 30
        msg.hard_timeout = 300
        if set_src_mac:
            msg.actions.append(ofp_action_dl_addr(type=OFPAT_SET_DL_SRC, dl_addr=set_src_mac))
        if set_dst_mac:
            msg.actions.append(ofp_action_dl_addr(type=OFPAT_SET_DL_DST, dl_addr=set_dst_mac))
        msg.actions.append(of.ofp_action_output(port=out_port))
        msg.data = event.ofp
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
    Startet den Layer 3 Switch mit Firewall
    
    Registriert einen Event-Listener für neue OpenFlow-Verbindungen
    """
    def start_switch(event):
        log.info("Starte Layer 3 Switch mit Firewall auf %s", event.connection)
        Layer3SwitchWithFirewall(event.connection)
    
    core.openflow.addListenerByName("ConnectionUp", start_switch) 