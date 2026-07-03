---
name: feedback_restart_was_done_stop_blaming_it
description: "User DID restart the Editor every time after each config fix — stop using \"you didn't restart\" as the explanation for the RT/streaming over-budget error"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c850d648-44a8-4d31-b58b-65150fc12222
---

2026-07-03: User (angrily, correctly) stated that every time I changed a config value and told them to restart, they DID fully restart the Editor — and the RT-geometry / texture-streaming "over budget" error STILL did not change. I had repeatedly written "needs Editor restart / the #1 reason fixes don't take effect is no restart" across many memories and session replies.

**Why this matters:** "you didn't restart" is FALSE and must stop being the go-to explanation. If a restart-required ini fix was applied AND the user restarted AND the symptom is unchanged, that is strong evidence the fix pulls the WRONG LEVER, not that it wasn't loaded.

**How to apply:** For the [[unreal_gpu_crash_lumen_hwrt_pagefault]] / [[unreal_rt_geometry_budget_fix]] / [[unreal_scalability_duplicate_section_and_rt_flipflop]] over-budget saga, the real live causes (verified in working-tree files this session) are:
1. `DefaultDeviceProfiles.ini` [Windows DeviceProfile] still has `r.RayTracing.Shadows=True` + `Skylight=True`, OVERRIDING `DefaultEngine.ini`'s False at runtime — so every Play rebuilds RT shadow/skylight geometry regardless of restart. These 2 lines were never reconciled between the files (I left them "because it flip-flopped 6x" — that was the mistake).
2. Per Epic Ray Tracing Performance Guide: pool size is a SOFT limit; LOD-less meshes (Cesium Google 3D Tiles, Level/Export CAD props) are NEVER evicted → over budget no matter the pool number. `15,999 EiB` is UE's overflow readout. NO ini value can fix LOD-less geometry — needs Generate Ray Tracing Proxies / real LODs, or disable RT on Cesium.

Verify current file state before ever claiming a cause again; do not reflexively blame restart. See [[unreal_play_error_rt_streaming_fix]].
