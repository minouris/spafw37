## Colour Selection Guide

Choose the appropriate style based on the component's architectural role:

| Layer | Role | Style Class | Colour Family |
|-------|------|-------------|---------------|
| **Client/External** | User-facing, external | `clientExtStyle` | Medium red/pink |
| | Internal client logic | `clientIntStyle` | Light red/pink |
| **Adapter** | Protocol handling | `adapterProtoStyle` | Medium blue |
| | Transport/streams | `adapterTransStyle` | Light blue |
| | Parsing/serialisation | `adapterParseStyle` | Very light blue |
| **Control** | Core orchestration | `controlCoreStyle` | Medium purple |
| | Command processing | `controlCmdStyle` | Light purple |
| | State management | `controlStateStyle` | Very light purple |
| **Backend** | Core backend logic | `backendCoreStyle` | Medium green |
| | Integration layer | `backendIntegStyle` | Light green |
| | Backend utilities | `backendUtilStyle` | Very light green |
| **Support** | Managers | `supportMgrStyle` | Medium magenta |
| | Workers/async | `supportWorkerStyle` | Light magenta |
| | Utilities/helpers | `supportUtilStyle` | Very light magenta |

**Rule of thumb:** Darker shades = external-facing or core functionality, lighter shades = internal or supporting functionality.

---