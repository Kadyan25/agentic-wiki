# Quick Structure Check

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: structure, validation, review, quickcheck, code

## Summary
# Quick Structure Check

A **quick structure check** is a rapid review process to verify that something (code, writing, data, system, or physical entity) is organized correctly, follows expected patterns, and maintains integrity. It prioritizes breadth over depth—flagging *what* is wrong rather than always explaining *why*. It applies to documents, codebases, data formats, databases, APIs, architecture designs, and more.

**Purpose:** Identify structural errors, inconsistencies, missing components, or integrity issues early before deeper review or deployment. The focus is on *form* over *detail*—a surface-level integrity check that should take minutes, not hours. It is *not* a substitute for thorough review, but rather a first-pass filter to catch obvious problems fast.

**Output:** Pass/fail status, checklist result, or short list of flagged issues.

**Common checks include:** Proper formatting and syntax, required fields/sections present, correct nesting or hierarchy, no broken links or references, consistent naming conventions, expected data types and values, logical flow and organization.

## Checks by Domain

**📝 Writing / Documents:** Clear intro, body, and conclusion; consistent heading hierarchy (H1 → H2 → H3); logical section order and flow; no orphaned sections or missing transitions.

**💻 Code / Software:** Functions/classes properly defined and scoped; syntax correct; imports and dependencies declared properly; no orphaned or unreachable blocks; function signatures match expectations; file/folder organization follows conventions; proper indentation and formatting.

**📊 Data / Spreadsheets & Databases:** Column headers present and consistent; no missing required fields; correct data types per column; table relationships and constraints intact; schema matches expected structure; no null values in required fields; foreign keys valid.

**🌐 API / JSON / XML:** Validate against schema (e.g., JSON Schema, XSD); required keys/tags present; correct data types used.

**🏗️ Systems / Architecture / Engineering:** Components correctly connected with no circular dependencies; endpoints properly defined with matching request/response schemas; layers follow defined patterns (e.g., MVC, microservices); load paths, connections, and material integrity sound; entry/exit points identifiable.

## Quick Check Steps

1. **Define scope** — What type of structure are you checking?
2. **Identify required elements** — What should be there?
3. **Apply a checklist or linter** — Use automated tools where possible (ESLint, markdownlint, JSONLint)
4. **Scan for missing/broken parts** — What's absent or malformed?
5. **Flag anomalies and prioritize** — Syntax errors, missing sections, broken links; distinguish critical vs. minor issues
6. **Summarize findings** — Document pass/fail status or list of issues for follow-up

## Tips for Effectiveness

✅ Use **automated tools** (linters, validators, schema checkers)
✅ Keep a **standardized checklist** for consistency
✅ Time-box the review—keep it brief and focused
✅ Specify *what type* of structure you want checked for targeted review
✅ Prioritize **hierarchy and consistency** over perfection
⚠️ Don't confuse structure with content quality—they are separate reviews

## Key Points
- See summary above for detailed points.

## Related Topics

