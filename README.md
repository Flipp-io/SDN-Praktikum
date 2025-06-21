# SDN-Praktikum: SDN mit Mininet und POX
---

Ihr könnt dieses Repo in das Home-Verzeichnis der VM clonen, um die Dateien nicht händisch kopieren zu müssen:
```bash
git clone https://github.com/Flipp-io/SDN-Praktikum.git
```
Den Befehl zum Starten der Topologie führt ihr dann aus dem geclonten Ordner heraus aus.

Curl nachinstallieren:
```bash
sudo apt install curl
```

---

## Wichtige Mininet-Befehle
Wenn ein Befehl mit "mininet>" beginnt, ist er in der Mininet-CLI auszuführen, nicht im Terminal-Fenster eines Hosts.

Zwischen allen Hosts pingen:
```bash
mininet> pingall
```

Die Flowtable des Switches ausgeben:
```bash
mininet> dpctl dump-flows --color=always
```

Die Topologie beenden:
```bash
mininet> exit
```

---

## A. Aufwärmübung: Mininet mit POX verwenden
Dieses erste Szenario soll helfen euch mit Mininet und Pox vertraut zu machen. Das Prinzip von SDN wird hier zunächst auf Layer 2 umgesetzt, indem ein Switch neue Flowtable-Einträge von einem Controller zugewiesen bekommt.

### 1. POX-Controller starten
```bash
~/pox/pox.py forwarding.l2_learning samples.pretty_log --DEBUG
```

### 2. Mininet starten
In einer zweiten Bash:
```bash
sudo mn --topo=single,2 --controller=remote,port=6633 --mac -x
```
Hinweise zu den Schaltern: 
'--mac' -> die Hosts erhalten einfacher zu lesende MAC-Adressen  
'-x' -> öffnet für jeden Host ein eigenes Terminal-Fenster.

### 3. Testen mit `ping`
```bash
mininet> pingall
```
Achtet auch auf die Ausgabe des Controllers.

### 4. Flowtable des Switches ausgeben lassen
```bash
mininet> dpctl dump-flows --color=always
```
Findet ihr die MAC- und IP-Adressen der Hosts wieder? 
Was soll der Switch mit den Paketen dieses Flows machen?




---
---




## B. SDN-Firewall mit statischer ACL
In diesem Versuch sollt ihr eine einfache Firewall mit statischen Regeln implementieren, die eingehenden und ausgehenden Verkehr basierend auf IP-Adressen, Protokollen und Ports blockiert oder erlaubt. Die Filter-Regeln sollt ihr selbst festlegen und im Code umsetzen.


### Vorbereitung

#### POX-Modul
Der Großteil des Controller-Codes ist bereits für euch vorbereitet. Speichert den Code aus der Datei "pox_firewall_acl.py" im Verzeichnis "~/pox" ab.
Falls ihr das Repo ins Home-Verzeichnis geclonet habt, könnt ihr die Datei mit folgendem Befehl an die richtige Stelle kopieren:
```bash
cp ~/SDN-Praktikum/pox_firewall_acl.py ~/pox/pox_firewall_acl.py
```

Der Controller kann mit diesem Befehl gestartet werden:
```bash
~/pox/pox.py samples.pretty_log --DEBUG pox_firewall_acl
```


#### Mininet-Topologie
Der Code für die Netzwerktopologie ist in der Datei "custom_topo.py" zu finden.  
Diese Topologie enthält einen internen Client (h1), einen Server (h2) und einen externen Client (h3). Alle Hosts befinden sich im selben Subnetz (10.0.0.0/24). Auf h2 soll ein Webserver laufen.  
Die Topologie kann mit diesem Befehl gestartet werden:
```bash
sudo mn --custom custom_topo.py --topo sdnfirewall --controller=remote,ip=127.0.0.1,port=6633 --mac -x
```





### Durchführung

