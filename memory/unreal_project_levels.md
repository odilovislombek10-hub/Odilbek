---
name: unreal-project-levels
description: "Exact list of all .umap level/map files in the Odilbek project and which are the main working levels (Glavniy_MirMIron, Pragulka, VR)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4a418fe2-c49b-45d3-9e9e-325b8aca75b7
---

The user's three main working levels live under **`/Content/Level/Odilbek/`**:
- `Content/Level/Odilbek/Glavniy_MirMIron.umap` (~14 MB) — main/master level ("Glavniy" = main in Russian). Has a companion `Glavniy_MirMIron_BuiltData.uasset` that is **~275 MB** — by far the biggest BuiltData in the project, confirming this is the one "hero" level with fully baked lighting. Also has multiple autosave copies under `Saved/Autosaves/Game/Level/Odilbek/Glavniy_MirMIron_Auto0/1/2/8/9.umap`.
- `Content/Level/Odilbek/Pragulka.umap` (~10.7 MB) — the "Pragulka" (прогулка = walk/stroll) level, presumably a walkthrough/exterior-path level. **No `_BuiltData` file exists for this level** — lighting is not baked (fully dynamic/Lumen, or simply never built).
- `Content/Level/Odilbek/VR.umap` (~12.4 MB) — the VR-mode level. **Also has no `_BuiltData` file** — same as Pragulka, lighting is unbaked.
- Same folder also has `RenderMirMiron.umap` (~9.1 MB, likely a cinematic/render variant of the main level, also unbaked) and `Cesium.umap` (~24 KB, geospatial/Cesium georeference sublevel), plus non-map assets `MirMironNastroyka.uasset` ("nastroyka" = settings) and `6__49_2__2_page-0001.uasset`.
- `Content/Level/Odilbek.umap` (one level up, not inside the `Odilbek/` subfolder, ~13.6 MB, no BuiltData) — similar size to Glavniy_MirMIron, possibly an earlier/parallel version of the main level.

**Key fact: among the three named main levels, only Glavniy_MirMIron has baked/built lighting.** Pragulka and VR do not — worth flagging before doing any lighting-quality work on those two.

All four of `Glavniy_MirMIron`, `Pragulka`, `RenderMirMiron`, `VR` also appear cooked under `Saved/Cooked/Windows/Odilbek/Content/Level/Odilbek/` (i.e. the project has been packaged/cooked at least once).

**Other level/map files found across the whole project** (full `.umap` inventory, so nothing is missed):
- `Content/Level/atrof.umap`, `Content/Level/HDR.umap`, `Content/Level/Light_Amanat.umap`, `Content/Level/Skamka.umap`, `Content/Level/Terasa.umap` — misc small levels at Level/ root (atrof="surroundings", Skamka="bench", Terasa="terrace")
- `Content/Level/Izmir/Model.umap`
- `Content/Level/Poytaxt/Poytaxt.umap`, `Content/Level/Poytaxt/Light.umap`, `Content/Level/Poytaxt/Light2.umap` ("Poytaxt" = capital city)
- `Content/ArchVizExplorer/Maps/Demonstration_01.umap`, `Realistic_01.umap`, `VRMap.umap`, `VRRealistic.umap` — the ArchVizExplorer plugin's own demo maps (all but VRRealistic have `_BuiltData` companions)
- `Content/BlankDefault/Levels/Blank_Empty.umap`
- `Content/StarterContent/Maps/Advanced_Lighting.umap`, `Minimal_Default.umap`, `StarterMap.umap`
- `Content/ThirdPerson/Blueprints/Prog.umap`, `Content/ThirdPerson/Maps/ThirdPersonMap.umap`
- `Content/TwinEra/TwinEra2.umap`, `TwinEra2PR.umap`, `TwinEra2VR.umap`, `TwinEra3Pr.umap`, `TwinEra3VR.umap`
- `Content/VRTemplate/Maps/VRTemplateMap.umap`
- `Content/padez/Level/podez_Interact.umap`
- `Content/Main.umap` (top-level, outside Level/ folder)
- `Plugins/CesiumForUnreal/Content/Tests/Maps/ConeAndCylinder.umap`, `SingleCube.umap` (plugin test maps, not project content)

**Why:** user explicitly named Glavniy_MirMiron, Pragulka, and VR as "the main levels" and asked for a full audit; exact filenames/paths differ slightly in casing from how the user typed them (`Glavniy_MirMIron` with capital I, not `Glavniy_MirMiron`).
**How to apply:** when discussing "the main levels," resolve to these three exact paths under `Content/Level/Odilbek/`. See [[unreal-project-overview]] for the broader folder map and [[unreal-audit-python-script]] for getting exact per-actor/per-light/per-material parameter values out of whichever level is currently open in the Editor.
