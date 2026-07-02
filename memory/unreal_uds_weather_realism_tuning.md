---
name: unreal-uds-weather-realism-tuning
description: "Root cause + fix for 'weather buttons change particles but not the sky/atmosphere' — UDS weather presets had too-mild Cloud Coverage; boosted values + full research report on UDS/PPV realistic-weather config"
metadata: 
  node_type: memory
  type: project
  originSessionId: ac84b74e-558b-4078-9ede-d2f19855d9c6
---

2026-07-02 (session ac84b74e). Follow-up to [[unreal_uds_weather_panel_progress]]. User report: clicking Rain/Snow buttons spawns particles (so `ChangeWeather` + `BP_UDW` work), BUT the sky/atmosphere/lighting does NOT change — stays sunny; Cloudy button does nothing visible.

**ROOT CAUSE (confirmed empirically):** The UDS weather presets (`/Game/UltraDynamicSky/Blueprints/Weather_Effects/Weather_Presets/*`, class `UDS_Weather_Settings_C`) had far-too-mild `Cloud Coverage` values relative to the level's baseline (~3.808). Original: Clear_Skies CC=0/Fog=0, Cloudy CC=5/Fog=1, Overcast CC=7.5/Fog=1.5, Rain CC=7.5/Fog=3/Rain=7, Snow CC=8.5/Fog=5/Snow=6. So Rain only nudged clouds 3.8→7.5 = barely visible → "stays sunny." Particles (Rain=7/Snow=6) applied fine, decoupled visually from the weak cloud change.

**KEY SCALE FACT:** UDS `Cloud Coverage` on THIS project is NOT 0–1 (a research agent wrongly claimed 0–1). Empirical scale ~0–20+: baseline 3.8 = light scattered, 9 = clearly cloudy, 15 = overcast/rainy grey (city still visible), 17 = heavy flat overcast, 18/Fog6 = too foggy (horizon lost). `Fog` prop ~0–6 useful range. Verified by setting UDW `Cloud Coverage`/`Fog` directly in EDITOR (PostEditChange updates the sky live) + CaptureViewport.

**FIX APPLIED (presets edited via ObjectTools.set_properties on `<preset>.<preset>` + saved via save_assets):** Clear_Skies CC=1.5/Fog=0, Cloudy CC=9/Fog=1.5, Overcast CC=17/Fog=3.5, Rain CC=15/Fog=5 (Rain=7 kept), Snow CC=13/Fog=4 (Snow=6 kept). Verified each look in-editor by simulating on the level UDW + capture: Cloudy=nice grey partly-cloudy, Overcast=dark flat, Rain(15/4)=moody overcast rainy — all clearly distinct from sunny. NOTE presets are shared UDS plugin content (affect all 3 levels; may be overwritten on a UDS plugin update).

**Widget/graph is CORRECT & unchanged by this** — weather buttons OnClicked_Event_12..15 → `ChangeWeather(preset,3.0)` on cached `BP_UDW`; Winter OnClicked_Event_18 = SetSeason(3)+ChangeWeather(Snow). UDW↔UDS link verified: UDW prop `ultraDynamicSky` = Ultra_Dynamic_Sky_C_0. `ChangeWeather` applies the whole weather-state struct (particles prove it) so boosted CC now transitions too. The earlier ×60→×100 TIME fix did NOT cause this (unrelated). EventTick change-detection is correct (Branch then→SetLastSlider→ApplyTime; only fires on slider change, not every frame).

**STILL TODO (research-backed polish, not yet applied — user wants full realistic viz):** Full report saved this session covers: (1) DISABLE UDS auto-exposure ("Set Exposure/Use Exposure Range" = OFF on UDS actor) to stop it overriding PPV — confirmed UDS forces its exposure over all PPVs. (2) Add an Unbound Post Process Volume: Manual exposure (EV0) for cinematic OR Auto Histogram Min0/Max2 + Local Exposure ON for walk-through; Motion Blur OFF, Chromatic Aberration OFF, Bloom ~0.5, Vignette ~0.3, Film Grain ~0.1. (3) Per-weather color grading (Temperature: sunny 5800-6200K, overcast 6800-7200K + Sat 0.9, rain 6800-7400K cool + Sat 0.85, snow 7000-8000K cold, golden-hour 4500-5200K warm). (4) Lumen GI Final Gather Quality 2–4, Reflections Quality 2–4/MaxBounces 2+ (keep HWRT async OFF per [[unreal_gpu_crash_lumen_hwrt_pagefault]]). Sources: UDS Docs V9, William Faucher, Brushify UDW, Jay Versluis (disable UDS exposure), Epic PPV/Auto-Exposure docs. Benchmark studio: nca373.ru (North Caucasus Architects) — UE5 real-time archviz explorer w/ dynamic weather/time as a headline feature, material configurator, drone/first-person/vehicle modes, 4K photo mode.

Level not saved (UDW instance edits transient; widget overrides at runtime). Presets ARE saved. See [[unreal_uds_weather_panel_progress]], [[feedback_respond_in_uzbek]].