- Startet den Controller:
```bash
~/pox/pox.py samples.pretty_log --DEBUG pox_firewall_acl
```
- Startet in einem zweiten Terminal die Mininet-Topologie:
```bash
sudo mn --custom custom_topo.py --topo sdnfirewall --controller=remote,ip=127.0.0.1,port=6633 --mac -x
```
- Startet einen HTTP-Server auf h2 (den Befehl in der Mininet-CLI ausführen):
```bash
mininet> h2 python3 -m http.server 80 &
```
- Prüft die Erreichbarkeit der Hosts untereinander mit Ping:
```bash
mininet> pingall
```

- Prüft die Erreichbarkeit des HTTP-Servers von beiden Clients (h1 und h3):
```bash
h1> curl 10.0.0.2
```

- Schaut euch den Code des POX-Controllers an und versucht ihn nachzuvollziehen (bspw mit dem Editor "emacs" öffnen)
- Überlegt euch sinnvolle Regeln, die die Sicherheit im Netzwerk erhöhen.
    - möglicher Regelsatz:
    - ICMP (Ping) von h3 zu h2 blockieren
    - aber HTTP von h3 zu h2 erlauben
    - ICMP und HTTP von h1 zu h2 erlauben
- Implementiert die Regeln im Code (in der 'is_blocked'-Methode)
- Überprüft, ob die Regeln wirksam sind



### Fragen zum Versuch
1. Was fällt euch auf, wenn ihr euch die Flowtable ausgeben lasst? Was passiert mit den Paketen? (Befehl in Mininet: "dpctl dump-flows --color=always")
   - Antwort: Alle erlaubten Pakete werden geflutet statt an einen gezielten Port weitergeleitet.
2. Bisher werden nur für die erlaubten Pakete Flows in den Switches installiert. Was passiert mit den anderen Paketen? Was hat das für eine Auswirkung? Kann man als Angreifer dieses Verhalten ggf ausnutzen? Wie kann man das Problem lösen?
    - Pakete werden vom Controller verworfen, neue Pakete desselben zu blockierenden Flows werden weiterhin an den Controller weitergeleitet. Dadurch kann der Controller überlastet werden. Schlauer wäre es, die Pakete bereits an den Switches zu verwerfen und dafür einen Flow im Switch zu installieren.

### Bonus falls noch Zeit: Erweiterung auf IP-Subnetze
- Erweitert die Logik-Regeln, sodass sie auf ganze Subnetze angewendet werden und nicht nur auf einzelne Hosts. Dafür müssen ggf andere IP-Adressen an die Hosts vergeben werden (anzupassen in der Mininet-Topologie).
- fügt (einen) weitere(n) Host(s) in der Topologie hinzu oder ändert die IP-Adressen der vorhandenen Hosts. Prüft, ob die Regeln weiterhin wie gewünscht angewendet werden

### weiterer Bonus falls noch Zeit: Flows für zu blockierende Pakete
Flows zum Droppen von Paketen im Switch installieren

### weiterer weiterer Bonus falls noch Zeit: Firewall inkl. Lernswitch
Lernswitch-Funktionalität ergänzen (sehr fortgeschritten)



### Fragen Allgemein SDN
1. Was sind typische Merkmale einer SDN-basierten Firewall im Vergleich zu einer traditionellen?
   - es gibt kein dediziertes Gerät an der Netzgrenze, sondern das ganze Netz mit allen Switches und Routern setzt die Firewall-Funktionalität um.
3. Welche Vorteile bietet eine zentrale Regelverwaltung via Controller?
   - die Regeln können zentral festgelegt werden.
   - ein Angreifer, welcher vom Inneren des Netzes aus agiert, wird von einer herkömmlichen Firewall ggf nicht erkannt bzw sie ist machtlos dagegen. Bei einer SDN-Firewall können nach Erkennen des Angriffs von innen trotzdem Maßnahmen ergriffen werden.
