## Mermaid Diagram Examples

### Styling Support by Diagram Type

**Styling support varies by diagram type:**
- ✅ **Graph/Flowchart** (`graph TB`, `flowchart LR`): Full support for `classDef` and custom styling
- ❌ **Sequence diagrams** (`sequenceDiagram`): No custom styling - use participant prefixes `[Layer]`
- ❌ **Class diagrams** (`classDiagram`): No custom styling - rely on structure and annotations
- ⚠️  **State diagrams** (`stateDiagram-v2`): Limited styling support

---

### Example: Layer-Based Component Diagram

Shows layered architecture with components in each layer:

```mermaid
graph TB
    subgraph client["Client/External Layer"]
        webclient["Web Client<br/>(Browser)"]
        cli["CLI Tool"]
        ui_handler["UI Controller"]
    end
    
    subgraph adapter["Adapter Layer"]
        protocol["Protocol Handler"]
        transport["Transport Layer"]
        parser["Message Parser"]
    end
    
    subgraph control["Control Layer"]
        controller["Controller<br/>(Orchestration)"]
        dispatcher["Command Dispatcher"]
        state["State Store"]
    end
    
    subgraph backend["Backend Layer"]
        service["Core Service"]
        integration["Integration API"]
        processor["Data Processor"]
    end
    
    subgraph support["Supporting Components"]
        manager["Resource Manager"]
        worker["Worker<br/>(Async)"]
        logger["Logger"]
    end
    
    webclient -->|HTTP/JSON| protocol
    cli -->|HTTP/JSON| protocol
    webclient --> ui_handler
    ui_handler --> protocol
    protocol --> transport
    transport --> parser
    parser --> controller
    controller --> dispatcher
    dispatcher --> state
    dispatcher --> service
    service --> integration
    integration --> processor
    controller --> manager
    dispatcher --> worker
    protocol --> logger
    
    classDef clientExtStyle fill:#ffcccc,stroke:#cc0000,stroke-width:2px,color:#333
    classDef clientIntStyle fill:#ffe6e6,stroke:#e60000,stroke-width:2px,color:#333
    classDef adapterProtoStyle fill:#cce6ff,stroke:#0066cc,stroke-width:2px,color:#333
    classDef adapterTransStyle fill:#e6f7ff,stroke:#3399ff,stroke-width:2px,color:#333
    classDef adapterParseStyle fill:#f0f8ff,stroke:#66b3ff,stroke-width:2px,color:#333
    classDef controlCoreStyle fill:#d9b3ff,stroke:#6600cc,stroke-width:2px,color:#333
    classDef controlCmdStyle fill:#f2e6ff,stroke:#9933ff,stroke-width:2px,color:#333
    classDef controlStateStyle fill:#f9f0ff,stroke:#cc66ff,stroke-width:2px,color:#333
    classDef backendCoreStyle fill:#b3e6b3,stroke:#00cc66,stroke-width:2px,color:#333
    classDef backendIntegStyle fill:#e6ffe6,stroke:#33cc33,stroke-width:2px,color:#333
    classDef backendUtilStyle fill:#f0fff0,stroke:#66ff66,stroke-width:2px,color:#333
    classDef supportMgrStyle fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px,color:#333
    classDef supportWorkerStyle fill:#e1bee7,stroke:#9c27b0,stroke-width:2px,color:#333
    classDef supportUtilStyle fill:#f3e5f5,stroke:#ba68c8,stroke-width:2px,color:#333
    
    class webclient,cli clientExtStyle
    class ui_handler clientIntStyle
    class protocol adapterProtoStyle
    class transport adapterTransStyle
    class parser adapterParseStyle
    class controller controlCoreStyle
    class dispatcher controlCmdStyle
    class state controlStateStyle
    class service backendCoreStyle
    class integration backendIntegStyle
    class processor backendUtilStyle
    class manager supportMgrStyle
    class worker supportWorkerStyle
    class logger supportUtilStyle
    
    linkStyle default stroke:#8c8c8c,stroke-width:2px
```

