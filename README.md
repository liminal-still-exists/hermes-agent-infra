```mermaid
flowchart TB
    Router["공유기<br/>WOL 포트만 개방"]

    subgraph Computer["컴퓨터"]
        subgraph Windows["Windows"]
            TS["Tailscale"]

            subgraph TaskScheduler["작업 스케줄러"]
                Lock["LockAfterAutoLogon.ps1"]
                RC["remote_control.py"]
            end

            Monitor["TurnOffMonitor.ps"]
        end

        subgraph WSL["WSL"]
            Net["Mirrored Mode Networking"]

            subgraph Hermes["Hermes Agent"]
                WebUI["Hermes WebUI"]
                Hindsight["Hindsight"]
                Webhook["/monitor-off 웹훅"]
                Script["monitor-off.py"]
            end
        end
    end

    Router --> Windows
    TS --> Net
    RC --> Webhook
    Webhook --> Script
    Script --> Monitor

    classDef network fill:#e8f3ff,stroke:#4385c6,color:#173b60
    classDef automation fill:#fff0dc,stroke:#c98b35,color:#694313
    classDef service fill:#e8f5e9,stroke:#579b61,color:#24552b

    class Router,TS,Net network
    class Lock,RC,Monitor,Webhook,Script automation
    class WebUI,Hindsight service

    style Computer fill:none,stroke:#777,stroke-width:1px
    style Windows fill:none,stroke:#777,stroke-width:1px
    style WSL fill:none,stroke:#777,stroke-width:1px
    style Hermes fill:none,stroke:#777,stroke-width:1px
    style TaskScheduler fill:none,stroke:#777,stroke-width:1px
```
