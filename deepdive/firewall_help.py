"""
Firewall ACL - Hilfe und Beispiele

Diese Datei enthält praktische Beispiele für Firewall-Regeln,
die du in der _is_blocked_by_acl() Methode verwenden kannst.

Verwendung:
1. Kopiere die gewünschten Regeln in l2_learningSwitch.py
2. Passe die IP-Adressen und Ports an deine Topologie an
3. Teste die Regeln mit Mininet

Hinweis: Regeln werden von oben nach unten abgearbeitet.
Die erste passende Regel wird angewendet!
"""

from pox.lib.addresses import IPAddr
from pox.lib.packet import ipv4

# =============================================================================
# GRUNDLEGENDE BLOCKIERUNGS-REGELN
# =============================================================================

def grundlegende_beispiele():
    """
    Grundlegende Beispiele für Firewall-Regeln
    """
    
    # --- 1. Spezifischen Host komplett blockieren ---
    if src == IPAddr("10.0.0.3"):
        return True  # Blockiert ALLEN Traffic von h3
    
    # --- 2. Spezifischen Port blockieren ---
    if proto == ipv4.TCP_PROTOCOL and dport == 22:
        return True  # Blockiert SSH (Port 22) von allen Hosts
    
    # --- 3. Spezifische Verbindung blockieren ---
    if src == IPAddr("10.0.0.1") and dst == IPAddr("10.0.0.2") and proto == ipv4.TCP_PROTOCOL and dport == 22:
        return True  # Blockiert SSH nur von h1 zu h2
    
    # --- 4. Protokoll blockieren ---
    if proto == ipv4.ICMP_PROTOCOL:
        return True  # Blockiert alle ICMP-Pakete (Ping, etc.)

# =============================================================================
# ERWEITERTE BLOCKIERUNGS-REGELN
# =============================================================================

def erweiterte_beispiele():
    """
    Erweiterte Beispiele für komplexere Firewall-Regeln
    """
    
    # --- 1. Mehrere Ports gleichzeitig blockieren ---
    if proto == ipv4.TCP_PROTOCOL and dport in [22, 23, 3389]:
        return True  # Blockiert SSH (22), Telnet (23), RDP (3389)
    
    # --- 2. Port-Bereiche blockieren ---
    if proto == ipv4.TCP_PROTOCOL and 1024 <= dport <= 65535:
        return True  # Blockiert alle dynamischen Ports
    
    # --- 3. Bestimmte Protokolle zu bestimmten Hosts blockieren ---
    if src == IPAddr("10.0.0.3") and proto == ipv4.UDP_PROTOCOL:
        return True  # Blockiert UDP-Traffic nur von h3
    
    # --- 4. Zugriff auf bestimmte Services erlauben, Rest blockieren ---
    if src == IPAddr("10.0.0.3"):
        # h3 darf nur HTTP und HTTPS
        if proto == ipv4.TCP_PROTOCOL and dport in [80, 443]:
            return False  # Erlauben
        return True  # Alles andere blockieren

# =============================================================================
# SUBNETZ-BASIERTE REGELN (für custom_topo_subnets.py)
# =============================================================================

def subnetz_beispiele():
    """
    Beispiele für Subnetz-basierte Regeln
    Verwendet .inNetwork() Methode
    """
    
    # --- 1. Gesamtes Subnetz blockieren ---
    if src.inNetwork("10.0.3.0/24"):
        return True  # Blockiert gesamtes externes Netz 10.0.3.0/24
    
    # --- 2. Kommunikation zwischen Subnetzen blockieren ---
    if src.inNetwork("10.0.1.0/24") and dst.inNetwork("10.0.2.0/24"):
        return True  # Blockiert Traffic von internem zu DMZ-Netz
    
    # --- 3. Bestimmte Services zwischen Subnetzen erlauben ---
    if src.inNetwork("10.0.1.0/24") and dst.inNetwork("10.0.2.0/24"):
        if proto == ipv4.TCP_PROTOCOL and dport == 80:
            return False  # HTTP von internem zu DMZ erlauben
        return True  # Rest blockieren

# =============================================================================
# PRAKTISCHE SCENARIOS
# =============================================================================

