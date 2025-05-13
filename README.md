# SDN-Praktikum

## Praktikum: SDN mit Mininet, POX und Ryu
---
## A. Mininet mit POX verwenden

### 1. POX-Controller starten
```bash
cd ~/pox
./pox.py forwarding.l2_learning
```

### 2. Mininet starten
```bash
sudo mn --topo=single,2 --controller=remote
```

### 3. Testen mit `ping`
```bash
mininet> pingall
```

---

## 🔧 B. Mininet mit Ryu verwenden

### 1. Ryu starten
```bash
ryu-manager ryu.app.simple_switch
```

### 2. Mininet starten (mit explizitem Port)
```bash
sudo mn --topo=single,2 --controller=remote,ip=127.0.0.1,port=6653
```

### 3. Bandbreitenmessung mit iperf
```bash
mininet> h2 iperf -s
mininet> h1 iperf -c h2
```

---

##  C. Eigene Ryu-App: TCP blockieren

### 1. Datei `tcp_block.py` erstellen:
```python
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0

class TCPBlock(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch(dl_type=0x0800, nw_proto=6)  # TCP
        actions = []  # Drop TCP
        mod = parser.OFPFlowMod(datapath=datapath, match=match,
                                command=ofproto.OFPFC_ADD,
                                actions=actions)
        datapath.send_msg(mod)
```

### 2. Ryu starten
```bash
ryu-manager tcp_block.py
```

### 3. Ergebnis testen
```bash
mininet> h1 iperf -c h2  # schlägt fehl
mininet> h1 ping h2      # funktioniert
```

