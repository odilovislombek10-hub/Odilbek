---
name: unreal-weather-panel-vr-pragulka
description: How BP_WeatherTime_Widget was made to work in Pragulka (ThirdPerson) and VR levels + touch input; exact hooks + files touched
metadata: 
  node_type: memory
  type: project
  originSessionId: b4d7b4d9-0113-48e5-98ec-f8b0fc508ab5
---

2026-07-03. Follow-up to [[unreal_uds_weather_panel_progress]]. Task: make `BP_WeatherTime_Widget` (the ПОГОДА|ВРЕМЯ СУТОК panel) usable in **Pragulka** and **VR** levels too — not just Glavniy_MirMIron. Widget was ONLY created by `BP_MasterMenu_Widget` (ArchViz flow), which only runs in Glavniy. The widget is self-contained: EventConstruct caches UDS/UDW via GetAllActorsOfClass + ApplyTime(16); so any level that (a) has Ultra_Dynamic_Sky/Weather actors and (b) creates+adds the widget will work.

**Level → GameMode → Pawn (verified via WorldSettings.DefaultGameMode + GameMode CDO Default__X_C DefaultPawnClass):**
- Pragulka → `BP_ThirdPersonGameMode` → pawn `BP_ThirdPersonCharacter1` (stock PlayerController). (Note: BP_ThirdPersonGameMode1 also exists + also uses BP_ThirdPersonCharacter1; WorldSettings uses the non-"1" one.)
- VR → `VRGameMode` → pawn `VRPawn` (stock PlayerController).
- Both levels already have `Ultra_Dynamic_Sky_C_0` + `Ultra_Dynamic_Weather_C_0`, and their UDW is CLEAN (cloud/fog Manual Override=false, season Mode=Manual Setting, ultraDynamicSky linked) — so weather buttons visibly change the sky in both (the Glavniy override-bug from [[unreal_uds_weather_realism_tuning]] does NOT affect these two).

**PRAGULKA fix (DONE + PIE-VERIFIED):** Edited `BP_ThirdPersonCharacter1:EventGraph` EventBeginPlay via write_graph_dsl (full-rewrite of the event, original AddMappingContext preserved, NO duplication). Prepended: GetPlayerController(0) → CreateWidget(BP_WeatherTime_Widget_C, PC) → AddToViewport → SetDesiredSizeInViewport(360,230) → SetPositionInViewport(40,40) → `Class|PlayerController|SetShowMouseCursor`(true) → `Input|SetInputModeGameAndUI`(PC). Compiled+saved. PIE (PlayMode_InViewPort, Pragulka): panel renders COMPACT top-left, time=16:00, weather+season button rows + slider all present. So mouse AND finger can operate it. **UX TRADEOFF (flagged to user, not yet changed):** bShowMouseCursor+GameAndUI means a persistent cursor; classic mouse-look may be reduced while cursor is free. Fine for touchscreen/kiosk (primary target) + WASD still walks. Alternative if user wants mouse-look preserved: gate the panel behind a toggle key (needs an InputAction + cursor/inputmode toggle).

**VR fix (DONE, needs in-headset laser test):** VR template already has full menu-laser infra — `VRPawn:ToggleMenu` spawns the `Menu` actor (`/Game/VRTemplate/Blueprints/Menu`) near the controller; Menu has a `widget` UWidgetComponent + Niagara laser (NS_MenuLaser) + WidgetInteractionRefLeft/Right that click WHATEVER UMG the WidgetComponent renders. Default widget was `WidgetMenu` (0 vars, empty EventGraph = blank VR-template placeholder). **Repointed the Menu's `widget` WidgetComponent template default** `WidgetClass`: WidgetMenu_C → `BP_WeatherTime_Widget_C`, and `DrawSize` 500×500 → 384×288 (panel-shaped). Component template reached at object path **`/Game/VRTemplate/Blueprints/Menu.Menu_C:widget_GEN_VARIABLE`** (the CDO `Default__Menu_C.widget` returns "None" — must use the `_GEN_VARIABLE` SCS archetype path). set_properties stuck, compiled+saved Menu. So in VR: press menu button → weather panel appears on the laser-clickable 3D widget → drives VR level's UDS/UDW. Isolated: Menu BP is only spawned by VRPawn, only used in VR level. Can't PIE-verify VR without a headset.

**TOUCH:** Config already touch-friendly — `Config/DefaultInput.ini`: `DefaultTouchInterface=None` (no virtual-joystick overlay to block the panel), bAlwaysShowTouchInterface=False. UMG buttons/slider natively receive touch on real touchscreen hardware; no extra work needed for the PANEL. `bUseMouseForTouch=False` (mouse does NOT simulate touch — only matters for editor testing; real touch hw unaffected). Did NOT flip it (could interfere with the GameAndUI cursor/mouse-look).

**KEY MCP FACTS learned this session:**
- GameMode CDO props readable at `/Game/.../BP_X.Default__BP_X_C` (NOT `.BP_X_C` class, NOT bare asset path).
- BP component template default editable at `/Game/.../BP.BP_C:<compName>_GEN_VARIABLE` (set_properties works there + compile + save persists).
- write_graph_dsl re-declaring an existing EventGraph event by name MERGES cleanly (verified: no dup AddMappingContext). Exec threads through `(bind v (execNode ...))` for CreateWidget.
- Node type_ids: `UserInterface|CreateWidget`(:Class :OwningPlayer→ReturnValue), `UserInterface|Viewport|AddtoViewport/SetDesiredSizeinViewport/SetPositioninViewport`(:self=widget :Size/:Position), `Class|PlayerController|SetShowMouseCursor`(:self :bShowMouseCursor), `Input|SetInputModeGameAndUI`(:PlayerController), `Math|Vector2D|MakeVector2D`.
- CaptureEditorImage returns base64 at `returnValue.data` (+`returnValue.mimeType`) — NOT returnValue.image.data. Screen-space UMG is visible ONLY in CaptureEditorImage (whole-app screenshot), NOT CaptureViewport (scene render). Decode via PowerShell [Convert]::FromBase64String. GetLogEntries needs category="" for all categories (default "LogsToolset" errors "not found").
- StartPIE may report "PIE ended before warmup completed" spuriously while IsPIERunning=true — just proceed to capture.

See [[unreal_uds_weather_panel_progress]], [[unreal_uds_weather_realism_tuning]], [[unreal_project_levels]], [[feedback_respond_in_uzbek]].
