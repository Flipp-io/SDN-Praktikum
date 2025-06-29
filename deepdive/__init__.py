"""
SDN Deepdive Package

Erweiterte SDN-Implementierungen mit Firewall-Funktionalität und Enterprise-Netzwerk-Topologien.

Verfügbare Module:
- l2_switch_with_firewall: L2 Learning Switch mit Firewall
- l3_switch_with_firewall: Layer 3 Switch mit Firewall
- enterprise_network_topo: Enterprise-Netzwerk Topologie
- enterprise_firewall_rules: Enterprise Firewall Rules
- firewall_help: Firewall ACL Hilfe und Beispiele
"""

__version__ = "1.0.0"
__author__ = "SDN-Praktikum"
__description__ = "Advanced SDN implementations with firewall functionality"

# Verfügbare Module
__all__ = [
    'l2_switch_with_firewall',
    'l3_switch_with_firewall', 
    'enterprise_network_topo',
    'enterprise_firewall_rules',
    'firewall_help'
] 