---

### Example: Sequence Diagram

Shows message flow across components. **Note:** Sequence diagrams don't support custom colours - use participant prefixes to indicate layers.

```mermaid
sequenceDiagram
    participant Client as [Ext] Client
    participant Adapter as [Adapter] Protocol Handler
    participant Ctrl as [Control] Controller
    participant Backend as [Backend] Service
    
    Note over Client,Backend: Request Flow
    
    Client->>Adapter: Send request
    activate Adapter
    Note right of Adapter: Validate & parse
    Adapter->>Ctrl: Process command
    activate Ctrl
    Ctrl->>Backend: Execute operation
    activate Backend
    Backend-->>Ctrl: Result
    deactivate Backend
    Ctrl-->>Adapter: Response data
    deactivate Ctrl
    Adapter-->>Client: Send response
    deactivate Adapter
```

**Layer prefix convention:**
- `[Ext]` - Client/External Layer
- `[Adapter]` - Adapter Layer
- `[Control]` - Control Layer
- `[Backend]` - Backend/Data Layer
- `[Support]` - Supporting Components

---

### Example: Class Diagram

Shows class structure and relationships. **Note:** Class diagrams don't support custom styling - use clear naming and structure.

```mermaid
classDiagram
    class ProtocolHandler {
        <<Adapter>>
        -transport: Transport
        -parser: Parser
        +start()
        +stop()
        +handle_message(msg)
    }
    
    class Controller {
        <<Control>>
        -state: StateManager
        -dispatcher: CommandDispatcher
        +process_request(req)
        +get_state()
    }
    
    class Service {
        <<Backend>>
        -processor: DataProcessor
        +execute_operation(op)
        +query_data(query)
    }
    
    class ResourceManager {
        <<Support>>
        -resources: dict
        +acquire(id)
        +release(id)
    }
    
    ProtocolHandler --> Controller : sends request
    Controller --> Service : executes operation
    Controller --> ResourceManager : manages resources
    Service --> ResourceManager : uses resources
```

**Stereotype convention:**
- `<<Adapter>>` - Adapter Layer components
- `<<Control>>` - Control Layer components
- `<<Backend>>` - Backend/Data Layer components
- `<<Support>>` - Supporting components

---

### Example: Component with Synchronisation

Shows components with internal synchronisation primitives:

```mermaid
graph TB
    subgraph protocol["Protocol Handler (Adapter)"]
        server_main["Main Thread"]
        seq_lock["_seq_lock<br/>(Lock)"]
        stop_event["_stop<br/>(Event)"]
        accepted["_accepted<br/>(Event)"]
    end
    
    subgraph service["Core Service (Backend)"]
        service_thread["Service Thread"]
        cond_var["_cond<br/>(Condition)"]
        resource_lock["_resource_lock<br/>(Lock)"]
    end
    
    subgraph worker["Worker (Support)"]
        worker_thread["Worker Thread"]
        result_queue["result_queue<br/>(Queue)"]
    end
    
    server_main -.uses.-> seq_lock
    server_main -.signals.-> stop_event
    server_main -.waits.-> accepted
    
    service_thread -.uses.-> resource_lock
    service_thread -.waits/notifies.-> cond_var
    
    worker_thread -.puts.-> result_queue
    
    classDef adapterThreadStyle fill:#cce6ff,stroke:#0066cc,stroke-width:2px,color:#333
    classDef backendThreadStyle fill:#b3e6b3,stroke:#00cc66,stroke-width:2px,color:#333
    classDef supportThreadStyle fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px,color:#333
    classDef lockStyle fill:#ef9a9a,stroke:#c62828,stroke-width:2px,color:#333
    classDef condStyle fill:#90caf9,stroke:#1565c0,stroke-width:2px,color:#333
    classDef queueStyle fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#333
    classDef eventStyle fill:#fff59d,stroke:#f57f17,stroke-width:2px,color:#333
    
    class server_main adapterThreadStyle
    class service_thread backendThreadStyle
    class worker_thread supportThreadStyle
    class seq_lock,resource_lock lockStyle
    class cond_var condStyle
    class result_queue queueStyle
    class stop_event,accepted eventStyle
    
    linkStyle default stroke:#8c8c8c,stroke-width:2px
```

