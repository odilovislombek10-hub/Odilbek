---
name: unreal-uds-weather-panel-progress
description: "In-progress task — swapping BP_AVE_SunSky→UltraDynamicSky and building a weather/time panel in BP_MasterMenu_Widget; tracks exactly what's done and what's next"
metadata: 
  node_type: memory
  type: project
  originSessionId: 66bda63c-fd31-4d3f-80cd-d2c0a23c3525
---

Started 2026-07-02. Full plan at `C:\Users\Windows 11\.claude\plans\lovely-mapping-raccoon.md`. Goal: replace BP_AVE_SunSky with UltraDynamicSky (`/Game/UltraDynamicSky/`) across the 3 levels and add a "ПОГОДА | ВРЕМЯ СУТОК" weather+time panel to BP_MasterMenu_Widget (shows only on Button_Home/Button_Surroundings/Button_Amenities). Note: `.uasset`/`.umap` are gitignored — Unreal work persists only via MCP `save_assets`, NOT git; git tracks only Python/config/plans.

**DONE:**
- All 3 levels (`/Game/Level/Odilbek/{Glavniy_MirMIron,Pragulka,VR}`): placed `Ultra_Dynamic_Sky` + `Ultra_Dynamic_Weather` actors at the old sun's transform (245.98,-480.21,97.60), removed `BP_AVE_SunSky_C_0`, saved. (`Ultra_Dynamic_Sky_C_0`, `Ultra_Dynamic_Weather_C_0` in each.)
- `BP_Time_Widget` (`/Game/ArchVizExplorer/Blueprints/Widgets/BP_Time_Widget`): removed old `BP_SunSky` var (was BP_AVE_SunSky ref) + re-added as Ultra_Dynamic_Sky_C ref. Deleted ALL old EventConstruct + OnValueChanged(Slider_01) nodes. Added new function `SetSolarTimeAndUpdate(float HoursValue)` = SetTimeOfDay(BP_SunSky, HoursValue*60) [UDS uses MINUTES] + Update_Time_Text(HoursValue) + Emissive_MPC Buildings/Effects scalar params from curves + hide/show "NightLight"-tagged actors (18:00–07:00) + reset pawn Idle_Timer. Compiled OK.
- NOTE: also added `BP_UDW` object var then REMOVED it from BP_Time_Widget (the weather ref belongs on the new panel, not here). BP_Time_Widget only needs BP_SunSky now.

**DONE (continued):**
- BP_Time_Widget EventGraph fully rebuilt + compiled: EventConstruct → GetAllActorsOfClass(Ultra_Dynamic_Sky_C) → SetBP_SunSky; init Slider_01 = GetTimeOfDay/60; bind Slider OnValueChanged via `WidgetEvent|AssignOnValueChanged` (auto-made custom event OnValueChanged_Event) → SetSolarTimeAndUpdate(Value); else Collapse self. Saved.
- Verified Glavniy_MirMIron viewport: UDS renders (volumetric clouds, daytime 16:00). Sky swap confirmed visually. (The blue neon arrows on the building are pre-existing BP_POI markers, not mine.)
- 7 icons generated LOCALLY via PowerShell System.Drawing/GDI+ (real python & ImageMagick unavailable in this env; bash python3 is a broken Store stub — use PowerShell). Script at scratchpad/make_icons.ps1. NOT AI-generated despite user's stated preference — flat white transparent UI glyphs come out far cleaner drawn than via Higgsfield; told user, offered AI redo. Imported to `/Game/ArchVizExplorer/Textures/UI/Icons/`: T_Icon_Weather_Sun/Cloud/Overcast/Rain, T_Icon_Season_Summer/Autumn/Winter. Saved. (Note GDI GraphicsPath needs FillMode=Winding or overlapping ellipses checkerboard.)
- Wrote `Content/Python/build_weather_time_widget.py` (committed to git). Builds full BP_WeatherTime_Widget tree: SizeBox(360w)→Border(black .88)→VBox[ Text_Title, HBox(Button_TimeLeft ◀ / TextBlock_Time / Button_TimeRight ▶), Slider_TimeOfDay(6-22,init16), HBox_Weather(Button_Weather_Sun/Cloud/Overcast/Rain w/ Img_), HBox_Season(Button_Season_Summer/Autumn/Winter) ]. All interactive widgets IsVariable. Fonts FIRASANSCONDENSED_Font(title 14/arrow 20), ArchivoNarrow_Font(time 26).

