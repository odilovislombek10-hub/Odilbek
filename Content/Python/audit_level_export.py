"""
Level audit exporter for the Odilbek ArchViz project.

Run inside the Unreal Editor (PythonScriptPlugin is already enabled in this project):
  1. Open the level you want to audit (Glavniy_MirMiron / Pragulka / VR / etc).
  2. Window > Developer Tools > Output Log, switch the input dropdown to "Python".
  3. Type:  import audit_level_export; audit_level_export.run()
     (Content/Python is auto-added to sys.path by the plugin.)

Alternative (console command, no need to switch dropdown):
     py "Content/Python/audit_level_export.py"

Output: a JSON file under Saved/AuditExport/level_audit_<map>_<timestamp>.json
containing every actor in the currently loaded level(s), their transforms,
static/skeletal mesh components (with full material parameter dumps: scalars,
vectors, textures, static switches), and light components (intensity, color,
temperature, attenuation, IES profile, cone angles, mobility, cast_shadows, etc).

Caveat: "exposed_properties" per actor is best-effort. Unreal's Python bindings
reliably expose properties of native (C++) classes; custom variables added purely
inside a Blueprint's Class Defaults are not always discoverable by name through
generic reflection from Python, so some Blueprint-only variables may be missing.
Everything coming from native component classes (mesh, material, light, transform,
collision, mobility) is complete.
"""
import unreal
import json
import os
import datetime


def stringify(v):
    if v is None or isinstance(v, (int, float, str, bool)):
        return v
    if isinstance(v, unreal.Vector):
        return {"x": v.x, "y": v.y, "z": v.z}
    if isinstance(v, unreal.Vector2D):
        return {"x": v.x, "y": v.y}
    if isinstance(v, unreal.Rotator):
        return {"pitch": v.pitch, "yaw": v.yaw, "roll": v.roll}
    if isinstance(v, unreal.LinearColor):
        return {"r": v.r, "g": v.g, "b": v.b, "a": v.a}
    if isinstance(v, unreal.Color):
        return {"r": v.r, "g": v.g, "b": v.b, "a": v.a}
    if isinstance(v, unreal.Object):
        try:
            return v.get_path_name()
        except Exception:
            return str(v)
    if isinstance(v, (list, tuple)):
        return [stringify(x) for x in v]
    try:
        list(v)
        return [stringify(x) for x in v]
    except TypeError:
        pass
    try:
        return str(v)
    except Exception:
        return repr(v)


def get_transform(obj):
    t = None
    try:
        t = obj.get_actor_transform()
    except Exception:
        try:
            t = obj.get_world_transform()
        except Exception:
            return None
    loc = t.translation
    rot = t.rotation.rotator()
    scale = t.scale3d
    return {
        "location": {"x": loc.x, "y": loc.y, "z": loc.z},
        "rotation": {"pitch": rot.pitch, "yaw": rot.yaw, "roll": rot.roll},
        "scale": {"x": scale.x, "y": scale.y, "z": scale.z},
    }


def get_material_params(mat):
    result = {"path": None, "scalars": {}, "vectors": {}, "textures": {}, "switches": {}}
    if mat is None:
        return result
    try:
        result["path"] = mat.get_path_name()
    except Exception:
        pass

    try:
        for name in unreal.MaterialEditingLibrary.get_scalar_parameter_names(mat):
            try:
                result["scalars"][str(name)] = unreal.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(mat, name)
            except Exception:
                try:
                    result["scalars"][str(name)] = unreal.MaterialEditingLibrary.get_scalar_parameter_default_value(mat, name)
                except Exception:
                    pass
    except Exception:
        pass

    try:
        for name in unreal.MaterialEditingLibrary.get_vector_parameter_names(mat):
            try:
                v = unreal.MaterialEditingLibrary.get_material_instance_vector_parameter_value(mat, name)
                result["vectors"][str(name)] = stringify(v)
            except Exception:
                pass
    except Exception:
        pass

    try:
        for name in unreal.MaterialEditingLibrary.get_texture_parameter_names(mat):
            try:
                tex = unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(mat, name)
                result["textures"][str(name)] = tex.get_path_name() if tex else None
            except Exception:
                pass
    except Exception:
        pass

    try:
        for name in unreal.MaterialEditingLibrary.get_static_switch_parameter_names(mat):
            try:
                val, _ = unreal.MaterialEditingLibrary.get_material_instance_static_switch_parameter_value(mat, name)
                result["switches"][str(name)] = val
            except Exception:
                pass
    except Exception:
        pass

    return result


