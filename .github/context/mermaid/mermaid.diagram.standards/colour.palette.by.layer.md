## Colour Palette by Layer

Use consistent colours to represent different architectural layers. Each layer uses a family of related colours to distinguish between external-facing, internal, and supporting components.

### Client/External Layer
**Use for:** External interfaces, user-facing components, CLI tools

#### External Components (user-facing)
- **Fill:** `#ffcccc` (medium red/pink)
- **Stroke:** `#cc0000` (dark red)
- **Text:** `#333` (dark grey)
- **Semantic meaning:** Direct user interaction points

#### Internal Client Components
- **Fill:** `#ffe6e6` (light red/pink)
- **Stroke:** `#e60000` (medium-dark red)
- **Text:** `#333` (dark grey)
- **Semantic meaning:** Client-side logic, UI controllers

---

### Adapter Layer (Protocol/Transport)
**Use for:** Protocol adapters, transport handlers, serialisation, authentication

#### Protocol Handler (external-facing)
- **Fill:** `#cce6ff` (medium blue)
- **Stroke:** `#0066cc` (dark blue)
- **Text:** `#333` (dark grey)
- **Semantic meaning:** Protocol implementation, message routing

#### Transport Layer
- **Fill:** `#e6f7ff` (light blue)
- **Stroke:** `#3399ff` (medium blue)
- **Text:** `#333` (dark grey)
- **Semantic meaning:** Socket handling, stream management

#### Serialisation/Parsing
- **Fill:** `#f0f8ff` (very light blue)
- **Stroke:** `#66b3ff` (light-medium blue)
- **Text:** `#333` (dark grey)
- **Semantic meaning:** Message parsing, data serialisation

---

### Control Layer
**Use for:** Core orchestration, state management, command processing

#### Core Controller (orchestration)
- **Fill:** `#d9b3ff` (medium purple)
- **Stroke:** `#6600cc` (dark purple)
- **Text:** `#333` (dark grey)
- **Semantic meaning:** Main control flow, session management

#### Command Processing
- **Fill:** `#f2e6ff` (light purple)
- **Stroke:** `#9933ff` (medium purple)
- **Text:** `#333` (dark grey)
- **Semantic meaning:** Command dispatch, request handling

#### State Management
- **Fill:** `#f9f0ff` (very light purple)
- **Stroke:** `#cc66ff` (light-medium purple)
- **Text:** `#333` (dark grey)
- **Semantic meaning:** State storage, cache management

---

### Backend/Data Layer
**Use for:** Data access, runtime integration, instrumentation

#### Core Backend
- **Fill:** `#b3e6b3` (medium green)
- **Stroke:** `#00cc66` (dark green)
- **Text:** `#333` (dark grey)
- **Semantic meaning:** Core backend logic, runtime integration

#### Integration Layer
- **Fill:** `#e6ffe6` (light green)
- **Stroke:** `#33cc33` (medium green)
- **Text:** `#333` (dark grey)
- **Semantic meaning:** External system integration

#### Utilities
- **Fill:** `#f0fff0` (very light green)
- **Stroke:** `#66ff66` (light-medium green)
- **Text:** `#333` (dark grey)
- **Semantic meaning:** Helper functions, utilities

---

### Supporting Components
**Use for:** Cross-cutting concerns, utilities, helpers

#### Managers (cross-cutting)
- **Fill:** `#ce93d8` (medium purple/magenta)
- **Stroke:** `#7b1fa2` (dark purple)
- **Text:** `#333` (dark grey)
- **Semantic meaning:** Resource management, coordination

#### Workers/Async Components
- **Fill:** `#e1bee7` (light purple/magenta)
- **Stroke:** `#9c27b0` (medium purple)
- **Text:** `#333` (dark grey)
- **Semantic meaning:** Background processing, async operations

#### Utilities/Helpers
- **Fill:** `#f3e5f5` (very light purple/magenta)
- **Stroke:** `#ba68c8` (light-medium purple)
- **Text:** `#333` (dark grey)
- **Semantic meaning:** Helper functions, common utilities

### Synchronisation Primitives
**Use for:** Locks, conditions, queues, events

- **Locks:** Fill `#ef9a9a`, Stroke `#c62828`, Text `#333`
- **Conditions:** Fill `#90caf9`, Stroke `#1565c0`, Text `#333`
- **Queues:** Fill `#fff9c4`, Stroke `#f57f17`, Text `#333`
- **Events:** Fill `#fff59d`, Stroke `#f57f17`, Text `#333`

---