---

### Example: State Diagram

Shows component lifecycle and state transitions:

```mermaid
stateDiagram-v2
    [*] --> Uninitialized
    Uninitialized --> Initialized: initialize()
    Initialized --> Listening: start_server()
    Listening --> Connected: client connects
    Connected --> Paused: breakpoint hit
    Paused --> Running: continue
    Running --> Paused: breakpoint hit
    Connected --> Disconnected: client disconnect
    Disconnected --> Listening: wait for new client
    Listening --> Shutdown: stop()
    Connected --> Shutdown: stop()
    Paused --> Shutdown: stop()
    Running --> Shutdown: stop()
    Shutdown --> [*]
    
    note right of Connected
        
        State: "running"
        Active trace hooks
        
    end note
    
    note right of Paused
        
        State: "stopped"
        All threads frozen
        
    end note
```

---

### Example: Data Flow

Shows how data flows through system layers:

```mermaid
graph LR
    subgraph input["Input"]
        json["JSON<br/>Message"]
    end
    
    subgraph parse["Parse/Validate"]
        deserialize["Deserialize"]
        validate["Validate Schema"]
    end
    
    subgraph process["Process"]
        dispatch["Command<br/>Dispatcher"]
        execute["Execute<br/>Handler"]
    end
    
    subgraph backend["Backend"]
        service["Service<br/>Handler"]
        query["Data<br/>Query"]
    end
    
    subgraph output["Output"]
        serialize["Serialize<br/>Response"]
        response["JSON<br/>Response"]
    end
    
    json --> deserialize
    deserialize --> validate
    validate --> dispatch
    dispatch --> execute
    execute --> service
    service --> query
    query --> serialize
    serialize --> response
    
    classDef clientStyle fill:#ffe6e6,stroke:#cc0000,stroke-width:2px,color:#333
    classDef frontsideStyle fill:#e6f7ff,stroke:#0066cc,stroke-width:2px,color:#333
    classDef centralStyle fill:#f2e6ff,stroke:#6600cc,stroke-width:2px,color:#333
    classDef backendStyle fill:#e6ffe6,stroke:#00cc66,stroke-width:2px,color:#333
    
    class json,response clientStyle
    class deserialize,validate,serialize frontsideStyle
    class dispatch,execute centralStyle
    class service,query backendStyle
    
    linkStyle default stroke:#8c8c8c,stroke-width:2px
```

---

### Example: Thread Interaction

Shows how threads interact with shared resources:

```mermaid
graph TB
    subgraph main["Main Thread"]
        main_code["Application Code"]
    end
    
    subgraph server_thread["Server Thread"]
        accept["Accept Connections"]
        recv["Receive Messages"]
        send["Send Responses"]
    end
    
    subgraph service_thread["Service Thread"]
        process_request["process_request()"]
        handle_operation["handle_operation()"]
        prepare_response["prepare_response()"]
    end
    
    subgraph worker_thread["Worker Thread"]
        process_task["Process Task"]
        return_result["Return Result"]
    end
    
    subgraph shared["Shared State"]
        resource_state[("Resource<br/>State")]
        data_cache[("Data<br/>Cache")]
        event_queue[("Event<br/>Queue")]
    end
    
    main_code -.reads.-> resource_state
    recv -.writes.-> resource_state
    handle_operation -.reads.-> resource_state
    
    recv -.enqueues.-> event_queue
    process_request -.enqueues.-> event_queue
    send -.dequeues.-> event_queue
    
    process_task -.writes.-> data_cache
    send -.reads.-> data_cache
    
    classDef threadBoxStyle fill:#d9b3ff,stroke:#6600cc,stroke-width:2px,color:#333
    classDef sharedStyle fill:#fff59d,stroke:#f57f17,stroke-width:3px,color:#333
    
    class main_code,accept,recv,send,process_request,handle_operation,prepare_response,process_task,return_result threadBoxStyle
    class resource_state,data_cache,event_queue sharedStyle
    
    linkStyle default stroke:#8c8c8c,stroke-width:2px
```