def get_static_mesh_data(comp):
    data = {
        "component_name": comp.get_name(),
        "class": comp.get_class().get_name(),
        "transform": get_transform(comp),
        "materials": [],
    }
    for prop in ("mobility", "cast_shadow", "visible", "receives_decals", "cast_dynamic_shadow"):
        try:
            data[prop] = stringify(comp.get_editor_property(prop))
        except Exception:
            pass
    try:
        mesh = comp.get_editor_property("static_mesh")
        data["mesh"] = mesh.get_path_name() if mesh else None
    except Exception:
        data["mesh"] = None
    try:
        data["collision_profile"] = str(comp.get_collision_profile_name())
    except Exception:
        pass
    try:
        num_mats = comp.get_num_materials()
    except Exception:
        num_mats = 0
    for i in range(num_mats):
        try:
            data["materials"].append(get_material_params(comp.get_material(i)))
        except Exception:
            pass
    return data


def get_skeletal_mesh_data(comp):
    data = {
        "component_name": comp.get_name(),
        "class": comp.get_class().get_name(),
        "transform": get_transform(comp),
        "materials": [],
    }
    for prop_name in ("skeletal_mesh_asset", "skeletal_mesh"):
        try:
            sk = comp.get_editor_property(prop_name)
            data["mesh"] = sk.get_path_name() if sk else None
            break
        except Exception:
            continue
    try:
        for i in range(comp.get_num_materials()):
            data["materials"].append(get_material_params(comp.get_material(i)))
    except Exception:
        pass
    return data


LIGHT_PROPS = [
    "intensity", "light_color", "use_temperature", "temperature",
    "cast_shadows", "affects_world", "indirect_lighting_intensity",
    "volumetric_scattering_intensity", "intensity_units", "mobility",
    "source_radius", "source_soft_radius", "attenuation_radius",
    "inner_cone_angle", "outer_cone_angle", "use_ies_brightness",
    "ies_brightness_scale", "ies_texture", "source_width", "source_height",
    "barn_door_angle", "barn_door_length", "min_roughness",
]


def get_light_data(comp):
    data = {"component_name": comp.get_name(), "class": comp.get_class().get_name()}
    for prop in LIGHT_PROPS:
        try:
            data[prop] = stringify(comp.get_editor_property(prop))
        except Exception:
            pass
    data["transform"] = get_transform(comp)
    return data


def dump_exposed_properties(obj, max_props=200):
    result = {}
    try:
        names = dir(type(obj))
    except Exception:
        return result
    count = 0
    for name in names:
        if count >= max_props or name.startswith("_"):
            continue
        attr = getattr(type(obj), name, None)
        if not isinstance(attr, property):
            continue
        try:
            value = obj.get_editor_property(name)
        except Exception:
            continue
        result[name] = stringify(value)
        count += 1
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

    export = {
        "map_name": map_name,
        "exported_at": datetime.datetime.now().isoformat(),
        "actor_count": len(actors),
        "actors": [],
    }

    for actor in actors:
        try:
            actor_data = {
                "label": actor.get_actor_label(),
                "class": actor.get_class().get_name(),
                "folder": str(actor.get_folder_path()),
                "transform": get_transform(actor),
                "static_mesh_components": [get_static_mesh_data(c) for c in actor.get_components_by_class(unreal.StaticMeshComponent)],
                "skeletal_mesh_components": [get_skeletal_mesh_data(c) for c in actor.get_components_by_class(unreal.SkeletalMeshComponent)],
                "light_components": [get_light_data(c) for c in actor.get_components_by_class(unreal.LightComponentBase)],
                "exposed_properties": dump_exposed_properties(actor),
            }
            try:
                actor_data["tags"] = [str(t) for t in actor.get_editor_property("tags")]
            except Exception:
                actor_data["tags"] = []
            export["actors"].append(actor_data)
        except Exception as e:
            export["actors"].append({"label": actor.get_name() if actor else "?", "error": str(e)})

    saved_dir = os.path.join(unreal.Paths.project_saved_dir(), "AuditExport")
    os.makedirs(saved_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(saved_dir, "level_audit_{}_{}.json".format(map_name, ts))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2, ensure_ascii=False)

    unreal.log("[audit_level_export] {} actors exported -> {}".format(len(actors), out_path))
    return out_path


if __name__ == "__main__":
    run()
