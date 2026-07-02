---
name: unreal-project-overview
description: "High-level structure/audit of the Odilbek Unreal Engine ArchViz project (engine version, plugins, top-level Content folder map, sizes)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4a418fe2-c49b-45d3-9e9e-325b8aca75b7
---

Project root: `D:\mirmironnnn oxirgiiii\Unreal Engine\Unreal Engine\Odilbek` (`.uproject` = `Odilbek.uproject`, `EngineAssociation: 5.8`).

This is an **ArchViz (architectural visualization)** project built on top of the **ArchVizExplorer** marketplace plugin/content pack (`/Content/ArchVizExplorer`), which supplies the core pawn/GameMode/widget framework. Custom project-specific scenes and levels live mainly under `/Content/Level`. There is almost no custom C++ — `/Source/Odilbek` only has the default `Odilbek.Build.cs`/`Odilbek.cpp`/`Odilbek.h` module boilerplate plus one stub `MyActor.h/.cpp`. The project is effectively 100% Blueprint + marketplace-content driven.

A video asset in `ArchVizExplorer/Movies/` is named (in Cyrillic) `ОАЗИС_В_ГОРОДЕ_Жилой_комплекс_NRG_VOHA` — "Oasis in the City, Residential Complex, NRG VOHA" — suggesting the real-world project this ArchViz build represents is a residential complex called "Oasis in the City" (developer/brand tag "NRG VOHA").

Project root also has an ~862 MB `cesium-request-cache.sqlite` (Cesium plugin's local tile cache — safe to ignore/exclude from backups, it's regenerable).

Key enabled plugins (from `Odilbek.uproject`): DatasmithImporter, InterchangeEditor, DatasmithCADImporter, DatasmithC4DImporter, AxFImporter, DataPrepEditor, VariantManager, SunPosition, HDRIBackdrop, **PythonScriptPlugin** (enabled — used for the audit export script, see [[unreal-audit-python-script]]), ModelingToolsEditorMode, MovieRenderPipeline(+MaskRenderPass), RuntimeDataTable (marketplace plugin under `/Plugins/RuntimeDataTable`), CesiumForUnreal (marketplace plugin under `/Plugins/CesiumForUnreal`, geospatial 3D tiles), OpenXR (VR), Terminal, EditorToolset, **ModelContextProtocol** (Epic's own MCP plugin — this is almost certainly what the harness's `unreal-mcp` server connects to; it only comes alive while the Unreal Editor is actually running, which is why no live editor-introspection tools were available during this audit — if the Editor is open next time and `unreal-mcp` exposes real tools, prefer those over the Python script for live introspection).

