## CRITICAL: Writing Style

### UK English
- Use UK English spelling and conventions (colour, behaviour, organise, centre, licence, defence)
- Use metric units (metres, kilometres, kilograms, Celsius, litres)
- Use internationally neutral examples (avoid US-specific geography, conventions, or cultural references)

### Tone and Voice

**Use dispassionate, matter-of-fact technical writing:**
- ✅ `unset_param()` removes parameter value completely from configuration.
- ❌ `unset_param()` provides a flexible way to remove parameter values.
- ✅ `PARAM_IMMUTABLE` constant marks parameter as write-once.
- ❌ `PARAM_IMMUTABLE` is an exciting new constant that gives you powerful protection.

**No marketing language:**
- Avoid: "exciting", "powerful", "elegant", "clever", "beautiful", "revolutionary", "innovative"
- Avoid: "enhanced", "improved" (without specific metrics)
- Use: factual descriptions of what the code does

**No internal development jargon:**
- Avoid: "flexible resolution", "semantic richness", "orthogonal concerns"
- Use: clear, specific technical descriptions users can understand
- If technical terms are necessary, define them clearly on first use

**Function descriptions format:**
```
function_name() does X. Raises ErrorType if Y.
```

**Tense usage:**
- Present tense for what exists: "function returns value", "parameter defines behaviour"
- Past tense for historical changes: "added support for", "fixed issue where"