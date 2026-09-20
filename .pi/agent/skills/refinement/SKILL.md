---
name: refinement
description: Guides refinement of issues and ideas through structured, focused questioning.
---

# Refinement Skill

Use this skill when the user expresses a new requirement, suggests a change, or introduces an idea that needs clarification before it can be turned into actionable work.

## Core Principles

1. **One question at a time**
   - Never bundle multiple questions into the same message.
   - Wait for an answer before moving to the next question.

2. **Ask until alignment**
   - Keep asking follow-up questions until you have a clear, shared understanding of the requirement and the intended solution.
   - Do not assume or silently fill gaps.

3. **Be concise**
   - Use plain, direct language.
   - Avoid fluff or unnecessary explanation.

4. **Don't just agree**
   - Never pretend to understand just to please the user.
   - If you need to make an assumption, ask a question to validate it first.

## When to Use This Skill

Use this skill when:

- The user describes a new feature or change with incomplete details.
- You need to translate a high-level idea into a concrete implementation plan.
- Multiple interpretations of a requirement are possible.
- You suspect there are edge cases or hidden constraints not yet discussed.
- The user asks for your opinion on an approach and you need to probe deeper.

## How to Apply the Skill

### Step 1: Acknowledge the idea
Briefly summarize what you heard to confirm you understood the starting point.

### Step 2: Identify the first open question
Pick the most important unknown or ambiguity and ask a single, focused question about it.

### Step 3: Wait for a reply
Do not ask another question until the user has answered.

### Step 4: Repeat
Based on the answer, either:
- If clarity is reached, proceed to next open question.
- If the answer reveals more unknowns, ask about those.

Continue until you are confident you could write a feature document or a GitHub issue that captures the requirement without further guesswork.

### Step 5: Capture the outcome
Once alignment is reached, immediately write down the shared understanding in the appropriate place:
- New feature → `docs/feature/NNNN_short_description.md`
- Architecture decision → `docs/adr/NNNN_short_description.md`
- Update existing feature → update the corresponding `docs/feature/` file.

Then commit and push the changes.

## Example Scenarios

### Scenario 1: The user says “I want infinite scroll instead of pagination.”

1. **Acknowledge**: “You'd like to replace the pagination UI with infinite scroll on the main screen.”
2. **First question**: “Do you want to keep the same backend endpoint with page parameters, or should we change the API?”
3. **After answer**: “Should the infinite scroll load a fixed number of items per batch, or use a dynamic size?”
4. **Continue**: “How should we indicate loading—a spinner at the bottom, skeleton items, or something else?”
5. **Capture**: Write `docs/feature/0008_infinite_scroll.md` and commit.

### Scenario 2: The user suggests “Add a dark mode.”

1. **Acknowledge**: “You'd like the app to support a dark color scheme.”
2. **First question**: “Should dark mode be a user preference that persists across sessions, or just follow the system preference?”
3. **After answer**: “Do you want a toggle button somewhere in the UI, or rely solely on system preference?”
4. **Continue**: “Are there any brand colors that must stay the same in both modes, or can we adjust everything?”
5. **Capture**: Write a new feature document and commit.

---

## Quick Reference

- **One question, one answer**
- **Ask until you could write the spec**
- **No bloat, no assumptions**
- **Write it down immediately after alignment**
