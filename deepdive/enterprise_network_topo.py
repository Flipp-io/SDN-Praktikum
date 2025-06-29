"""
Enterprise-Netzwerk Topologie für L3 Switch Demo

Diese Topologie simuliert ein realistisches Unternehmensnetzwerk mit:
- Internes Netzwerk (Büros, Entwickler)
- DMZ (Webserver, Mailserver, DNS)
- Externes Netzwerk (Internet-Zugang)
- Server-Farm (Datenbanken, Anwendungen)
- Management-Netzwerk (Admin-Zugang)

Netzwerk-Struktur:
- 10.1.0.0/16 - Internes Netzwerk (Büros)
- 10.2.0.0/16 - DMZ (öffentliche Server)
- 10.3.0.0/16 - Externes Netzwerk (Internet)
- 10.4.0.0/16 - Server-Farm (Datenbanken)
- 10.5.0.0/16 - Management-Netzwerk (Admin)

Verwendung:
    sudo mn --custom enterprise_topo.py --topo enterprise --controller=remote,ip=127.0.0.1,port=6633 --mac -x
"""

from mininet.topo import Topo

class EnterpriseNetworkTopo(Topo):
    def build(self):
        # Router-Switch (L3-Switch, von POX gesteuert)
        router = self.addSwitch('r1')

        # =====================
        # INTERNES NETZWERK (10.1.1.0/24)
        # =====================
        s1 = self.addSwitch('s1')
        h1 = self.addHost('h1', ip='10.1.1.10/24', defaultRoute='via 10.1.1.254')
        h2 = self.addHost('h2', ip='10.1.1.11/24', defaultRoute='via 10.1.1.254')
        h3 = self.addHost('h3', ip='10.1.1.12/24', defaultRoute='via 10.1.1.254')
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(s1, router)

        # =====================
        # DMZ (10.2.1.0/24)
        # =====================
        s2 = self.addSwitch('s2')
        h8 = self.addHost('h8', ip='10.2.1.100/24', defaultRoute='via 10.2.1.254')
        h9 = self.addHost('h9', ip='10.2.1.101/24', defaultRoute='via 10.2.1.254')
        self.addLink(h8, s2)
        self.addLink(h9, s2)
        self.addLink(s2, router)

        # =====================
        # EXTERNES NETZWERK (10.3.1.0/24)
        # =====================
        s3 = self.addSwitch('s3')
        h15 = self.addHost('h15', ip='10.3.1.200/24', defaultRoute='via 10.3.1.254')
        h16 = self.addHost('h16', ip='10.3.1.201/24', defaultRoute='via 10.3.1.254')
        self.addLink(h15, s3)
        self.addLink(h16, s3)
        self.addLink(s3, router)

        # =====================
        # SERVER-FARM (10.4.1.0/24)
        # =====================
        s4 = self.addSwitch('s4')
        h19 = self.addHost('h19', ip='10.4.1.220/24', defaultRoute='via 10.4.1.254')
        h20 = self.addHost('h20', ip='10.4.1.221/24', defaultRoute='via 10.4.1.254')
        self.addLink(h19, s4)
        self.addLink(h20, s4)
        self.addLink(s4, router)

        # =====================
        # MANAGEMENT (10.5.1.0/24)
        # =====================
        s5 = self.addSwitch('s5')
        h25 = self.addHost('h25', ip='10.5.1.250/24', defaultRoute='via 10.5.1.254')
        h26 = self.addHost('h26', ip='10.5.1.251/24', defaultRoute='via 10.5.1.254')
        self.addLink(h25, s5)
        self.addLink(h26, s5)
        self.addLink(s5, router)

# Topologie registrieren
# (Name bleibt 'enterprise', damit dein Startbefehl gleich bleibt)
topos = { 'enterprise': (lambda: EnterpriseNetworkTopo()) } 