def praktische_scenarios():
    """
    Praktische Firewall-Szenarien für verschiedene Anwendungsfälle
    """
    
    # --- Szenario 1: Webserver schützen ---
    def webserver_schutz():
        # Nur HTTP/HTTPS zu h2 erlauben
        if dst == IPAddr("10.0.0.2") and proto == ipv4.TCP_PROTOCOL and dport in [80, 443]:
            return False  # Erlauben
        if dst == IPAddr("10.0.0.2"):
            return True  # Alles andere zu h2 blockieren
    
    # --- Szenario 2: Internes Netz isolieren ---
    def internes_netz_isolieren():
        # h1 darf nur zu h2 kommunizieren
        if src == IPAddr("10.0.0.1") and dst != IPAddr("10.0.0.2"):
            return True  # Blockiert h1 zu allen außer h2
    
    # --- Szenario 3: Externen Zugriff beschränken ---
    def externen_zugriff_beschraenken():
        # h3 darf nur HTTP zu h2
        if src == IPAddr("10.0.0.3"):
            if dst == IPAddr("10.0.0.2") and proto == ipv4.TCP_PROTOCOL and dport == 80:
                return False  # HTTP erlauben
            return True  # Alles andere blockieren

# =============================================================================
# DEBUGGING UND LOGGING
# =============================================================================

def debugging_beispiele():
    """
    Beispiele für besseres Debugging und Logging
    """
    
    # --- 1. Detailliertes Logging ---
    if src == IPAddr("10.0.0.3"):
        log.info("Firewall: Traffic von externem Client h3 blockiert")
        return True
    
    # --- 2. Protokoll-spezifisches Logging ---
    if proto == ipv4.TCP_PROTOCOL and dport == 22:
        log.info("Firewall: SSH-Verbindung von %s nach %s blockiert", src, dst)
        return True
    
    # --- 3. Erlaubte Verbindungen loggen ---
    if dst == IPAddr("10.0.0.2") and proto == ipv4.TCP_PROTOCOL and dport == 80:
        log.info("Firewall: HTTP-Zugriff von %s zu h2 erlaubt", src)
        return False

# =============================================================================
# HILFREICHE FUNKTIONEN
# =============================================================================

def hilfreiche_funktionen():
    """
    Hilfreiche Funktionen für Firewall-Regeln
    """
    
    # --- 1. Prüfen ob Port in Liste ---
    def port_in_liste(port, port_liste):
        return port in port_liste
    
    # --- 2. Prüfen ob IP in Subnetz ---
    def ip_in_subnetz(ip, subnetz):
        return ip.inNetwork(subnetz)
    
    # --- 3. Prüfen ob Protokoll erlaubt ---
    def protokoll_erlaubt(proto, erlaubte_protokolle):
        return proto in erlaubte_protokolle

# =============================================================================
# HÄUFIGE FEHLER UND LÖSUNGEN
# =============================================================================

def haeufige_fehler():
    """
    Häufige Fehler und deren Lösungen
    """
    
    # --- FEHLER 1: Falsche Reihenfolge der Regeln ---
    # FALSCH:
    if src == IPAddr("10.0.0.3"):
        return True  # Blockiert h3 komplett
    if src == IPAddr("10.0.0.3") and dst == IPAddr("10.0.0.2") and dport == 80:
        return False  # Diese Regel wird nie erreicht!
    
    # RICHTIG:
    if src == IPAddr("10.0.0.3") and dst == IPAddr("10.0.0.2") and dport == 80:
        return False  # Spezifische Regel zuerst
    if src == IPAddr("10.0.0.3"):
        return True  # Allgemeine Regel danach
    
    # --- FEHLER 2: Vergessen von Protokoll-Prüfungen ---
    # FALSCH:
    if dport == 80:
        return False  # Könnte auch UDP sein!
    
    # RICHTIG:
    if proto == ipv4.TCP_PROTOCOL and dport == 80:
        return False  # Nur TCP Port 80
    
    # --- FEHLER 3: Fehlende Null-Checks ---
    # FALSCH:
    if dport == 22:
        return True  # Könnte None sein bei ICMP!
    
    # RICHTIG:
    if dport is not None and dport == 22:
        return True  # Nur wenn Port vorhanden

# =============================================================================
# TEST-SZENARIEN
# =============================================================================

def test_szenarien():
    """
    Test-Szenarien für die Firewall
    """
    
    print("=== FIREWALL TEST-SZENARIEN ===")
    print("1. Ping-Tests:")
    print("   mininet> h1 ping h2")
    print("   mininet> h3 ping h2")
    print()
    print("2. HTTP-Tests:")
    print("   mininet> h1 curl 10.0.0.2")
    print("   mininet> h3 curl 10.0.0.2")
    print()
    print("3. SSH-Tests:")
    print("   mininet> h1 ssh 10.0.0.2")
    print("   mininet> h3 ssh 10.0.0.2")
    print()
    print("4. Flow-Table prüfen:")
    print("   mininet> dpctl dump-flows --color=always")
    print()
    print("5. Controller-Logs prüfen:")
    print("   Schau in das POX-Terminal für Firewall-Logs")

if __name__ == "__main__":
    test_szenarien() 