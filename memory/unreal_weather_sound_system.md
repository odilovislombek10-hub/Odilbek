---
name: unreal_weather_sound_system
description: Weather/season-driven audio for BP_WeatherTime_Widget — sunny ambient + rain/snow footsteps done 2026-07-03
metadata: 
  node_type: memory
  type: project
  originSessionId: bbc80fbe-7b23-49c1-be34-530a8bd784cd
---

User task (Uzbek): BP_WeatherTime_Widget (runs in ArchViz Explorer on Play, sunny by default) needs season-matched sound. Sunny=city ambient (cars/people/pleasant), snow/rain=changes like winter/rain. Pragulka /Game/ThirdPerson: walking character needs footstep sounds when walking in snow/rain.

**KEY FINDING:** Project has NO city/traffic/crowd/footstep audio of its own — only UDS weather sounds (Rain, Snow/Snow_Compress, Wind, Puddles, Thunder, Dust) + VRTemplate fire. UDS "Enable Weather Sound Effects" was ALREADY = true on all 3 level UDW actors (rain/snow/wind auto-play when widget changes weather — Directional+Global WeatherSounds MetaSounds wired). The ONLY gap was "Environment Sound" = None (why sunny was silent).

**What I did (2026-07-03):**
1. AMBIENT (all 3 levels: Glavniy_MirMIron, Pragulka, VR): set UDW actor "Environment Sound" = /Game/UltraDynamicSky/Sound/Environment/Forest_Example (class UDS_Environment_Sound_C). This is the pleasant clear-weather ambient; UDS auto-ducks it in rain/snow so sound "changes per weather." Forest birds = PLACEHOLDER for city (user chose "use existing sounds"; no city asset exists). To swap: import city .wav → make a UDS_Environment_Sound from it → set that property. Saved via AssetTools.save_assets (UDW is NOT external actor — save_actor fails, must save the level asset).
2. FOOTSTEPS (Pragulka BP_ThirdPersonCharacter1): user chose snow+rain only (no dry/concrete step, no such asset). Added vars UDW_Ref (Ultra_Dynamic_Weather_C obj ref) + FootstepCooldown (float). New function graphs: EnsureUDW (lazy GetAllActorsOfClass caches UDW_Ref), PlayStepSound (IsValid UDW → GetSnow/GetRain via Class|UltraDynamicWeather|GetSnow/GetRain; snow>0.15→Snow_Compress_1, elif rain>0.15→Puddle_01, random pitch 0.85-1.15 for variation), Footstep(DeltaSeconds) (calls EnsureUDW; gate speed>20 via VectorLengthXY + IsMovingOnGround; cadence = Clamp(125/speed,0.25,0.55)s). Wired via surgical EventTick(ReceiveTick)→CallFunction|Footstep (create_node+connect_pins, NOT write_graph_dsl). Compiled clean. PIE-verified Pragulka runs error-free (no Accessed None), movement intact.

**CRITICAL LESSON — read_graph_dsl is LOSSY on BP_ThirdPersonCharacter1 EventGraph:** it showed Move/Look/Jump EnhancedInput events as EMPTY, but find_nodes proved 33 nodes exist (Knots/MacroInstance/CallFunction movement logic). write_graph_dsl REPLACES the whole graph → would DESTROY movement. NEVER rewrite that EventGraph via DSL; use surgical add_event/create_node/connect_pins. DSL round-trip is safe only for NEW/simple graphs. See [[unreal_weather_panel_vr_pragulka]] [[unreal_uds_weather_realism_tuning]].

**MCP DSL notes:** variable getter type_id strips underscores (UDW_Ref var → Variables|Default|GetUDWRef). Self-context component getters (Variables|Character|GetCharacterMovement) take NO positional arg; actor library fns (Transformation|GetVelocity/GetActorLocation) take optional self target. Custom fn call = CallFunction|FnName. Utilities|IsValid is multi-exec branch (terminates flow — can't sequence after; isolate in own fn). PlaySound=Audio|PlaySoundatLocation.
