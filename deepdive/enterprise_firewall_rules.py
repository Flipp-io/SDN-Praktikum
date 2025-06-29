"""
Enterprise Firewall Rules für L3 Switch

Diese Datei enthält erweiterte Firewall-Regeln für die Enterprise-Topologie.
Die Regeln implementieren realistische Sicherheitsrichtlinien für ein Unternehmensnetzwerk.

Netzwerk-Segmente:
- 10.1.0.0/16: Internes Netzwerk (Büros, Entwickler, IT-Admins)
- 10.2.0.0/16: DMZ (öffentliche Server)
- 10.3.0.0/16: Externes Netzwerk (Internet)
- 10.4.0.0/16: Server-Farm (Datenbanken, Anwendungen)
- 10.5.0.0/16: Management-Netzwerk (Admin-Zugang)

Verwendung:
1. Kopiere diese Regeln in die _is_blocked_by_acl() Methode des L3 Switches
2. Passe die Regeln an deine spezifischen Anforderungen an
3. Teste die Regeln mit der Enterprise-Topologie
"""

from pox.lib.addresses import IPAddr
from pox.lib.packet import ipv4

def enterprise_firewall_rules(src, dst, proto, dport):
    """
    Enterprise Firewall Rules - Erweiterte Sicherheitsrichtlinien
    
    Args:
        src: Quell-IP-Adresse
        dst: Ziel-IP-Adresse
        proto: Protokoll-ID
        dport: Zielport
        
    Returns:
        bool: True wenn Paket blockiert werden soll
    """
    
    # =============================================================================
    # GRUNDLEGENDE SICHERHEITSREGELN
    # =============================================================================
    
    # Regel 1: Gesamten Traffic aus externem Netzwerk blockieren (Standard)
    if src.inNetwork("10.3.0.0/16"):
        # Ausnahmen für erlaubte Services definieren
        if dst.inNetwork("10.2.0.0/16"):
            # Externe Clients dürfen nur auf DMZ-Server zugreifen
            if proto == ipv4.TCP_PROTOCOL and dport in [80, 443]:  # HTTP/HTTPS
                return False  # Erlauben
            if proto == ipv4.TCP_PROTOCOL and dport == 21:  # FTP
                return False  # Erlauben
            if proto == ipv4.TCP_PROTOCOL and dport == 25:  # SMTP
                return False  # Erlauben
            if proto == ipv4.UDP_PROTOCOL and dport == 53:  # DNS
                return False  # Erlauben
        return True  # Alles andere aus externem Netz blockieren
    
    # =============================================================================
    # DMZ-ZUGRIFFSREGELN
    # =============================================================================
    
    # Regel 2: Internes Netzwerk → DMZ (eingeschränkter Zugriff)
    if src.inNetwork("10.1.0.0/16") and dst.inNetwork("10.2.0.0/16"):
        # Büro-Mitarbeiter dürfen nur HTTP/HTTPS
        if src.inNetwork("10.1.1.0/24"):
            if proto == ipv4.TCP_PROTOCOL and dport in [80, 443]:
                return False  # Erlauben
            return True  # Alles andere blockieren
        
        # Entwickler dürfen mehr Services
        if src.inNetwork("10.1.2.0/24"):
            if proto == ipv4.TCP_PROTOCOL and dport in [80, 443, 22, 21]:  # HTTP, HTTPS, SSH, FTP
                return False  # Erlauben
            return True  # Alles andere blockieren
        
        # IT-Admins dürfen alles zur DMZ
        if src.inNetwork("10.1.3.0/24"):
            return False  # Alles erlauben
    
    # =============================================================================
    # SERVER-FARM ZUGRIFFSREGELN
    # =============================================================================
    
    # Regel 3: Zugriff auf Server-Farm (nur intern und Management)
    if dst.inNetwork("10.4.0.0/16"):
        # Nur internes Netzwerk und Management-Netzwerk dürfen zugreifen
        if not (src.inNetwork("10.1.0.0/16") or src.inNetwork("10.5.0.0/16")):
            return True  # Blockieren
        
        # Spezifische Port-Regeln für Datenbanken
        if dst.inNetwork("10.4.1.0/24"):  # Datenbank-Server
            if proto == ipv4.TCP_PROTOCOL and dport in [3306, 5432]:  # MySQL, PostgreSQL
                return False  # Erlauben
            return True  # Andere Ports blockieren
        
        # Anwendungs-Server
        if dst.inNetwork("10.4.2.0/24"):
            if proto == ipv4.TCP_PROTOCOL and dport in [8080, 8000, 22]:  # Java, Python, SSH
                return False  # Erlauben
            return True  # Andere Ports blockieren
    
    # =============================================================================
    # MANAGEMENT-NETZWERK ZUGRIFFSREGELN
    # =============================================================================
    
    # Regel 4: Management-Netzwerk (nur IT-Admins)
    if dst.inNetwork("10.5.0.0/16"):
        if not src.inNetwork("10.1.3.0/24"):  # Nur IT-Admins
            return True  # Blockieren
    
    # =============================================================================
    # SPEZIFISCHE SERVER-REGELN
    # =============================================================================
    
    # Regel 5: Webserver-Zugriff
    if dst == IPAddr("10.2.1.100") or dst == IPAddr("10.2.1.101"):  # Webserver
        if proto == ipv4.TCP_PROTOCOL and dport in [80, 443]:
            return False  # HTTP/HTTPS erlauben
        return True  # Andere Ports blockieren
    
    # Regel 6: Mailserver-Zugriff
    if dst == IPAddr("10.2.2.110"):  # SMTP-Server
        if proto == ipv4.TCP_PROTOCOL and dport == 25:
            return False  # SMTP erlauben
        return True  # Andere Ports blockieren
    
    if dst == IPAddr("10.2.2.111"):  # IMAP-Server
        if proto == ipv4.TCP_PROTOCOL and dport in [143, 993]:  # IMAP, IMAPS
            return False  # IMAP erlauben
        return True  # Andere Ports blockieren
    
    # Regel 7: DNS-Server-Zugriff
    if dst == IPAddr("10.2.3.120") or dst == IPAddr("10.2.3.121"):  # DNS-Server
        if proto == ipv4.UDP_PROTOCOL and dport == 53:
            return False  # DNS erlauben
        return True  # Andere Ports blockieren
    
    # Regel 8: FTP-Server-Zugriff
    if dst == IPAddr("10.2.4.130"):  # FTP-Server
        if proto == ipv4.TCP_PROTOCOL and dport in [21, 20]:  # FTP Control, Data
            return False  # FTP erlauben
        return True  # Andere Ports blockieren
    
    # =============================================================================
    # DATENBANK-ZUGRIFFSREGELN
    # =============================================================================
    
    # Regel 9: MySQL-Server (nur für Anwendungen)
    if dst == IPAddr("10.4.1.220"):  # MySQL-Server
        if src.inNetwork("10.4.2.0/24"):  # Nur von Anwendungs-Servern
            if proto == ipv4.TCP_PROTOCOL and dport == 3306:
                return False  # MySQL erlauben
        return True  # Andere blockieren
    
    # Regel 10: PostgreSQL-Server (nur für Anwendungen)
    if dst == IPAddr("10.4.1.221"):  # PostgreSQL-Server
        if src.inNetwork("10.4.2.0/24"):  # Nur von Anwendungs-Servern
            if proto == ipv4.TCP_PROTOCOL and dport == 5432:
                return False  # PostgreSQL erlauben
        return True  # Andere blockieren
    
    # =============================================================================
    # MONITORING-ZUGRIFFSREGELN
    # =============================================================================
    
    # Regel 11: Monitoring-Server (nur IT-Admins)
    if dst == IPAddr("10.5.1.250") or dst == IPAddr("10.5.1.251"):  # Monitoring
        if src.inNetwork("10.1.3.0/24"):  # Nur IT-Admins
            if proto == ipv4.TCP_PROTOCOL and dport in [80, 443, 22]:  # Web, SSH
                return False  # Erlauben
        return True  # Andere blockieren
    
    # =============================================================================
    # VPN-ZUGRIFFSREGELN
    # =============================================================================
    
    # Regel 12: VPN-Gateway (eingeschränkter Zugriff)
    if dst == IPAddr("10.3.2.210"):  # VPN-Gateway
        if proto == ipv4.UDP_PROTOCOL and dport == 500:  # IKE
            return False  # VPN-Protokoll erlauben
        if proto == ipv4.UDP_PROTOCOL and dport == 4500:  # NAT-T
            return False  # VPN-NAT erlauben
        return True  # Andere Ports blockieren
    
    # =============================================================================
    # ICMP-REGELN (Ping)
    # =============================================================================
    
    # Regel 13: ICMP nur innerhalb von Subnetzen erlauben
    if proto == ipv4.ICMP_PROTOCOL:
        # Internes Netzwerk darf sich selbst pingen
        if src.inNetwork("10.1.0.0/16") and dst.inNetwork("10.1.0.0/16"):
            return False  # Erlauben
        
        # IT-Admins dürfen alle Subnetze pingen
        if src.inNetwork("10.1.3.0/24"):
            return False  # Erlauben
        
        # Management-Netzwerk darf sich selbst pingen
        if src.inNetwork("10.5.0.0/16") and dst.inNetwork("10.5.0.0/16"):
            return False  # Erlauben
        
        return True  # Andere ICMP blockieren
    
    # =============================================================================
    # STANDARD-REGELN
    # =============================================================================
    
    # Regel 14: Internes Netzwerk darf sich frei bewegen
    if src.inNetwork("10.1.0.0/16") and dst.inNetwork("10.1.0.0/16"):
        return False  # Erlauben
    
    # Regel 15: Management-Netzwerk darf sich frei bewegen
    if src.inNetwork("10.5.0.0/16") and dst.inNetwork("10.5.0.0/16"):
        return False  # Erlauben
    
    # Regel 16: Server-Farm interne Kommunikation
    if src.inNetwork("10.4.0.0/16") and dst.inNetwork("10.4.0.0/16"):
        return False  # Erlauben
    
    # Standard: Paket erlauben (Default-Deny wäre sicherer)
    return False

