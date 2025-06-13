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
