## Mermaid Best Practices

### General Guidelines

1. **Syntax Constraints**
   - **NEVER nest round parentheses inside square brackets** in node labels (e.g., `FA[Adapter(transport)]` is invalid)
   - Use line breaks instead: `FA[Adapter<br/>transport]`
   - Avoid bracketed notes inside square-bracket nodes
   - Use `note` keyword or separate shapes for annotations

2. **Diagram Size**
   - Create small, focused diagrams illustrating specific concepts
   - Avoid monolithic diagrams trying to show everything
   - Link related diagrams together

3. **Styling**
   - Always define and apply `classDef` styles for graph/flowchart diagrams
   - Sequence and class diagrams don't support custom styling
   - Use participant prefixes for sequence diagrams: `[Ext]`, `[Adapter]`, `[Control]`, `[Backend]`, `[Support]`

4. **Clarity**
   - Label connections clearly: "calls", "sends", "depends on", etc.
   - Use subgraphs to group related components
   - Keep layer colours consistent across all diagrams

5. **Notes and Colour Usage**
   - For state diagrams: Use empty lines before/after note text for visual spacing
   - For flowcharts (v11.3.0+): Use comment shapes `@{ shape: comment }` or text blocks `@{ shape: text }` for annotations
   - Style annotation nodes with light backgrounds and good text contrast
   - Avoid extreme colours like pure black (`#000`) or pure white (`#fff`) for text and backgrounds
   - Use softer colours like dark grey (`#333`) for text on light backgrounds
   - Ensure adequate contrast between link colours and background fills

5. **Notes and Annotations**
   - Add padding to notes for better readability (use background colours with good contrast)
   - Avoid extreme colours like pure black (#000) or pure white (#fff) for text and backgrounds
   - Use softer colours like dark grey (#333) for text on light backgrounds

---