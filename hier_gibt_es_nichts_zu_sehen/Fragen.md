### Fragen 
1. Was fällt euch auf, wenn ihr euch die Flowtable ausgeben lasst? Was passiert mit den Paketen? (Befehl in Mininet: "dpctl dump-flows --color=always")
   - Antwort: Alle erlaubten Pakete werden geflutet statt an einen gezielten Port weitergeleitet.

2. Bisher werden nur für die erlaubten Pakete Flows in den Switches installiert. Was passiert mit den anderen Paketen? Was hat das für eine Auswirkung? Kann man als Angreifer dieses Verhalten ggf ausnutzen? Wie kann man das Problem lösen?
    - Pakete werden vom Controller verworfen, neue Pakete desselben zu blockierenden Flows werden weiterhin an den Controller weitergeleitet. Dadurch kann der Controller überlastet werden. Schlauer wäre es, die Pakete bereits an den Switches zu verwerfen und dafür einen Flow im Switch zu installieren.

3. Was ist der Unterschied zwischen einer SDN-basierten Firewall und einer traditionellen?
   - es gibt kein dediziertes Gerät an der Netzgrenze, sondern das ganze Netz mit allen Switches und Routern setzt die Firewall-Funktionalität um.

4. Welche Vorteile bietet die Regelverwaltung via SDN-Controller gegenüber einer herkömmlichen Firewall?
   - die Regeln können zentral festgelegt werden.
   - ein Angreifer, welcher vom Inneren des Netzes aus agiert, wird von einer herkömmlichen Firewall ggf nicht erkannt bzw sie ist machtlos dagegen. Bei einer SDN-Firewall können nach Erkennen des Angriffs trotzdem Maßnahmen ergriffen werden (wie ein IDS/IPS)
