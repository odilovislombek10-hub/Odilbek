---
name: unreal-perf-texture-audit
description: "Performance findings for the Odilbek project — duplicate textures, oversized 8K/4K textures, texture streaming pool config bug, and what actually makes Glavniy_MirMIron/Pragulka/VR heavy"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4a418fe2-c49b-45d3-9e9e-325b8aca75b7
---

Audit performed 2026-07-01 via filesystem/binary string analysis (no live Editor connection available). See [[unreal-project-overview]] and [[unreal-project-levels]] for base project facts, [[unreal-audit-python-script]] for the actor/light/material Details-panel export script.

## 1. Texture streaming pool / VRAM — found a real misconfiguration
`Config/DefaultEngine.ini` sets `r.Streaming.PoolSize=12288` (12GB) with a comment "Texture Streaming for 24GB VRAM", plus `r.Streaming.UseFixedPoolSize=1` and `r.Streaming.LimitPoolSizeToVRAM=1`. **But** `Config/DefaultDeviceProfiles.ini`, under `[Windows DeviceProfile]`, sets `CVars=r.Streaming.PoolSize=8192` (8GB) — device-profile CVars are applied after DefaultEngine.ini on the matching platform, so **the effective pool size on Windows is actually 8GB, not the intended 12GB**. Also `r.Nanite.Streaming.PoolSize=4096` (4GB) is separate/additional (Nanite virtualized geometry has its own streaming pool, on top of the regular texture pool).
**Why it matters:** with a real 24GB card, an 8GB texture pool is unnecessarily conservative and will cause more texture-streaming thrashing (blurry/pop-in textures) than needed, especially with the large duplicate/oversized texture footprint described below.
**FIXED 2026-07-01:** changed `CVars=r.Streaming.PoolSize=8192` to `=12288` on line 40 of `Config/DefaultDeviceProfiles.ini` (`[Windows DeviceProfile]` section) so it now matches the 12288 intended in `DefaultEngine.ini`. Requires an Editor/game restart to take effect (device profile CVars apply at startup).

