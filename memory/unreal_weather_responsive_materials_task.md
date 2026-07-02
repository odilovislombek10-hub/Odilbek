---
name: unreal-weather-responsive-materials-task
description: "PENDING user task (crashed before starting): make Glavniy_MirMIron materials react to UltraDynamicSky weather/season — wet asphalt+puddles+raindrop ripples in rain, snow on ground+walls in winter, as one universal optimized material"
metadata: 
  node_type: memory
  type: project
  originSessionId: aa5d47bd-1a99-45a5-8267-f7746d4ca737
---

**User's original command (recovered 2026-07-03 from local transcript session `a0e9b6d8`, 2026-07-02T17:39; the work CRASHED Unreal when first attempted so this section was never done — user re-asked in session `8e9840ef` 18:36 and again `aa5d47bd` / current).** Conversation transcripts (.jsonl) are NOT in git — only `memory/` + audit JSON are committed (auto_commit pushes to the sibling `Muslimatun` repo `D:\...\Unreal Engine\Muslimatun`, still no jsonl). Transcripts live locally at `C:\Users\Windows 11\.claude\projects\D--...-Odilbek\*.jsonl` (30 sessions); recover user commands via PowerShell ConvertFrom-Json per line filtering type=='user'.

**Exact command (Uzbek, verbatim):** "BP_WeatherTime_Widget BIZDA SHU WIDGET BOR ULTRA DIYNAMIC SKAY BUNI UZING QILDING, ENDI BUNDAY QILISH KERAK GLAVNI LEVELDAGI MATERIALLARNI ULTRA DIYNAMC SKAYGA MOSLAB YOMGIR YOGANDA MIDOL UCHUN ASFALT SUV BULISH KERAK SUV TUPLANGAN JOYLAR BULISH KERAK YOMGIR ASFALTGA TUSHGANDA ASFALTDAGI TUPLANGAN SUVLARGA TOPCHI TUHGANI BILINISH KERAK DEVOR TEXTURALARIDAHAM SHUNDAY BULISH KERAK, QOR YOGANDAHAM HUDDA SHUNDAY BULISH KERAK MATERIALLARNI SHUNAQA QILIB UNIVERSAL MATERIAL QILIB OPTIMIZATSIYA QILISH KERAK"

**Requirement, decoded:**
- Make **Glavniy_MirMIron** level materials respond to UltraDynamicSky weather/season (the [[unreal_uds_weather_panel_progress]] BP_WeatherTime_Widget already drives UDS weather/season).
- **Rain:** asphalt gets wet (darker + higher specular/lower roughness), puddles form in low spots, visible raindrop ripple impacts on the pooled water.
- **Winter/snow:** snow accumulation on ground AND on wall textures (up-facing surfaces).
- Do it as ONE **universal material** (a shared master with weather params driven globally) — optimized, not per-asset hand-editing.
- User-identified target materials so far: **`M_Asphalt_base_Inst1`** = asphalt, **`M_Grass`** = lawn/gazon. (More surfaces — walls — to be enumerated.)

**Approach notes (not yet started):** UDS ships a global weather-wetness/snow system — typical integration is a Material Parameter Collection (MPC) or global scalar/vector params (`Wetness`, `Snow Amount`) that UltraDynamicWeather writes each frame, which surface master materials read to blend a wet/snow layer (world-space up-vector mask for snow, puddle mask from a noise/heightmap for water, panner-driven ripple normal for rain impacts). Check UDS docs/blueprints for the exact MPC/param names it already exposes (`/Game/UltraDynamicSky/...`) BEFORE authoring a new material — UDS likely already has "Post Process Materials" / "Wetness" hooks (`Ultra_Dynamic_Weather` has wetness & snow settings). **CAUTION: this crashed Unreal on first attempt — start small (one material, e.g. M_Asphalt_base_Inst1), save often, watch for the Lumen HWRT async GPU crash [[unreal_gpu_crash_lumen_hwrt_pagefault]].**

See [[unreal_uds_weather_panel_progress]], [[unreal_wood_material_shading_model_fix]], [[feedback_respond_in_uzbek]].
