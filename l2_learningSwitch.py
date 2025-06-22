from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet import ethernet
from pox.lib.addresses import EthAddr

log = core.getLogger()

class LearningSwitch(object):
    def __init__(self, connection):
        self.connection = connection
        self.mac_to_port = {}  # Zuordnung MAC-Adresse → Port
        connection.addListeners(self)
        log.info("LearningSwitch verbunden mit %s", connection)

    def _handle_PacketIn(self, event):
        packet = event.parsed

        if not packet.parsed:
            log.warning("Unverständliches Paket")
            return

        eth = packet.find('ethernet')
        src_mac = eth.src
        dst_mac = eth.dst
        in_port = event.port

        # --- Sektion A: MAC-Adresse lernen ---
        self.mac_to_port[src_mac] = in_port
        log.debug("Gelernt: %s → Port %s", src_mac, in_port)

        # --- Sektion B: Zieladresse bekannt? ---
        if dst_mac in self.mac_to_port:
            out_port = self.mac_to_port[dst_mac]
            log.info("Switching: %s -> %s über Port %s", src_mac, dst_mac, out_port)

            # Flow installieren, damit künftige Pakete direkt geswitcht werden
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match.from_packet(packet, in_port)
            msg.idle_timeout = 30  # Flow-Regel wird nach Inaktivität gelöscht
            msg.hard_timeout = 300  # max. Lebenszeit
            msg.actions.append(of.ofp_action_output(port=out_port))
            msg.data = event.ofp  # sendet auch gleich das aktuelle Paket
            self.connection.send(msg)
        else:
            # --- Sektion C: Ziel nicht bekannt → Flood ---
            log.info("Unbekanntes Ziel %s – Flood", dst_mac)
            msg = of.ofp_packet_out(data=event.ofp)
            msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
            msg.in_port = in_port
            self.connection.send(msg)

def launch():
    def start_switch(event):
        log.info("Starte LearningSwitch auf %s", event.connection)
        LearningSwitch(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)
