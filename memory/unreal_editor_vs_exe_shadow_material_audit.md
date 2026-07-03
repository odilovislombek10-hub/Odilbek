---
name: unreal_editor_vs_exe_shadow_material_audit
description: "MEGA audit of editor-vs-EXE difference (Glavni/Pragulka/VR washed + materials missing): 3 log-confirmed root causes = VSM non-Nanite overflow (shadow), MeshModelingToolsetExp textures NOT cooked (materials), unlocked auto-exposure + LocalExposure 0.8 (washed)"
metadata:
  node_type: memory
  type: project
  originSessionId: 142e52be-f47a-4b55-9015-5fee424a5691
---

2026-07-03: User narrowed the packaged-EXE-looks-Medium/washed problem to the 3 open-sky levels (Glavniy_MirMIron/Pragulka/VR) — interiors look fine in EXE. Then said it's a SHADOW issue. Ran a MEGA audit (config diff + packaged runtime log `E:\MIR MIRON PACKAGE\Windows\Odilbek\Saved\Logs\Odilbek.log` + level binary + UE community research). Full report: `Reports/2026-07-03_editor_vs_exe_shadow_material_MEGA_audit.md` (git-tracked, Uzbek).

**3 log-confirmed root causes:**
- **A. VSM shadow overflow (the user's "shadow" hunch — CONFIRMED):** packaged log lines 11250 & 11408 = `[VSM] Non-Nanite Marking Job Queue overflow. ...many non-nanite meshes cover a large area of the shadow map.` Cause = `Level/Export` CAD props + full-detail trees are NOT Nanite; they overflow VSM → non-Nanite geometry drops out of shadow casting → flat/washed. We had only SILENCED it earlier (`r.Shadow.Virtual.AllowScreenOverflowMessages=0`), never fixed it. Only these 3 levels (open sky + huge CAD area); interiors are small/enclosed. Community fix (Epic forums 2172645/2606445/2718622 + VSM docs): convert heavy meshes to Nanite, OR switch shadow method to conventional Shadow Maps for that geometry.
- **B. Materials not showing (\"ayrim materiallar tushmagani\") — CONCRETE CAUSE FOUND:** packaged log lines 1215–1235+ repeat `LogPackageName: Error: GetLocalBaseFilenameWithPath: Failed converting package name \"/MeshModelingToolsetExp/Textures/DefaultEmissive\"` (+`DefaultOpacity`). `MeshModelingToolsetExp` = EDITOR-ONLY plugin (Modeling Mode); its textures are NOT cooked into the package. Some project material references them → breaks in EXE. Matches community #1 (editor/engine content used in material/PPV not cooked → copy into project). NEXT: MCP get_referencers on those two texture paths → find the material → repoint Emissive/Opacity to project assets.
- **C. Washed/flat:** auto-exposure NOT locked (`AutoExposure.Method=1`, EyeAdaptation LUT toggling, log 426/1296/11270) + `r.DefaultFeature.LocalExposure.HighlightContrastScale=0.8` & `ShadowContrastScale=0.8` (<1.0 flattens contrast). Fix = lock exposure in PPV/UDS + LocalExposure 0.8→1.0. See [[unreal_packaged_vs_editor_exposure]].

**FIXED this session:** `Config/DefaultDeviceProfiles.ini` (applies ONLY in packaged, so it's the editor↔EXE divergence) — `r.Nanite.MaxPixelsPerEdge` 2→1.0 and `r.Nanite.AllowTessellation` True→False, to match editor's DefaultEngine.ini (EXE Nanite geometry/shadow was coarser). **Needs RE-PACKAGE** — packaged build has NO loose config (only `Engine/Config/StagedBuild_Odilbek.ini`); DefaultDeviceProfiles is baked into the pak, cannot hot-edit the existing EXE.

**Key mechanism reminder:** editor uses `WindowsEditor` device profile (no CVars) → editor = DefaultEngine.ini values. Packaged uses `[Windows DeviceProfile]` (big CVar list) which overrides at startup → editor↔EXE differences are EXACTLY the cvars where the device profile differs from DefaultEngine.ini. Core VSM shadow cvars (Enable=1, CSM.MaxCascades=4, MaxResolution=2048, sg.ShadowQuality=3, RayTracing.Shadows=False) are IDENTICAL in both — so shadow SETTINGS aren't the divergence; geometry fineness + VSM overflow + cook failures are.

Community fixes researched (Epic forums): editor-content-not-cooked (359316), static-lights+Lumen→movable (2726142), VSM overflow→Nanite/shadow-method (2172645). Python broken in this env's Bash (Windows store stub) — use Grep tool / PowerShell, not `python -c`.