def demo_scenarios():
    """
    Demo-Szenarien für die Enterprise Firewall
    """
    print("=== ENTERPRISE FIREWALL DEMO-SZENARIEN ===")
    print()
    print("1. EXTERNE ZUGRIFFE TESTEN:")
    print("   mininet> h15 ping h8")  # Externer Client → Webserver (sollte funktionieren)
    print("   mininet> h15 ping h19") # Externer Client → MySQL (sollte blockiert werden)
    print()
    print("2. INTERNE ZUGRIFFE TESTEN:")
    print("   mininet> h1 ping h8")   # Büro-Client → Webserver (sollte funktionieren)
    print("   mininet> h1 ping h19")  # Büro-Client → MySQL (sollte blockiert werden)
    print()
    print("3. ENTWICKLER-ZUGRIFFE TESTEN:")
    print("   mininet> h4 ping h21")  # Entwickler → Java-Server (sollte funktionieren)
    print("   mininet> h4 ssh h21")   # SSH von Entwickler (sollte funktionieren)
    print()
    print("4. IT-ADMIN-ZUGRIFFE TESTEN:")
    print("   mininet> h6 ping h25")  # IT-Admin → Monitoring (sollte funktionieren)
    print("   mininet> h6 ssh h25")   # SSH von IT-Admin (sollte funktionieren)
    print()
    print("5. DATENBANK-ZUGRIFFE TESTEN:")
    print("   mininet> h21 telnet h19 3306")  # App-Server → MySQL (sollte funktionieren)
    print("   mininet> h1 telnet h19 3306")   # Büro-Client → MySQL (sollte blockiert werden)
    print()
    print("6. HTTP-ZUGRIFFE TESTEN:")
    print("   mininet> h15 curl 10.2.1.100")  # Externer → Webserver (sollte funktionieren)
    print("   mininet> h15 curl 10.4.2.230")  # Externer → App-Server (sollte blockiert werden)
    print()
    print("7. FLOW-TABLE PRÜFEN:")
    print("   mininet> dpctl dump-flows --color=always")
    print()
    print("8. CONTROLLER-LOGS PRÜFEN:")
    print("   Schau in das POX-Terminal für Firewall-Logs")

if __name__ == "__main__":
    demo_scenarios() 