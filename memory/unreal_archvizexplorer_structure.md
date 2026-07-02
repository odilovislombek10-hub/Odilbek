---
name: unreal-archvizexplorer-structure
description: Full breakdown of /Content/ArchVizExplorer — the core blueprint/widget framework the whole Odilbek project is built on
metadata: 
  node_type: memory
  type: project
  originSessionId: 4a418fe2-c49b-45d3-9e9e-325b8aca75b7
---

`/Content/ArchVizExplorer` (1.2G) is the marketplace ArchVizExplorer plugin/content pack and is the **core interaction framework** for the whole project (per user: "eng katta bluprint widgetlar shu yerda" — the biggest blueprints/widgets are here).

**Blueprints/** (root level, gameplay framework):
`BPI_CSV` (interface), `BP_360Sphere`, `BP_AVE_SunSky`, `BP_Environment_Mqtt`, `BP_Explorer_GameInstance`, `BP_Explorer_GameMode`, `BP_Explorer_Pawn`, `BP_Explorer_PC` (PlayerController), `BP_Explorer_SaveGame`, `BP_POI` (point of interest), `BP_RoadTool`, `BP_Route`.
- `Blueprints/Curves/`: Buildings_Emissive_Curve, Effects_Emissive_Curve, Pan_Intensity_Curve, Zoom_Intensity_Curve, Zoom_InterpSpeed_Curve
- `Blueprints/DataTables/`: `11_-_11_csv`, `11_-_11_csv1`
- `Blueprints/Enums/`: Availability_Enum, MediaType_Enum, PawnType_Enum, POI_Type_Enum
- `Blueprints/Structs/`: DirectionStruct, Media_Struct, POI_Filter_Struct, POI_Info_Struct

**Blueprints/Widgets/** (18 UMG widget blueprints — the "biggest widgets" the user referred to; no `WBP_` prefix is used anywhere in this project, all widgets use `BP_*_Widget` naming):
BP_360Menu_Widget, BP_3D_Center_Widget, BP_3D_Widget, BP_Amenities_Widget, BP_Compass_Widget, BP_EntryList_Widget, BP_Entry_Widget, BP_Gallery_Preview_Widget, BP_Gallery_Widget, **BP_Info_Widget (693.6 KB)**, **BP_MasterMenu_Widget (826.7 KB — main HUD/menu shell)**, BP_Notification_Widget, BP_Slider_Widget, BP_Surroundings_Widget, BP_Time_Widget, BP_ToggleButton_01, **BP_UnitSearch_Widget (1.01 MB — largest widget, apartment/unit search UI)**, BP_Vagon_Widget1.
This is a real-estate/apartment "unit search" style ArchViz explorer UI: unit search, amenities, gallery, 360 view, compass/time-of-day, master menu, entry list. The core gameplay blueprint `BP_Explorer_Pawn` (player pawn) is the single largest blueprint in the project at 1.19 MB; `BP_POI` (Point of Interest) is 820 KB, `BP_Explorer_PC` (PlayerController) is 641 KB.

**Environment/Foliage/**: MI_Bush_01_Branch/Leaves_Inst, MI_PP_Foliage_Inst, MI_Tree_Beech_01_Leaves/Trunk_Inst, MI_Tree_Pine_01_Leaves/Trunk_Inst, M_PP_Foliage_Master_Mat, SM_Bush_01, SM_Tree_Beech_01, SM_Tree_Pine_01, plus 6 special "pivot painter" textures (`T_*_PivotPos_a_ParentIndexInt_UV_2`, `T_*_XVector_a_XExtentDividedby2048...`) used for wind-animated foliage shaders.

**Environment/Lighting/**: BP_Lamp, BP_Pole, BP_Skyglow (blueprints), M_Luminaire_Main_01_Mat(+_Inst), PoleData/RoadData (data assets), SM_Bracket_01, SM_LightBulb_01, SM_LightPole_10M_01, SM_Luminaire_01 (meshes), T_Luminaire_01_AO/N (textures) — this is the street-lighting/lamppost kit used along roads.

**Fonts/** (26 files): `ArchivoNarrow_Font` + 8 style variants (Bold/BoldItalic/Italic/Medium/MediumItalic/Regular/SemiBold/SemiBoldItalic), `FIRASANSCONDENSED_Font` + 14 style variants, and a `RichText_DataTable`.

**Movies/** (5 files): `MediaPlayer_01`, `MediaTexture_01`, `SampleVideo`, `StreamMediaSource_01`, and a Cyrillic-named video `ОАЗИС_В_ГОРОДЕ_Жилой_комплекс_NRG_VOHA` ("Oasis in the City — Residential Complex NRG VOHA" — see [[unreal-project-overview]] for what this implies about the real-world project name).

**Maps/**: `Demonstration_01` (~6.5 MB), `Realistic_01` (~310 MB, largest umap in the whole project), `VRMap` (~4.7 MB), `VRRealistic` (~246 MB) — plugin's own demo/sample maps, separate from the project's real levels (see [[unreal-project-levels]]). BuiltData exists for all but VRRealistic.

**Materials/** (31 files at root + subfolders `Effects`(7), `Glass`(3), `MF`(3), `MPC`(2 — Material Parameter Collections), `Maquette`(6)):
Root materials/instances: MF_Metal_Galvanized_01_Mat, MI_Concrete_01/02_Inst, MI_Grass_Inst, MI_Landscape(_Far)_Inst, MI_Oak_Ovrly_03_Inst, MI_Road_Inst, MI_Road_Lines_Inst, MI_SkySphere_Gradient_Inst, MI_TilesWavy_02_Inst, MI_Tiles_Inst, MI_Wall_01/02_Inst, MI_Widget_3D_Inst, M_Base_01, M_EmissiveText, M_Flooring, M_Framing, M_Glass_01(+_Inst), M_Grass, M_Landscape, M_Metal_Galvanized_Mat(+_Inst), M_Metal_Reflective_01, M_Roofs, m_SimpleVolumetricCloud_Inst, M_SkySphere, M_Tiles, M_Wall, M_Widget_3D, M_Widget_RadGradientBG_Mat.

**Meshes/**: root has SM_Buildings_01, SM_Buildings_Mqtt_01, SM_Building_01_Sidewalk, SM_Landscape_Far_01, SM_POI_Custom_01, SM_Roads_01, SM_Roads_Mqtt_01, SM_SkySphere, SM_SplineMesh_01.
- `Meshes/Building_01/`: a modular building kit — SM_Building_01_0..8_Floor, SM_Building_01_1..5_Gallery, SM_Building_01_Facade_01, SM_Building_01_Filling, SM_Building_01_Gym_01, SM_Building_01_MainEntrance_01, SM_Building_01_Sidewalk_Mqtt, SM_Guardrail_01, SM_Pool_01.
- `Meshes/SlidingDoor_01/`: SM_SlidingDoor_Base_01/02_Low, SM_SlidingDoor_Frame_01/02_Low.

**Textures/**: root has ~28 files (T_Asphalt_02_AO/BC/N/R, T_Building_Windows_01_BC, T_Concrete_Clean_01_AO/BC/N/R, T_Landscape_01_N, T_Lights_Traffic_M, T_Logo_01, T_Macros_Metal_01_M, T_MacroVariation, T_Metal_Galvanized_01_AO/BC/N/R, T_MuseumBoard_BC/N/R, T_Noise_01_N, T_Noise_GaussianSpots_01_M, T_Oak_Ovrly_03_AO/D/N/R, T_Ovrly_01_M, T_Tiles_Wavy_Concrete_01_AO/BC/N/R, HighresScreenshot00000).
- `Textures/HDR/` (2), `Textures/IES_LightProfiles/` (4 — real-world IES light profiles used by the Lighting kit above), `Textures/UI/` (82 — widget/UI textures/icons).

**Why:** user specifically flagged `/Game/ArchVizExplorer` as containing the biggest/most important blueprints and widgets, and wanted every mesh/light/material named down to Details-panel parameters.
**How to apply:** when working on UI/widget features, look in `Blueprints/Widgets/`. When working on gameplay/interaction logic, look at the root `Blueprints/` framework classes (GameMode/Pawn/PC/SaveGame/POI/Route). For exact numeric parameter values on any of these materials/lights, use [[unreal-audit-python-script]] since the values themselves aren't visible from the filesystem.
