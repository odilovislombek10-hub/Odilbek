---
name: unreal_gpu_crash_lumen_hwrt_pagefault
description: "2026-07-02 GPU crash root cause = Lumen HWRT async-compute \"RayTracing Miss\" DMA page fault (NOT VRAM); fixed with r.Lumen.HardwareRayTracing.Async=0"
metadata: 
  node_type: memory
  type: project
  originSessionId: 2b9892c0-b8e2-4a69-8c90-b6d11a9be984
---

2026-07-02 22:43 Editor GPU crash (LoginId 1dfbd1744acdccdc5c1d2ca6243bb017). Callstack was all UnrealEditor_D3D12RHI → Core → kernel32 → ntdll.

**Root cause (from NVIDIA Aftermath dump, decoded in Saved/Crashes/UECC-Windows-55F2AC...9_0001):**
- CrashType=GPUCrash, Status=PageFault, Type=**RayTracing Miss**, Device state=Error_DMA_PageFault.
- Active GPU work at crash: LumenSceneLighting / LumenScreenProbeGather on the **AsyncCompute** pipeline.
- VRAM was FINE: Local Budget 23554 MB, Used only 10827 MB → **NOT an out-of-memory crash.** It's Lumen Hardware Ray Tracing dereferencing a freed/invalid BVH resource in an async-compute race.

**Why:** engine is actually **UE 5.8** (`C:\Program Files\Epic Games\UE_5.8\`), config comments say 5.5 — mismatch, not the cause. `r.GPUCrashDebugging=0` meant DRED had no breadcrumb, but Aftermath still pinpointed HWRT.

**Fix applied to project Config/DefaultEngine.ini (2026-07-02):**
- `r.Lumen.HardwareRayTracing.Async=0` — forces HWRT onto the graphics queue, kills the async-compute page-fault race. Minimal quality cost. Added in Lumen section.
- `r.GPUCrashDebugging=1` — added near top so next crash gives exact resource breadcrumb.
- Also removed deprecated `r.Mobile.VirtualTextures=True` (was firing a separate handled Ensure; crash folder 63B853... — that Ensure is NOT the GPU crash).

**Fallback if crash recurs:** set `r.Lumen.HardwareRayTracing=0` (Software RT) — 100% removes RT page faults, slightly lower reflection quality. This is the "safe" tier the user was offered.

Needs **Editor restart** to take effect. Do NOT random-flip r.RayTracing.Shadows/Skylight for this — Aftermath proved it's HWRT async, see [[unreal_scalability_duplicate_section_and_rt_flipflop]] and [[unreal_rt_geometry_budget_fix]] and [[unreal_play_error_rt_streaming_fix]].
