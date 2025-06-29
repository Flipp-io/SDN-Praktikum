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
        """
        Erstellt eine komplexe Enterprise-Netzwerk Topologie
        """
        
        # =============================================================================
        # SWITCHES (L3 Switch mit Firewall)
        # =============================================================================
        s1 = self.addSwitch('s1')  # Haupt-Switch für alle Subnetze
        
        # =============================================================================
        # INTERNES NETZWERK (10.1.0.0/16) - Büros und Entwickler
        # =============================================================================
        # Büro-Mitarbeiter
        h1 = self.addHost('h1', ip='10.1.1.10/16')  # Büro-Client 1
        h2 = self.addHost('h2', ip='10.1.1.11/16')  # Büro-Client 2
        h3 = self.addHost('h3', ip='10.1.1.12/16')  # Büro-Client 3
        
        # Entwickler
        h4 = self.addHost('h4', ip='10.1.2.20/16')  # Entwickler 1
        h5 = self.addHost('h5', ip='10.1.2.21/16')  # Entwickler 2
        
        # IT-Administratoren
        h6 = self.addHost('h6', ip='10.1.3.30/16')  # IT-Admin 1
        h7 = self.addHost('h7', ip='10.1.3.31/16')  # IT-Admin 2
        
        # =============================================================================
        # DMZ (10.2.0.0/16) - Öffentliche Server
        # =============================================================================
        # Webserver
        h8 = self.addHost('h8', ip='10.2.1.100/16')   # Haupt-Webserver
        h9 = self.addHost('h9', ip='10.2.1.101/16')   # Backup-Webserver
        
        # Mailserver
        h10 = self.addHost('h10', ip='10.2.2.110/16') # SMTP-Server
        h11 = self.addHost('h11', ip='10.2.2.111/16') # IMAP-Server
        
        # DNS-Server
        h12 = self.addHost('h12', ip='10.2.3.120/16') # Primärer DNS
        h13 = self.addHost('h13', ip='10.2.3.121/16') # Sekundärer DNS
        
        # FTP-Server
        h14 = self.addHost('h14', ip='10.2.4.130/16') # FTP-Server
        
        # =============================================================================
        # EXTERNES NETZWERK (10.3.0.0/16) - Internet-Zugang
        # =============================================================================
        # Externe Clients (Internet)
        h15 = self.addHost('h15', ip='10.3.1.200/16') # Externer Client 1
        h16 = self.addHost('h16', ip='10.3.1.201/16') # Externer Client 2
        h17 = self.addHost('h17', ip='10.3.1.202/16') # Externer Client 3
        
        # VPN-Gateway
        h18 = self.addHost('h18', ip='10.3.2.210/16') # VPN-Gateway
        
        # =============================================================================
        # SERVER-FARM (10.4.0.0/16) - Datenbanken und Anwendungen
        # =============================================================================
        # Datenbank-Server
        h19 = self.addHost('h19', ip='10.4.1.220/16') # MySQL-Server
        h20 = self.addHost('h20', ip='10.4.1.221/16') # PostgreSQL-Server
        
        # Anwendungs-Server
        h21 = self.addHost('h21', ip='10.4.2.230/16') # Java-App-Server
        h22 = self.addHost('h22', ip='10.4.2.231/16') # Python-App-Server
        
        # File-Server
        h23 = self.addHost('h23', ip='10.4.3.240/16') # NFS-Server
        h24 = self.addHost('h24', ip='10.4.3.241/16') # Samba-Server
        
        # =============================================================================
        # MANAGEMENT-NETZWERK (10.5.0.0/16) - Admin-Zugang
        # =============================================================================
        # Monitoring-Server
        h25 = self.addHost('h25', ip='10.5.1.250/16') # Nagios-Monitoring
        h26 = self.addHost('h26', ip='10.5.1.251/16') # Grafana-Dashboard
        
        # Backup-Server
        h27 = self.addHost('h27', ip='10.5.2.260/16') # Backup-Server
        
        # =============================================================================
        # VERBINDUNGEN
        # =============================================================================
        
        # Internes Netzwerk → Switch
        self.addLink(h1, s1)  # Büro-Client 1
        self.addLink(h2, s1)  # Büro-Client 2
        self.addLink(h3, s1)  # Büro-Client 3
        self.addLink(h4, s1)  # Entwickler 1
        self.addLink(h5, s1)  # Entwickler 2
        self.addLink(h6, s1)  # IT-Admin 1
        self.addLink(h7, s1)  # IT-Admin 2
        
        # DMZ → Switch
        self.addLink(h8, s1)   # Haupt-Webserver
        self.addLink(h9, s1)   # Backup-Webserver
        self.addLink(h10, s1)  # SMTP-Server
        self.addLink(h11, s1)  # IMAP-Server
        self.addLink(h12, s1)  # Primärer DNS
        self.addLink(h13, s1)  # Sekundärer DNS
        self.addLink(h14, s1)  # FTP-Server
        
        # Externes Netzwerk → Switch
        self.addLink(h15, s1)  # Externer Client 1
        self.addLink(h16, s1)  # Externer Client 2
        self.addLink(h17, s1)  # Externer Client 3
        self.addLink(h18, s1)  # VPN-Gateway
        
        # Server-Farm → Switch
        self.addLink(h19, s1)  # MySQL-Server
        self.addLink(h20, s1)  # PostgreSQL-Server
        self.addLink(h21, s1)  # Java-App-Server
        self.addLink(h22, s1)  # Python-App-Server
        self.addLink(h23, s1)  # NFS-Server
        self.addLink(h24, s1)  # Samba-Server
        
        # Management-Netzwerk → Switch
        self.addLink(h25, s1)  # Nagios-Monitoring
        self.addLink(h26, s1)  # Grafana-Dashboard
        self.addLink(h27, s1)  # Backup-Server

# Topologie registrieren
topos = { 'enterprise': (lambda: EnterpriseNetworkTopo()) } 