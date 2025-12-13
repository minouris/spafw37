## Quick Reference: Styling Classes

**Use with graph/flowchart diagrams only** (sequence and class diagrams don't support custom styling):

```
%% Client/External Layer
classDef clientExtStyle fill:#ffcccc,stroke:#cc0000,stroke-width:2px,color:#333
classDef clientIntStyle fill:#ffe6e6,stroke:#e60000,stroke-width:2px,color:#333

%% Adapter Layer
classDef adapterProtoStyle fill:#cce6ff,stroke:#0066cc,stroke-width:2px,color:#333
classDef adapterTransStyle fill:#e6f7ff,stroke:#3399ff,stroke-width:2px,color:#333
classDef adapterParseStyle fill:#f0f8ff,stroke:#66b3ff,stroke-width:2px,color:#333

%% Control Layer
classDef controlCoreStyle fill:#d9b3ff,stroke:#6600cc,stroke-width:2px,color:#333
classDef controlCmdStyle fill:#f2e6ff,stroke:#9933ff,stroke-width:2px,color:#333
classDef controlStateStyle fill:#f9f0ff,stroke:#cc66ff,stroke-width:2px,color:#333

%% Backend Layer
classDef backendCoreStyle fill:#b3e6b3,stroke:#00cc66,stroke-width:2px,color:#333
classDef backendIntegStyle fill:#e6ffe6,stroke:#33cc33,stroke-width:2px,color:#333
classDef backendUtilStyle fill:#f0fff0,stroke:#66ff66,stroke-width:2px,color:#333

%% Supporting Components
classDef supportMgrStyle fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px,color:#333
classDef supportWorkerStyle fill:#e1bee7,stroke:#9c27b0,stroke-width:2px,color:#333
classDef supportUtilStyle fill:#f3e5f5,stroke:#ba68c8,stroke-width:2px,color:#333

%% Synchronisation Primitives
classDef lockStyle fill:#ef9a9a,stroke:#c62828,stroke-width:2px,color:#333
classDef condStyle fill:#90caf9,stroke:#1565c0,stroke-width:2px,color:#333
classDef queueStyle fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#333
classDef eventStyle fill:#fff59d,stroke:#f57f17,stroke-width:2px,color:#333
```
Then apply with:

```
class protocol adapterProtoStyle
class transport adapterTransStyle
class parser adapterParseStyle
```

---