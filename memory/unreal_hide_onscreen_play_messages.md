---
name: unreal_hide_onscreen_play_messages
description: How the red/yellow on-screen Play (PIE) warning/error text was hidden — DisableAllScreenMessages in GameMode BeginPlay
metadata: 
  node_type: memory
  type: project
  originSessionId: f8f27f6f-9f70-41ca-9590-1da25c2ca728
---

2026-07-03: User complained that pressing Play shows red/yellow on-screen text (top-left of game viewport: e.g. RT over-budget, streaming pool, "LIGHTING NEEDS TO BE REBUILT", blueprint warnings — the GAreScreenMessagesEnabled overlay). Wanted them invisible.

**Fix (verified working):** Added `EventBeginPlay → Development|ExecuteConsoleCommand("DisableAllScreenMessages")` to **BP_Explorer_GameMode** (`/Game/ArchVizExplorer/Blueprints/BP_Explorer_GameMode`) EventGraph via MCP `write_graph_dsl`, compiled + saved. This is the GlobalDefaultGameMode (DefaultEngine.ini:235), so it runs for every level using it, incl. Glavniy_MirMIron (the main level). Verified via StartPIE + CaptureEditorImage: game viewport top-left clean, only the intended weather/time widget visible, no red/yellow debug text.

Notes:
- There is NO cvar for this (SearchCVars "ScreenMessage" returns empty); `DisableAllScreenMessages` is a console COMMAND, hence the BeginPlay-exec approach (same pattern as [[unreal_vr_perf_optimization]] / [[unreal_weather_panel_vr_pragulka]] BeginPlay console commands).
- Covers levels using BP_Explorer_GameMode. If Pragulka/VR use a different GameMode and still show messages, add the same node to their GameMode/pawn BeginPlay.
- To re-enable messages for debugging: run `EnableAllScreenMessages` in console, or remove the node.