Top-level `/Content` folders sorted by disk size (from `du -sh`):
- 3.7G `ArchvisDefault/` — generic ArchViz template default content (vendor pack, not audited file-by-file)
- 2.8G `PosedHumansPack1/` — posed human character marketplace pack (vendor)
- 2.5G `Level/` — **the actual custom project content lives here**, see [[unreal-project-levels]]
- 1.6G `Megascans/` — Quixel Megascans surfaces/props (vendor library)
- 1.5G `AutomotiveMaterials/` — car paint/material marketplace pack (vendor)
- 1.2G `ArchVizExplorer/` — the core plugin/content framework, see [[unreal-archvizexplorer-structure]]
- 1.1G `TwinEra/` (609 files, largest architectural scene folder besides ArchvisDefault) — a large furnished-interior scene: raw FBX imports (`Decor`/`FBX`/`FBX3`/`FBX4`, 230 files total) + extensive `material/` subfolders by category (Wood 59, Plastic 64, Soft 47, Tile 44, Dom1 62, Tree 30, Kniga 20, Metalic 6, Picturest 10, Glass 5, Floor/Light/Wall/Master a few each) + its own maps `TwinEra2/2PR/2VR/3Pr/3VR.umap` — looks like a VR/non-VR + Pr(photoreal?)/VR pair per apartment unit (2 and 3). Partially follows UE naming (74 `M_`, 23 `MI_`, 8 `T_`) but mostly uses descriptive names (White_, Master_, Color_, door_, Bed_, Usman_).
- 1.1G `Speed_tree/`, 847M `Statik_tree/` — SpeedTree foliage vendor packs
- 603M `StarterContent/` — stock UE starter content
- 487M `Characters/` — UE5 Mannequins + MannequinsXR (VR hand/body rigs)
- 446M `Parallax/` — Hotel_PARALLAX (EXR HDRI) + wP_Free_Scene (vendor demo scene)
- 315M `PosedHumansShoppingPack1/` — another posed-human vendor pack
- 311M `BlankDefault/` — blank template default level/content
- 226M `Mavrid/` (101 files) — a decor/plant-props kit (`FBX_Exporter/Tuvak_gullar/` = "pots/flowers", `RECLAIMED_ARTIZAN_IRON_XL`) plus generic materials/textures (`Default_M`, `material/`, `Texture/Decal`+`dpk`) — no dedicated map, likely referenced by other scenes rather than a scene itself
- 145M `Blueprint/` — misc custom blueprints: `Blueprint/Car/Car2..Car4` (vehicle BPs, backed by `AutomotiveMaterials/`), `Blueprint/Human` (character animation BPs, backed by `Characters/`)
- 91M `padez/` (208 files, "podъезд" = building entrance/stairwell) — interactive scene: `FBX/` (170 files, bulk of content), `Level/podez_Interact.umap`, `Materials/Basic/` (26 files: `DOOR_`×9, `Basic_`×9, `Chrome_`×6, `Emessive_`×3), `Texturas/` (10)
- 88M `Fab/` — Fab (Quixel/Megascans marketplace) surfaces
- 29M `FPWeapon/` — first-person weapon template assets (Materials/MaterialLayers, Mesh, Textures)
- 27M `AXYZAssets/` — AXYZ human character assets (Animations/Materials/Textures)
- 22M `GrandCapital/` (3 files) — just a fountain/pond prop kit (`FBX/Models/Fountain/`: Pond mesh 22.2 MB + water material/instance), not a full scene
- 18M `PLOSHATKA/` (15 files, "ploshadka"=playground/square) — outdoor playground equipment FBX imports (swings, climbing wall, rocking toys, playground set) with raw/non-UE-convention names; not an interior scene
- 40K `Luxury/` (3 files) — material-only stub (`ColorMaster`, `M_color_17`, `M_color_4`), no meshes/maps
- 11M `Minimalism_1/` (7 files) — materials-only style kit (`Basic_Chrome_Metall`, `White_dirt3`, + 5 textures), no meshes/maps present
- 48K `Neokassik_3/` / 16K `Neoklasik_1/` — single stub material each (`Master_soft`, `NewMaterial57`), placeholders only
- 7.2M `VRTemplate/` — UE VR template (Blueprints, Input/Actions, Maps/VRTemplateMap, Materials/Functions, VFX, Haptics, Audio)
- 3.8M `ThirdPerson/` — UE ThirdPerson template (has `Blueprints/Prog.umap` + `Maps/ThirdPersonMap.umap`)
- Small (<1M each): `NVSplineTools`, `VRSpectator` (Input/Actions), `floorPlan` (a single scanned floor-plan photo, reference only), `Material`, `__ExternalActors__`/`__ExternalObjects__` (World Partition/OFPA actor data, only used by `ThirdPerson/Maps/ThirdPersonMap`), `M_Material`, `LevelPrototyping`, `MSPresets`, `Python` (the audit script), `Functions`, `CesiumSettings`
- Empty: `Developers/`, `Collections/`

**Why:** the user asked for a full audit of the whole Content tree (every actor/mesh/material/light down to Details-panel parameters) on 2026-07-01, to be kept in memory as a durable reference since re-deriving it requires extensive exploration of a very large binary-asset project.
**How to apply:** when the user references a folder by name (e.g. "Mavrid", "TwinEra", "padez"), use this map to know what it is before digging further. For exact per-actor Details-panel numeric values (light intensity, material scalar/vector params), the filesystem alone is insufficient (`.uasset`/`.umap` are binary) — use [[unreal-audit-python-script]] instead.
