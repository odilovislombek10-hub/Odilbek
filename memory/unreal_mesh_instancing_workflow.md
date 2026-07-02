---
name: unreal-mesh-instancing-workflow
description: "How mesh-actor-to-HISM instancing actually works in this project: MCP can prepare HISM host actors but cannot populate instances; Content/Python/instance_foliage_actors.py + find_instance_candidates.py do the real work and must be run inside the Editor's native Python console"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7adce85f-9ecf-4986-9ff6-556f318ad0f6
---

## The scripts already exist and are now git-tracked
`Content/Python/find_instance_candidates.py` (read-only report of duplicate-mesh StaticMeshActor groups >=5) and `Content/Python/instance_foliage_actors.py` (the actual converter) were already written in a prior session but were **never committed to git** — the blanket `Content/` gitignore rule swallowed them even though the file's own comment says "code/config only tracked". Fixed 2026-07-02: `.gitignore` changed from `Content/` to `Content/*` + `!Content/Python/` (a plain `Content/` + `!Content/Python/**` negation does NOT work — git refuses to re-include children of an excluded parent directory unless the parent itself is un-excluded via the `Content/*` wildcard form). Also added `Content/Python/__pycache__/` to gitignore. All 5 existing scripts (`audit_level_export.py`, `audit_textures.py`, `audit_lightmap_uv.py`, `find_instance_candidates.py`, `instance_foliage_actors.py`) committed in `1dd302b`.
**How to apply:** any future reusable Python tooling written to `Content/Python/` should be committed to git in the same session it's created — don't assume it persists, and don't rediscover this gitignore gotcha from scratch.

## MCP cannot populate real HISM instances — confirmed by live test
Tried `ObjectTools.set_properties` on a `HierarchicalInstancedStaticMeshComponent`'s `PerInstanceSMData` property directly — fails with "the following properties could not be set: PerInstanceSMData". This is not exposed to the generic reflection-based property setter. No toolset (`ActorTools`, `ObjectTools`, `PrimitiveTools`, `SceneTools`, `AssetTools`, `StaticMeshTools`, `MaterialTools`, `MaterialInstanceTools`, `EditorAppToolset`) exposes a generic "call arbitrary UFunction" tool, so `HierarchicalInstancedStaticMeshComponent.AddInstance()` cannot be invoked from MCP either.
**What MCP CAN do:** create the HISM host actor + component + assign the right `StaticMesh`, via `SceneTools.add_to_scene_from_class` + `ActorTools.add_component` (component_type `/Script/Engine.HierarchicalInstancedStaticMeshComponent`) + `ObjectTools.set_properties({"StaticMesh": "<mesh Package.AssetName path>"})`. This is exactly what `instance_foliage_actors.py`'s docstring already documented as the intended prep step.
**What only native Editor Python can do:** the actual `hism_component.add_instance(transform, True)` call per original actor, then `actor_subsystem.destroy_actor(actor)` to remove the duplicates, then `level_editor_subsystem.save_current_level()`. This must be run by the user (or triggered some other way) via Output Log > Python dropdown inside the running Editor — there is no MCP bridge to raw `unreal` module Python execution.

## Session 2026-07-02: applied this to Pragulka and VR (Glavniy already had it)
Compared mesh-actor duplication across the 3 main levels via a live MCP scan (`find_actors` + `get_components` + `get_properties` on every StaticMeshActor's StaticMeshComponent, batched in one `execute_tool_script`):
- **Glavniy_MirMIron**: 327 total individual StaticMeshActors, worst duplicate group only 10x, `Object248` (chair, the mesh from [[unreal_hism_mirrored_instance_bug]]) = 0 individual placements — fully HISM'd already.
- **Pragulka**: 1293 individual StaticMeshActors, worst group `Plane007` x203, `Object248` x24 still un-instanced.
- **VR**: 1179 individual StaticMeshActors, `Plane007` x201, `Object248` x24, same pattern as Pragulka (these two levels share almost the same base environment set, per [[unreal_perf_texture_audit]]).

This confirms Glavniy really was optimized (mesh instancing) at some point and Pragulka/VR never were — validates it as a real, worthwhile difference, not user misperception.

Created 26 `HISM_<name>` host actors (component named `HISM`) in both Pragulka and VR via the MCP prep step above, reusing the exact `MESH_TO_HISM_LABEL` dict already hardcoded in `instance_foliage_actors.py` (trees/bushes: Silver_Birch_Small_01, Pinus_Mugo_0403_, Cornus_sanguinea, crp_Spireya_golden, 18m_Terak_02, Ash_tree_05_21_2m_, dub_4m_03, Silver_Birch_Medium_6m_02, GrowFX001, Libertia_Grandiflora01_009/010; site furniture/CAD: Plane007, Cylinder001, Object1834019033, Object1834013890, metal1, POT_25092019_2/5, Object248, wicker1, PLAM, Public_bench_RADIUM_00, manutti_cross_cloth002, metal_generic, Set_014, Velo_Stoyanka1). All 26 created with no errors in each level, both levels saved.

**Still pending (needs the user to run in-Editor):** for each of Pragulka and VR — load the level, Output Log > Python:
```
import importlib, instance_foliage_actors
importlib.reload(instance_foliage_actors)
instance_foliage_actors.run(dry_run=True)   # verify counts match expectations first
instance_foliage_actors.run(dry_run=False)  # adds instances, deletes originals, saves
```
**Why:** completes the "optimize Pragulka/VR meshes like Glavniy" request — MCP did everything scriptable, the final instance-population step needs native Python.
**How to apply:** if the user reports this was run and asks to verify, re-run the same duplicate-mesh-count scan (`execute_tool_script` pattern above) on Pragulka/VR and confirm counts dropped to match Glavniy's profile (few/no individual actors for these 26 mesh paths).

## Side finding: merge_actors is the only mesh-consolidation tool MCP does expose
`SceneTools.merge_actors` bakes multiple StaticMeshActors into one new merged StaticMesh asset + actor (real geometry merge, not GPU instancing). Considered as a fallback since true instancing isn't scriptable, but wasn't needed once the existing HISM scripts were found. Keep in mind for future levels/projects that don't already have `instance_foliage_actors.py`-style tooling.
