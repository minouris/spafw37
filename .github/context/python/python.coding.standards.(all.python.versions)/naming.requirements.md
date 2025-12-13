## Naming Requirements

All members, from the biggest class to the smallest index variable, must have descriptive, meaningful names that convey their purpose and usage clearly.

**Rules:**
- Use full words, not abbreviations (e.g., `message_length` not `msg_len`)
- **NEVER** use single-letter names, even for loop indices - use `line_index`, `item_index`, etc.
- **NEVER** use lazy placeholder names like `tmp`, `data`, `result`, `val` - use specific descriptive names like `parsed_message`, `breakpoint_id`, `validation_result`
- Use an "owner_item" style of naming for clarity, e.g., `stack_frame` ("This is a frame in a stack") or `thread_id` ("This is the id of a thread")
- Do not prefix local variable or helper names with the local module or type name unless the prefix disambiguates across nearby scopes or meaningfully improves readability
- Use an owner prefix only when it avoids genuine ambiguity
- **Tests are NOT EXEMPT from these naming requirements** - test code must follow the same naming standards as production code

**Examples:**
```python
# Good:
for line_index in range(len(lines)):
    current_line = lines[line_index]
    parsed_result = parse_line(current_line)

# Bad:
for i in range(len(lines)):
    l = lines[i]
    result = parse_line(l)
```
