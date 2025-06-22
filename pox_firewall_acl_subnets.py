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
        # hier werden Quell-/Ziel-IP, Protokoll, Ports aus dem IP-Paket extrahiert
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
        if self.is_blocked(src_ip, dst_ip, proto, dst_port):
            log.info("Blockiert: %s -> %s (proto %s, port %s)", src_ip, dst_ip, proto, dst_port)
            return  # Paket wird nicht weitergeleitet
        else:
            log.info("Erlaubt: %s -> %s (proto %s, port %s)", src_ip, dst_ip, proto, dst_port)
            self._allow_packet(event)

    # --- Sektion C: Statische ACL ---
    # TODO: in der Methode "is_blocked" sollt ihr Regeln festlegen
    """
    # --- Hilfe ---
    # Syntax für den Vergleich mit einigen gängigen Protokollen:
    proto == ipv4.TCP_PROTOCOL
    proto == ipv4.UDP_PROTOCOL
    proto == ipv4.ICMP_PROTOCOL
    proto == ipv4.IGMP_PROTOCOL

    # Syntax für den Vergleich mit einer IP-Adresse:
    ip == IPAddr("192.168.0.1")

    # Syntax um zu prüfen, ob eine IP-Adresse in einem gegebenen Subnetz liegt:
    if ip in IPNet("10.0.0.0/24"):
        print("Adresse liegt im Subnetz")
    """
    def is_blocked(self, src, dst, proto, dport):
        # ----- Beispielhafter Regelsatz -----
        # --- Netzwerke ---
        # internes Netz:    10.0.1.0/24
        # DMZ (Server):     10.0.2.0/24
        # externes Netz:    10.0.3.0/24

        # --- Regeln ---
        # keinen Traffic vom externen Client zulassen bis auf Zugriff auf den HTTP-Server
        # der interne Client darf alles, bis auf SSH zu h2
        
        # Regel 1: TCP-Pakete von allen Hosts an den HTTP-Server auf h2 erlauben
        if dst == IPAddr("10.0.2.2") and proto == ipv4.TCP_PROTOCOL and dport == 80:
            return False

        # Regel 2: gesamten Traffic aus externem Netz blockieren
        external_network = IPAddr("10.0.3.0/24")
        if src.inNetwork(external_network):
            log.info("IP %s befindet sich im externen Netz %s", src_ip, external_network)
            return True

        # Regel 3: SSH von internem Netz zur DMZ blockieren
        # if src in IPNet("10.0.1.0/24") and dst in IPNet("10.0.2.0/24") and proto == ipv4.TCP_PROTOCOL and dport == 22:
        #     return True
        
        # --- Einzelbeispiele für Regeln ---
        # Beispiel: ICMP von externem Client blockieren
        # if src == IPAddr("10.0.0.3") and proto == ipv4.ICMP_PROTOCOL:
        #     return True
        
        # Beispiel: TCP Port 22 (SSH) von externem Client blockieren
        # if src == IPAddr("10.0.0.3") and proto == ipv4.TCP_PROTOCOL and dport == 22:
        #     return True
        
        # Beispiel: ICMP von externem Netz zu h2 blockieren
        # externes_subnetz = IPNet("10.0.3.0/24")
        # if src in externes_subnetz and dst == interner_host and proto == ipv4.ICMP_PROTOCOL:
        #     return True
        return False

    def _allow_packet(self, event):
        # Flow installieren, damit das Paket durchgeht
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(event.parsed)
        msg.idle_timeout = 30
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        msg.data = event.ofp
        self.connection.send(msg)

def launch():
    def start_switch(event):
        log.info("Starte Firewall auf %s", event.connection)
        SimpleFirewall(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)