---

### Example: Module Dependencies

Shows relationships between modules:

```mermaid
graph TB
    subgraph adapters["adapters"]
        protocol_handler["protocol_handler.py<br/>(Protocol)"]
        transport["transport.py<br/>(Transport)"]
        parser["parser.py<br/>(Serialization)"]
    end
    
    subgraph core["core"]
        controller["controller.py<br/>(Orchestration)"]
        dispatcher["dispatcher.py<br/>(Commands)"]
        state["state.py<br/>(State Mgmt)"]
    end
    
    subgraph backend["backend"]
        service["service.py<br/>(Core Service)"]
        processor["processor.py<br/>(Utilities)"]
    end
    
    subgraph integration["integration"]
        api_impl["api_impl.py<br/>(Integration)"]
        api["api.py<br/>(Utilities)"]
    end
    
    subgraph utils["utils"]
        resource_mgr["resource_mgr.py<br/>(Manager)"]
        worker["worker.py<br/>(Worker)"]
        logging["logging.py<br/>(Utility)"]
    end
    
    protocol_handler --> transport
    protocol_handler --> parser
    protocol_handler --> controller
    transport --> logging
    
    controller --> dispatcher
    controller --> state
    controller --> logging
    controller --> resource_mgr
    
    dispatcher --> service
    dispatcher --> api
    dispatcher --> worker
    
    service --> processor
    service --> api
    
    api_impl --> api
    
    classDef adapterProtoStyle fill:#cce6ff,stroke:#0066cc,stroke-width:2px,color:#333
    classDef adapterTransStyle fill:#e6f7ff,stroke:#3399ff,stroke-width:2px,color:#333
    classDef adapterParseStyle fill:#f0f8ff,stroke:#66b3ff,stroke-width:2px,color:#333
    classDef controlCoreStyle fill:#d9b3ff,stroke:#6600cc,stroke-width:2px,color:#333
    classDef controlCmdStyle fill:#f2e6ff,stroke:#9933ff,stroke-width:2px,color:#333
    classDef controlStateStyle fill:#f9f0ff,stroke:#cc66ff,stroke-width:2px,color:#333
    classDef backendCoreStyle fill:#b3e6b3,stroke:#00cc66,stroke-width:2px,color:#333
    classDef backendIntegStyle fill:#e6ffe6,stroke:#33cc33,stroke-width:2px,color:#333
    classDef backendUtilStyle fill:#f0fff0,stroke:#66ff66,stroke-width:2px,color:#333
    classDef supportMgrStyle fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px,color:#333
    classDef supportWorkerStyle fill:#e1bee7,stroke:#9c27b0,stroke-width:2px,color:#333
    classDef supportUtilStyle fill:#f3e5f5,stroke:#ba68c8,stroke-width:2px,color:#333
    
    class protocol_handler adapterProtoStyle
    class transport adapterTransStyle
    class parser adapterParseStyle
    class controller controlCoreStyle
    class dispatcher controlCmdStyle
    class state controlStateStyle
    class service backendCoreStyle
    class api_impl backendIntegStyle
    class processor,api backendUtilStyle
    class resource_mgr supportMgrStyle
    class worker supportWorkerStyle
    class logging supportUtilStyle
    
    linkStyle default stroke:#8c8c8c,stroke-width:2px
```

---