## 2. Duplicate textures — confirmed, biggest offender is AutomotiveMaterials
A heuristic scan (filename + file-size match across the whole `/Content` tree, 4183 `.uasset` files) found **251 filenames duplicated somewhere in the project**, 120 of them following proper `T_/SM_/M_/MI_/MF_` naming (i.e. very likely genuine re-imports, not coincidental generic names like "1.uasset"/"NewMaterial.uasset" which make up the rest and are lower-confidence).
**Biggest confirmed pattern:** `Content/AutomotiveMaterials/` has **two parallel folder trees** — `Avto_Materials/` and `Materials/` — both containing their own `MI_CarPaint_*`, `MI_Glass_*`, textures like `T_Leather_06_N/R` (~97MB each, present twice — sizes differ by only ~10 bytes = same source), `T_MetalWear_Wear02/03_N` (present in `Avto_Materials`, `Materials`, AND a third copy nested inside `Content/ArchvisDefault/Model/avto_skm/AutomotiveMaterials/Materials/` — triple duplication), `T_OrangePeel_N`, `T_Flakes_D2/D3_*`. These are not byte-identical folders (different MI instance names/counts) but share the same underlying heavy textures duplicated 2-3x.
**Also found:** `Content/Megascans/Surfaces/Concrete_Wall_uepobaiew/` has the exact same 4K textures (`T_Concrete_Wall_uepobaiew_4K_D/N`) present both directly in that folder AND in a `NewFolder/` subfolder inside it — a pure accidental double-import of the same Megascans surface.
**Authoritative check:** filename+size matching is only a heuristic (`.uasset` files embed unique GUIDs so exact byte-identity never happens even for true duplicates). The `find_duplicates()`-equivalent logic now lives in `Content/Python/audit_textures.py` (`scan()` groups by original-import-filename + width/height via each texture's `AssetImportData` — the reliable signal for "same source file imported twice"). Run `audit_textures.report()` in the Editor for the definitive list before deleting/redirecting anything — nothing was or should be auto-deleted, since duplicates may be referenced by different levels/materials and need manual redirect-then-delete via the Reference Viewer.

## 3. Oversized (8K/4K) textures — confirmed to exist, biggest ones
Found by raw file size heuristic (BC-compressed 8K textures are typically 60-130MB+ on disk; true dimensions need the Editor):
- `Content/ArchvisDefault/Material/master_material/bruschatka/texture/uexlbdbn_8K_Normal.uasset` (131MB) and `uexlbdbn_8K_Albedo.uasset` (128MB)
- `Content/ArchvisDefault/Material/master_material/asphalt/textura/tlomaeady_8K_Albedo.uasset` (117MB)
- `Content/ArchvisDefault/Material/bruschatka/Texture/paving_granite_plates_RANDOM_normal.uasset` (230MB!) and `PAVING_02_12x10m_warm_Normal.uasset` (189MB) — no "8K" in the name but file size implies very high resolution, likely uncompressed or 8K+ normal maps
- `Content/BlankDefault/HDR/NewFolder/NewFolder/NewFolder/driving_school_8k.uasset` (73MB) — an 8K HDRI
- Many "4K" Megascans surface textures at 60-90MB each (Woodchip, Dark_Patterned_Tiles, Asphalt_Dried, Concrete_Floor, Concrete_Wall — each surface has D/N/ORDp variants at this size)
**Fix tool:** `Content/Python/audit_textures.py` → `apply_downsize(dry_run=True)` first to preview, then `apply_downsize(dry_run=False)` to cap oversized textures to `MaxTextureSize=2048` (non-destructive — reversible by resetting the property, does not touch original imported source art, so re-enabling higher res later is free).

## 4. What actually makes Glavniy_MirMIron / Pragulka / VR heavy — mesh geometry, not textures
Extracted direct `/Game/...` asset references from each level's binary `.umap` (grep-based string extraction) and cross-referenced against on-disk file sizes. **All three levels reference nearly the same heavy-asset set** (they clearly share the same base environment/street/landscape), and the top contributors are overwhelmingly **raw static mesh geometry, not textures**:
- `Content/Statik_tree/Big_tree/Ash-tree_05_21_2m_.uasset` — 81MB, and its own package references almost no textures (~20KB of materials) — the 81MB is almost entirely mesh geometry.
- `Content/Statik_tree/leaf.uasset` — 73MB, same story — a "leaf" mesh that is nearly all raw geometry.
- `Content/Level/Export/Shape389.uasset` (57MB), `BlockV360.uasset` (54MB), `door039.uasset` (46MB), `3dSolid7716.uasset` (43MB), `Cube_053.uasset` (26MB), `Plane126.uasset` (18MB), `rack_012.uasset` (16MB) — all in `Content/Level/Export/`, all with **zero material/texture references of their own** — these are raw Datasmith/CAD-imported meshes (generic "Shape/Cube/Plane/3dSolid/door" auto-names confirm this) that were never retopologized/decimated after import. A single door mesh at 46MB is 10-50x what a game-ready door should be.
- `Content/Speed_tree/Sample_Broadleaf_Forest2/Nanite/N_Sample_Broadleaf_Forest2.uasset` (59MB), `18m_Terak_01/02.uasset` (41-48MB each, more Statik_tree), `Cornus_sanguinea.uasset` (47MB)
- `Content/BlankDefault/Model/wicker.uasset`/`wicker1.uasset` (~18.7MB each) and `zont_1_011.uasset` ("umbrella", 27MB) — oversized furniture props
- `Content/GrandCapital/FBX/Models/Fountain/Pond.uasset` (22MB)
- Directly-referenced *textures* by the levels themselves are all small (UI icons, small MI parameter sets) — the big textures (8K/4K materials) are pulled in transitively through materials, not directly by the level, so they weren't visible in this direct-reference pass, but they still count toward the streaming pool budget once resolved.

**Conclusion for the user:** the dominant weight problem in Glavniy_MirMIron/Pragulka/VR is **unoptimized/undecimated static mesh geometry** (raw CAD-imported "Level/Export" props and full-detail tree/foliage meshes), not texture resolution — fixing textures (dedup + 8K→2K downsize) will help VRAM/streaming but the far bigger win is reducing polycount / adding proper LODs on the `Level/Export/*` CAD props and the `Statik_tree`/`Speed_tree` foliage meshes actually placed in these levels.

**Why:** user asked (2026-07-01) to find duplicate textures, downsize 8K→2K, check texture streaming pool/VRAM usage, and specifically find out what's making Glavniy_MirMiron/Pragulka/VR heavy.
**How to apply:** when discussing performance/optimization for this project, lead with the mesh-geometry finding (biggest lever), then texture dedup, then the streaming pool config bug, then 8K downsizing. Use `Content/Python/audit_textures.py` for the authoritative in-editor texture scan/fix, and repeat the `grep -aoE "/Game/[A-Za-z0-9_/.\-]+"` trick on any `.umap`/`.uasset` for quick reference extraction without opening the Editor.
