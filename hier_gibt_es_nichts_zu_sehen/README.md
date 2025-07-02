Dieser Ordner enthält die Musterlösung.  
Seid bitte fair.

- Regelsatz der Musterlösung:
    - keinen Traffic vom externen Client zulassen bis auf Zugriff auf den HTTP-Server
    - der interne Client darf alles, bis auf SSH zu h2
- zusätzliche Mögliche Regeln:
    - ICMP (Ping) von h3 zu h2 blockieren
    - aber HTTP von h3 zu h2 erlauben
    - ICMP und HTTP von h1 zu h2 erlauben