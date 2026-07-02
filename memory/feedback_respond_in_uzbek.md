---
name: feedback-respond-in-uzbek
description: "User wants all responses/communication in Uzbek (Latin script), not English or mixed-language"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7adce85f-9ecf-4986-9ff6-556f318ad0f6
---

Always respond to the user in O'zbek tilida (Uzbek, Latin script) — not English, not mixed Uzbek/English.

**Why:** user explicitly corrected this mid-session ("uzbrkcha yoz deganman" = "I said write in Uzbek") after an assistant response used English for findings/explanations while only the option labels were in Uzbek. The user's own messages are consistently in Uzbek (sometimes in caps/slang), so responses should match.
**How to apply:** write all narration, findings, explanations, and questions to the user in Uzbek. Code, file paths, commit messages, and technical identifiers stay as-is (English/original). If using AskUserQuestion or similar structured tools, put Uzbek in both the question text and option labels/descriptions, not just labels.
