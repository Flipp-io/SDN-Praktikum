# Mininet-Topologie fuer Aufagbe B: SDN-Firewall mit statischer ACL
# Cients in verschiedenen /24 Subnetzen 
# (Netzmaske /16, damit kein Routing notwendig ist)

from mininet.topo import Topo

class SDNFirewallTopo(Topo):
    def build(self):
        # Switch
        s1 = self.addSwitch('s1')

        # Hosts
        # Netzmaske /16 damit sie ohne Routing kommunizieren können
        h1 = self.addHost('h1', ip='10.0.1.1/16')  # interner Client
        h2 = self.addHost('h2', ip='10.0.2.2/16')  # Server in DMZ
        h3 = self.addHost('h3', ip='10.0.3.3/16')  # externer Client
        h4 = self.addHost('h4', ip='10.0.2.4/16')  # Client in DMZ

        # Links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s1)

topos = { 'sdnfirewall': (lambda: SDNFirewallTopo()) }
