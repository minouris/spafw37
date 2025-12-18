---
applyTo: "**/*"
---

# Bash Command Instructions

This instruction file contains rules and best practices for embedding and running Bash commands in the repository (shell snippets in documentation, GitHub Actions `run:` blocks, development container scripts, and other places where Bash is used).

These rules are complementary to the general instructions and are intended to avoid common pitfalls that cause subtle parsing errors when code is copied, pasted into terminals, or embedded in multiline configuration blocks.

Rules

- **Avoid nesting back-ticks (`\`...\``) in shell examples or scripts.**
  - Reason: Back-tick style command substitution is error-prone when nested (the quoting and escaping becomes confusing) and can cause parsing issues when examples are copied into YAML `run:` blocks or here-documents.
  - Use the modern form `$(...)` for command substitution instead. Example:
    - Prefer: `result=$(grep -c "pattern" file.txt)`
    - Avoid: `` result=`grep -c "pattern" file.txt` ``

- **Do not include unescaped exclamation marks (`!`) inside double-quoted strings in examples or `run:` blocks.**
  - Reason: In interactive shells with history expansion enabled, `!` can trigger history expansion and cause unexpected content or syntax errors when the snippet is evaluated. This also affects some CI shells or when commands are executed inside `bash -lc` with certain flags.
  - If you need a literal exclamation mark inside a string, prefer one of these safe options:
    - Use single quotes: `echo 'Hello world!'` (single quotes prevent history expansion and interpolation).
    - Escape the character: `echo "Hello world\!"` (note the backslash). Be careful with layers of quoting when embedding in YAML.
    - Use a here-document with a quoted delimiter to prevent expansion: `cat <<'EOF'` ... `EOF`.

  - Style note: Prefer neutral, factual wording in terminal and CI messages (avoid using exclamation marks to "inject excitement"). This prevents accidental history‑expansion issues and keeps logs professional and easier to parse by humans and tools.

- **When embedding multiline shell in configuration files (for example, YAML `run:` blocks), keep quoting simple.**
  - Use single-quoted heredocs (`<<'EOF'`) if you need to include literal text that should not be expanded by the shell.
  - Avoid complex nested quotes and backtick usage inside such blocks.

- **When demonstrating shell commands in documentation, provide copyable commands.**
  - Avoid mixing prompt text and commands. Show only the command itself in fenced code blocks so users can copy-and-run without modification.

Examples

- Good (no backticks, no unescaped `!` inside double quotes):

```bash
WHEEL=$(ls dist/*.whl | head -n1)
python - <<'PY'
import zipfile, sys
with zipfile.ZipFile(WHEEL) as z:
    print('Found METADATA')
PY
```

- Problematic (nested backticks and unescaped `!` inside double quotes):

```bash
# Avoid this:
echo "Building project at `pwd`!"
```

Support

If you are unsure whether a particular shell snippet will behave correctly in CI or when embedded in YAML, paste it into a short shell script and run it in the devcontainer before committing. When in doubt, prefer a short Python helper for parsing tasks instead of complex shell pipelines.
