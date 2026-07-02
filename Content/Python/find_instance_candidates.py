"""
Read-only report: finds StaticMeshActor placements in the currently loaded level
that share the same mesh and appear MIN_GROUP_SIZE+ times, sorted by count.
These are candidates for the same "convert to HierarchicalInstancedStaticMeshComponent"
treatment already applied to the Statik_tree/Speed_tree foliage in this level
(see instance_foliage_actors.py). Makes no changes.

Run inside the Unreal Editor (Output Log > Python dropdown):
  import find_instance_candidates
  find_instance_candidates.run()
"""
import unreal

MIN_GROUP_SIZE = 5


def run():
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_actors = actor_subsystem.get_all_level_actors()

    groups = {}  # mesh_path -> count
    for actor in all_actors:
        try:
            if actor.get_class().get_name() != "StaticMeshActor":
                continue
            comps = actor.get_components_by_class(unreal.StaticMeshComponent)
            if not comps:
                continue
            mesh = comps[0].get_editor_property("static_mesh")
            if mesh is None:
                continue
            path = mesh.get_path_name()
            groups[path] = groups.get(path, 0) + 1
        except Exception:
            continue

    qualifying = {p: c for p, c in groups.items() if c >= MIN_GROUP_SIZE}
    ranked = sorted(qualifying.items(), key=lambda kv: -kv[1])

    unreal.log("[find_instance_candidates] {} distinct meshes placed as StaticMeshActor, {} groups placed >= {} times:".format(
        len(groups), len(qualifying), MIN_GROUP_SIZE))
    for path, count in ranked:
        unreal.log("  {} x{}".format(path, count))

    return ranked


if __name__ == "__main__":
    run()
