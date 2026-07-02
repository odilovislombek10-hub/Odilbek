"""
Lightmap-UV readiness audit for the Odilbek ArchViz project.

Why this exists: switching a level from fully-dynamic (Lumen, r.AllowStaticLighting=False)
back to baked static lighting only pays off if every Static-mobility mesh actually has a
valid lightmap UV channel. A mesh whose LightMapCoordinateIndex points at a UV channel
that doesn't exist (or that never had its lightmap UVs unwrapped) bakes to solid black
once lighting is built -- this script finds those meshes before you ever click Build.

Run inside the Unreal Editor (same pattern as audit_level_export.py):
  1. Open the level you want to check (Glavniy_MirMiron / Pragulka / VR).
  2. Output Log > Python dropdown > type: import audit_lightmap_uv; audit_lightmap_uv.run()

Output: Saved/AuditExport/lightmap_uv_audit_<map>_<timestamp>.json
Also prints a short PROBLEM summary directly to the log.
"""
import unreal
import json
import os
import datetime


def get_source_model_flags(mesh):
    """Best-effort read of per-LOD0 build settings (generate_lightmap_uvs, src/dst UV index)
    via the EditorStaticMeshLibrary scripting API (direct property reflection on
    SourceModels isn't exposed to Python in this engine version)."""
    try:
        build_settings = unreal.EditorStaticMeshLibrary.get_lod_build_settings(mesh, 0)
        return {
            "generate_lightmap_uvs": build_settings.get_editor_property("generate_lightmap_uvs"),
            "src_lightmap_index": build_settings.get_editor_property("src_lightmap_index"),
            "dst_lightmap_index": build_settings.get_editor_property("dst_lightmap_index"),
        }
    except Exception as e:
        return {"error_build_settings": str(e)}


def audit_mesh(mesh):
    path = mesh.get_path_name()
    result = {"mesh": path}
    try:
        result["light_map_coordinate_index"] = mesh.get_editor_property("light_map_coordinate_index")
    except Exception as e:
        result["light_map_coordinate_index"] = None
        result["error_coord"] = str(e)
    try:
        result["light_map_resolution"] = mesh.get_editor_property("light_map_resolution")
    except Exception:
        result["light_map_resolution"] = None
    try:
        result["num_uv_channels_lod0"] = unreal.EditorStaticMeshLibrary.get_num_uv_channels(mesh, 0)
    except Exception as e:
        result["num_uv_channels_lod0"] = None
        result["error_uv"] = str(e)
    try:
        result["num_lods"] = mesh.get_num_lods()
    except Exception:
        result["num_lods"] = None
    try:
        result["num_triangles_lod0"] = mesh.get_num_triangles(0)
    except Exception:
        result["num_triangles_lod0"] = None

    result.update(get_source_model_flags(mesh))

    # The actual failure condition: Lightmass reads LightMapCoordinateIndex as the UV
    # channel to bake into. If that index doesn't exist on the mesh, the mesh gets no
    # lightmap at all (renders black under baked/static lighting) unless
    # generate_lightmap_uvs is True (engine then auto-unwraps one at build time).
    coord = result.get("light_map_coordinate_index")
    num_uv = result.get("num_uv_channels_lod0")
    auto_gen = result.get("generate_lightmap_uvs")
    if coord is not None and num_uv is not None:
        missing_channel = coord >= num_uv
        result["will_be_black_when_baked"] = bool(missing_channel and not auto_gen)
        result["missing_uv_channel"] = missing_channel
    else:
        result["will_be_black_when_baked"] = None
        result["missing_uv_channel"] = None

    res = result.get("light_map_resolution")
    result["resolution_too_low"] = bool(res is not None and res <= 4)

    return result


def run():
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = actor_subsystem.get_all_level_actors()

    map_name = "unknown_map"
    if actors:
        try:
            map_name = actors[0].get_world().get_name()
        except Exception:
            pass

    seen = {}
    for actor in actors:
        try:
            for comp in actor.get_components_by_class(unreal.StaticMeshComponent):
                mesh = comp.get_editor_property("static_mesh")
                if mesh is None:
                    continue
                path = mesh.get_path_name()
                if path in seen:
                    seen[path]["placement_count"] += 1
                    continue
                data = audit_mesh(mesh)
                data["placement_count"] = 1
                seen[path] = data
        except Exception:
            continue

    meshes = list(seen.values())
    problems_black = [m for m in meshes if m.get("will_be_black_when_baked")]
    problems_low_res = [m for m in meshes if m.get("resolution_too_low")]

    export = {
        "map_name": map_name,
        "exported_at": datetime.datetime.now().isoformat(),
        "distinct_mesh_count": len(meshes),
        "meshes": meshes,
        "summary": {
            "will_be_black_when_baked_count": len(problems_black),
            "resolution_too_low_count": len(problems_low_res),
        },
    }

    saved_dir = os.path.join(unreal.Paths.project_saved_dir(), "AuditExport")
    os.makedirs(saved_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(saved_dir, "lightmap_uv_audit_{}_{}.json".format(map_name, ts))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2, ensure_ascii=False)

    unreal.log("[audit_lightmap_uv] {} distinct meshes checked -> {}".format(len(meshes), out_path))
    unreal.log("[audit_lightmap_uv] PROBLEM: {} meshes will bake BLACK (missing/invalid lightmap UV channel, no auto-unwrap)".format(len(problems_black)))
    for m in problems_black[:30]:
        unreal.log("  BLACK-RISK: {} (placed {}x, coord_index={}, num_uv_channels={})".format(
            m["mesh"], m["placement_count"], m.get("light_map_coordinate_index"), m.get("num_uv_channels_lod0")))
    unreal.log("[audit_lightmap_uv] PROBLEM: {} meshes have LightMapResolution<=4 (never tuned, will bake blurry/blocky)".format(len(problems_low_res)))

    return out_path


if __name__ == "__main__":
    run()