**NEXT — BLOCKED on user running the Python once:**
1. **USER must run `Content/Python/build_weather_time_widget.py` in the Editor** (Output Log Python console or bottom Python cmd bar). MCP can't build UMG trees and there's NO exec-python MCP tool, so this is a manual handoff (same pattern as [[unreal_mesh_instancing_workflow]]). Script prints "[WeatherTime] BUILD DONE" or a traceback. Only after this do the widget's Button/Slider variables exist for MCP graph wiring.
2. Wire BP_WeatherTime_Widget graph via MCP: EventConstruct GetAllActorsOfClass(Ultra_Dynamic_Sky_C)+(Ultra_Dynamic_Weather_C) → cache new vars BP_UDS/BP_UDW; Slider_TimeOfDay OnValueChanged → set UDS TimeOfDay = Value*60 + update TextBlock_Time; TimeLeft/Right → step slider ±1 (clamp 6-22); Button_Weather_* OnClicked → `Class|UltraDynamicWeather|ChangeWeather(self=BP_UDW, "New Weather Type"=preset, "Time To Transition To New Weather (Seconds)"=3.0)` presets `/Game/UltraDynamicSky/Blueprints/Weather_Effects/Weather_Presets/`{Clear_Skies,Cloudy,Overcast,Rain}; Button_Season_* → `Class|UltraDynamicWeather|SetSeason(self=BP_UDW, Season=1/2/3)` (0=Spring,1=Summer,2=Autumn,3=Winter). Compile+save.
3. BP_MasterMenu_Widget: remove embedded BP_Time_Widget from canvas, add BP_WeatherTime_Widget (top-left per user screenshot), Collapsed default; in EventGraph add SetVisibility(Visible) to Button_Home/Button_Surroundings/Button_Amenities OnClicked, SetVisibility(Collapsed) to the others. Compile+save.
4. Final: Designer screenshot compare + ask user to PIE-test.

**Key MCP/DSL facts learned:**
- UDS node type_ids: `Class|UltraDynamicSky|SetTimeOfDay` (self + "Time of Day" pins, minutes 0-1440). `Class|UltraDynamicWeather|ChangeWeather` (self + "New Weather Type" UDS_Weather_Settings ref + "Time To Transition To New Weather (Seconds)" float). `Class|UltraDynamicWeather|SetSeason` (self + Season float).
- Blueprint asset ref format for MCP: `/Game/Path/Name.Name` for BlueprintTools graph/blueprint args; `/Game/Path/Name.Name_C` for actor Class refs. Widget graphs: `...BP_X.BP_X:EventGraph`, functions `...BP_X.BP_X:FuncName`.
- `write_graph_dsl` can't place MPC SetScalarParameterValue (self is not a MID) — create those nodes via `create_node` with `declaring_class=/Script/Engine.KismetMaterialLibrary`, then wire with connect_pins/set_pin_value. Also `write_graph_dsl` re-adds an auto Update_Time_Text/idle-timer chain; check with `read_graph_dsl` and delete stray nodes.
- Getters in BP_Time_Widget DSL: `Variables|Default|GetBPSunSky`, `GetBuildingsEmissiveCurve`, `GetEffectsEmissiveCurve`; funcs `CallFunction|UpdateTimeText`, `Class|BPExplorerGameInstance|GetExplorerMainPawn`, `Class|BPExplorerPawn|SetIdleTimer`, `Utilities|Casting|CastToBP_Explorer_GameInstance`, `Actor|GetAllActorswithTag`, `Rendering|SetActorHiddenInGame`.
- describe_toolset output for BlueprintTools too big — saved at tool-results, grep by byte offset.

See [[unreal_mesh_instancing_workflow]] (same MCP-can't-build-UMG gap → Python), [[unreal_archvizexplorer_structure]], [[feedback_respond_in_uzbek]].
