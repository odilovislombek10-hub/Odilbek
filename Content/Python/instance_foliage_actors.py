"""
Adds one HISM instance per original actor's transform for each mesh group listed
in MESH_TO_HISM_LABEL, then deletes the original individual StaticMeshActors once
every instance for that group was added successfully, then saves the level.

The HISM_<mesh> host actors (with a HierarchicalInstancedStaticMeshComponent
already pointed at the right static mesh) were created via unreal-mcp
(SceneTools.add_to_scene_from_class + ActorTools.add_component + ObjectTools.set_properties),
since raw Python has no reliable "add component to a level actor instance" call
in this engine version.

Run inside the Unreal Editor (Output Log > Python dropdown):
  import importlib, instance_foliage_actors
  importlib.reload(instance_foliage_actors)
  instance_foliage_actors.run(dry_run=True)     # preview only, changes nothing
  instance_foliage_actors.run(dry_run=False)    # adds instances, deletes originals, saves
"""
import unreal

# mesh path -> label of the pre-made HISM host actor
MESH_TO_HISM_LABEL = {
    # round 1: foliage (Statik_tree / Speed_tree)
    "/Game/Speed_tree/Silver_Birch_Small/Silver_Birch_Small_01.Silver_Birch_Small_01": "HISM_Silver_Birch_Small_01",
    "/Game/Statik_tree/Kustarnik/Pinus_Mugo_0403_.Pinus_Mugo_0403_": "HISM_Pinus_Mugo_0403_",
    "/Game/Speed_tree/Cornus_sanguinea/Cornus_sanguinea.Cornus_sanguinea": "HISM_Cornus_sanguinea",
    "/Game/Statik_tree/Kustarnik/crp_Спирея_голден_принцесс001.crp_Спирея_голден_принцесс001": "HISM_crp_Spireya_golden",
    "/Game/Statik_tree/Big_tree/18m_Terak_02.18m_Terak_02": "HISM_18m_Terak_02",
    "/Game/Statik_tree/Big_tree/Ash-tree_05_21_2m_.Ash-tree_05_21_2m_": "HISM_Ash_tree_05_21_2m_",
    "/Game/Speed_tree/Dub/dub_4m_03.dub_4m_03": "HISM_dub_4m_03",
    "/Game/Speed_tree/Silver_Birch_Small/Silver_Birch_Medium_6m_02.Silver_Birch_Medium_6m_02": "HISM_Silver_Birch_Medium_6m_02",
    "/Game/Statik_tree/Kustarnik/GrowFX001.GrowFX001": "HISM_GrowFX001",
    "/Game/Statik_tree/Kustarnik/Libertia_Grandiflora01_009.Libertia_Grandiflora01_009": "HISM_Libertia_Grandiflora01_009",
    "/Game/Statik_tree/Kustarnik/Libertia_Grandiflora01_010.Libertia_Grandiflora01_010": "HISM_Libertia_Grandiflora01_010",
    # round 2: repeated site furniture / CAD fixtures (non-foliage)
    "/Game/Level/Export/Plane007.Plane007": "HISM_Plane007",
    "/Game/Level/Export/Cylinder001.Cylinder001": "HISM_Cylinder001",
    "/Game/Level/Export/Object1834019033.Object1834019033": "HISM_Object1834019033",
    "/Game/BlankDefault/Model/Object1834013890.Object1834013890": "HISM_Object1834013890",
    "/Game/BlankDefault/Model/metal1.metal1": "HISM_metal1",
    "/Game/Mavrid/FBX_Exporter/Tuvak_gullar/Collection_Indoor_outdoor_plant_163_concrete_dirt_vase_pot_palm_cactus/POT_25092019_2.POT_25092019_2": "HISM_POT_25092019_2",
    "/Game/BlankDefault/Model/Object248.Object248": "HISM_Object248",
    "/Game/Mavrid/FBX_Exporter/Tuvak_gullar/Collection_Indoor_outdoor_plant_163_concrete_dirt_vase_pot_palm_cactus/POT_25092019_5.POT_25092019_5": "HISM_POT_25092019_5",
    "/Game/BlankDefault/Model/wicker1.wicker1": "HISM_wicker1",
    "/Game/Mavrid/FBX_Exporter/Tuvak_gullar/Collection_Indoor_outdoor_plant_163_concrete_dirt_vase_pot_palm_cactus/PLAM.PLAM": "HISM_PLAM",
    "/Game/BlankDefault/Model/Public_bench_RADIUM_00.Public_bench_RADIUM_00": "HISM_Public_bench_RADIUM_00",
    "/Game/BlankDefault/Model/manutti_cross_cloth002.manutti_cross_cloth002": "HISM_manutti_cross_cloth002",
    "/Game/BlankDefault/Model/metal.metal": "HISM_metal_generic",
    "/Game/BlankDefault/Model/Set_014.Set_014": "HISM_Set_014",
    "/Game/BlankDefault/Model/Velo_Stoyanka1.Velo_Stoyanka1": "HISM_Velo_Stoyanka1",
}


def find_hism_component(actor_subsystem, label):
    for actor in actor_subsystem.get_all_level_actors():
        if actor.get_actor_label() == label:
            comps = actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
            if comps:
                return comps[0]
    return None


def run(dry_run=True):
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_actors = actor_subsystem.get_all_level_actors()

    groups = {}  # mesh_path -> list of original StaticMeshActor
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
            if path in MESH_TO_HISM_LABEL:
                groups.setdefault(path, []).append(actor)
        except Exception as e:
            unreal.log_warning("[instance_foliage_actors] skipped actor: {}".format(e))

    for path, label in MESH_TO_HISM_LABEL.items():
        count = len(groups.get(path, []))
        unreal.log("[instance_foliage_actors] {} -> {} ({} original actors found)".format(path, label, count))

    if dry_run:
        unreal.log("[instance_foliage_actors] DRY RUN ONLY -- nothing changed. Call run(dry_run=False) to apply.")
        return

    total_converted = 0
    total_removed = 0
    for path, label in MESH_TO_HISM_LABEL.items():
        actors = groups.get(path, [])
        if not actors:
            continue
        hism = find_hism_component(actor_subsystem, label)
        if hism is None:
            unreal.log_error("[instance_foliage_actors] could not find HISM component for {}, skipping".format(label))
            continue

        added = 0
        for actor in actors:
            t = actor.get_actor_transform()
            idx = hism.add_instance(t, True)
            if idx is not None and idx >= 0:
                added += 1

        if added != len(actors):
            unreal.log_warning("[instance_foliage_actors] {}: only {}/{} instances added -- NOT deleting originals, check manually".format(
                label, added, len(actors)))
            continue

        for actor in actors:
            actor_subsystem.destroy_actor(actor)

        total_converted += added
        total_removed += len(actors)
        unreal.log("[instance_foliage_actors] OK: {} -> {} instances added, {} original actors removed".format(
            label, added, len(actors)))

    unreal.log("[instance_foliage_actors] TOTAL: {} instances added across all groups, {} original actors removed".format(
        total_converted, total_removed))

    try:
        les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        les.save_current_level()
        unreal.log("[instance_foliage_actors] level saved")
    except Exception as e:
        unreal.log_error("[instance_foliage_actors] could not auto-save level, save manually (Ctrl+S): {}".format(e))


if __name__ == "__main__":
    run(dry_run=True)
