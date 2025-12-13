## Feature Name

**Added in v1.1.0**

[Full markdown content here including examples, explanations, etc.]

### Example: Use Case Description

```python
spafw37.add_params([{
    PARAM_NAME: 'example',
    # ... configuration
}])
```

This example demonstrates [behavior description].

[Additional explanation paragraphs]

See complete example in [`examples/example_file.py`](../examples/example_file.py).
````

**Tests:** Manual review to verify documentation clarity and accuracy

---

#### 6.2. Update API reference

**File:** `doc/api-reference.md`

Add documentation for the new constants and properties.

**Updates required:**

1. **Properties table** - Add new row:
   ```markdown
   | `PROPERTY_NAME` | Description of property. Added in v1.1.0. |
   ```

2. **Constants section** - Add constant definitions:
   ```markdown
   ### Constant Group Name
   
   **Added in v1.1.0**
   
   - **`CONSTANT_NAME`** (`'value'`)
     - Description of what it does
     - When to use it
   ```

3. **Functions section** (if applicable) - Document new functions:
   ```markdown
   ### `function_name(param1, param2)`
   
   **Added in v1.1.0**
   
   [Function description]
   
   **Parameters:**
   - `param1` - Description
   - `param2` - Description
   
   **Returns:**
   - Description of return value
   ```

**Tests:** Manual review to verify documentation completeness and accuracy

---

#### 6.3. Update README.md

**File:** `README.md`

Add references to the new functionality in three locations.

**Updates required:**

1. **Features list** - Add bullet point:
   ```markdown
   - Feature description with technical specifics
   ```

2. **Examples list** - Add new example entry:
   ```markdown
   - **`example_file.py`** - Demonstrates feature usage
   ```

3. **"What's New in v1.1.0" section** - Add concise one-line bullet:
   ```markdown
   - Feature description with key constants/functions (`CONSTANT1`, `CONSTANT2`)
   ```

**Tests:** Manual review to verify README clarity and consistency

[↑ Back to top](#table-of-contents)
````

**Key formatting rules:**

1. **Full markdown content** - When showing complete documentation sections (like parameters.md examples), wrap in ````markdown and include ALL content
2. **Specifications** - When showing specific updates (like API reference table rows), use numbered lists with markdown snippets in ```markdown blocks
3. **Concise for README** - README "What's New" entries should be single-line bullets, not multi-paragraph explanations
4. **Version annotations** - Always include "**Added in vX.Y.Z**" notes in documentation content
5. **Example links** - Link to example files with relative paths: `[examples/file.py](../examples/file.py)`
6. **Horizontal rule** - Always include `---` separator after intro paragraph, before first subsection