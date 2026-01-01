# Step 4: Implement change-create-component.md Prompt

**File:** [.github/prompts/change-create-component.md](../../../.github/prompts/change-create-component.md)

**Purpose:** Add new component when introducing new feature area

## Table of Contents

1. [Get Component Information](#1-get-component-information)
2. [Validate Component ID](#2-validate-component-id)
3. [Add to Component Identification](#3-add-to-component-identification)
4. [Create GitHub Label](#4-create-github-label)
5. [Update Tracking Issue #98](#5-update-tracking-issue-98)

---

## Detailed Implementation Actions

### 1. Get Component Information

**Interaction:** User prompts

- Ask user for component ID (validate format: subject-domain-aspect, 3-5 letters per group)
- Ask user for component name (short, descriptive)
- Ask user for component description (one sentence)
- Ask user for category (Features/Tools/Documentation)
- Ask user for first milestone (current or specific version)

### 2. Validate Component ID

**Tools:** `run_in_terminal` (gh issue)

- Check Component ID format matches pattern: `{subject}-{domain}-{aspect}`
- Verify each part is 3-5 letters
- Subject must be `feat`, `tool`, or `docs`
- **Fetch from GitHub issue #98** - Use `gh issue view 98 --json body -q .body` to pull current content as source of truth
- Parse Component Identification tables from issue content
- Check for component ID collisions

### 3. Add to Component Identification

**Tools:** `replace_string_in_file`

- Determine correct category table in Component Identification section
- Create table row:
  - Component: Component ID
  - Name: Component name
  - Description: Component description
  - First Milestone: First milestone
  - Status: "Active"
- Insert row in alphabetical order within category
- **Update workspace file** - Use `replace_string_in_file` to write modified content to [CHANGES-ACTIVE.md](../../CHANGES-ACTIVE.md)

### 4. Create GitHub Label

**Tools:** `run_in_terminal` (gh label create)

- Use GitHub CLI to create label: `gh label create "{component-id}" --color ededed --description "{component-name}"`
- Label name: Component ID
- Label colour: #ededed (grey)
- Label description: Component name

### 5. Update Tracking Issue #98

**Tools:** `run_in_terminal` (gh issue)

- **Push modified Component Identification** - Use `gh issue edit 98 --body` to update GitHub issue #98
- Post comment with `gh issue comment 98 --body`: "Added component: {component-id} ({component-name})"
