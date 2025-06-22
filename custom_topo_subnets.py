from mininet.topo import Topo

class SDNFirewallTopo(Topo):
    def build(self):
        # Switch
        s1 = self.addSwitch('s1')

        # Hosts
        h1 = self.addHost('h1', ip='10.0.1.1/24')  # interner Client
        h2 = self.addHost('h2', ip='10.0.2.2/24')  # Server
        h3 = self.addHost('h3', ip='10.0.3.3/24')  # externer Client

        # Links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)

topos = { 'sdnfirewall': (lambda: SDNFirewallTopo()) }
