# vr_perf_audit.py
# VR performance diagnostic for the CURRENTLY OPEN level.
# Run in the Unreal Editor (NOT in PIE) via the Python console:
#   exec(open(r"D:/mirmironnnn oxirgiiii/Unreal Engine/Unreal Engine/Odilbek/Content/Python/vr_perf_audit.py").read())
# Writes a full report to  <Project>/Saved/VR_Perf_Audit.txt  and prints a summary
# to the Output Log with the prefix  VRAUDIT:  (so it is greppable).
#
# Purpose: give a 100% accurate picture of what is heavy in the VR level so we can
# target the right optimizations (Nanite gaps, dynamic-shadow lights, translucency,
# instance counts, oversized textures, actor/draw-call load).

import unreal
from collections import Counter, defaultdict

LOG = []
def out(s=""):
    LOG.append(str(s))
    unreal.log("VRAUDIT: " + str(s))

def safe(fn, default=None):
    try:
        return fn()
    except Exception as e:
        return default

# ---- gather all actors in the open editor world ------------------------------
try:
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = eas.get_all_level_actors()
except Exception:
    actors = unreal.EditorLevelLibrary.get_all_level_actors()

level_name = safe(lambda: unreal.EditorLevelLibrary.get_editor_world().get_name(), "?")
out("================ VR PERF AUDIT ================")
out("Level: %s" % level_name)
out("Total actors: %d" % len(actors))

# ---- helpers -----------------------------------------------------------------
def mesh_tris(sm, lod=0):
    # try several API paths for triangle count
    for fn in (
        lambda: unreal.StaticMeshEditorSubsystem and unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).get_number_triangles(sm, lod),
        lambda: unreal.EditorStaticMeshLibrary.get_number_triangles(sm, lod),
    ):
        v = safe(fn)
        if v:
            return v
    return 0

def is_nanite(sm):
    v = safe(lambda: sm.get_editor_property("nanite_settings").enabled)
    if v is None:
        v = safe(lambda: sm.is_nanite_enabled(), False)
    return bool(v)

# ---- aggregates --------------------------------------------------------------
class_counts = Counter()
sm_usage = defaultdict(lambda: {"inst": 0, "tris": 0, "nanite": False, "name": ""})
total_static_tris = 0
total_nonnanite_tris = 0
light_counts = Counter()
light_dynamic_shadow = 0
light_movable = 0
skel_count = 0
skel_tris = 0
hism_instances = 0
ism_instances = 0
foliage_hosts = 0
niagara = 0
cascade = 0
decals = 0
ppv = 0
cesium = 0
translucent_meshes = 0
twosided_meshes = 0
mat_seen = {}

def classify_material(mat):
    # cache expensive shading traits per material path
    if mat is None:
        return
    p = safe(lambda: mat.get_path_name(), None)
    if not p or p in mat_seen:
        return mat_seen.get(p)
    tr = False; ts = False
    base = safe(lambda: mat.get_base_material(), mat)
    tr = bool(safe(lambda: base.get_editor_property("blend_mode") == unreal.BlendMode.BLEND_TRANSLUCENT, False))
    ts = bool(safe(lambda: base.get_editor_property("two_sided"), False))
    mat_seen[p] = (tr, ts)
    return mat_seen[p]

for a in actors:
    cn = safe(lambda: a.get_class().get_name(), "?")
    class_counts[cn] += 1
    if "Cesium" in cn:
        cesium += 1

    # static mesh components (covers StaticMeshActor + BP components)
    smcs = safe(lambda: a.get_components_by_class(unreal.StaticMeshComponent), []) or []
    for smc in smcs:
        cls = safe(lambda: smc.get_class().get_name(), "")
        sm = safe(lambda: smc.static_mesh) or safe(lambda: smc.get_editor_property("static_mesh"))
        # instance counts for HISM/ISM
        inst = safe(lambda: smc.get_instance_count(), None)
        if cls == "HierarchicalInstancedStaticMeshComponent":
            if inst:
                hism_instances += inst
            foliage_hosts += 1
        elif cls == "InstancedStaticMeshComponent":
            if inst:
                ism_instances += inst
        n_this = inst if inst else 1
        if sm:
            key = safe(lambda: sm.get_path_name(), str(sm))
            e = sm_usage[key]
            if not e["name"]:
                e["name"] = safe(lambda: sm.get_name(), key)
                e["tris"] = mesh_tris(sm, 0)
                e["nanite"] = is_nanite(sm)
            e["inst"] += n_this
            total_static_tris += e["tris"] * n_this
            if not e["nanite"]:
                total_nonnanite_tris += e["tris"] * n_this
        # material traits
        mats = safe(lambda: smc.get_materials(), []) or []
        for m in mats:
            r = classify_material(m)
            if r:
                if r[0]: translucent_meshes += 1
                if r[1]: twosided_meshes += 1

    # lights
    lcs = safe(lambda: a.get_components_by_class(unreal.LightComponent), []) or []
    for lc in lcs:
        lt = safe(lambda: lc.get_class().get_name(), "Light")
        light_counts[lt] += 1
        if safe(lambda: lc.get_editor_property("cast_shadows"), False) and \
           safe(lambda: lc.get_editor_property("mobility") != unreal.ComponentMobility.STATIC, True):
            light_dynamic_shadow += 1
        if safe(lambda: lc.get_editor_property("mobility") == unreal.ComponentMobility.MOVABLE, False):
            light_movable += 1

    # skeletal meshes
    for skc in (safe(lambda: a.get_components_by_class(unreal.SkeletalMeshComponent), []) or []):
        skel_count += 1

    if safe(lambda: a.get_components_by_class(unreal.NiagaraComponent), []):
        niagara += 1
    if safe(lambda: a.get_components_by_class(unreal.DecalComponent), []):
        decals += 1
    if "PostProcessVolume" in cn:
        ppv += 1

# ---- report ------------------------------------------------------------------
out("")
out("---- DRAW LOAD ----")
out("Unique static meshes: %d" % len(sm_usage))
out("Total static-mesh draws (incl. instances): %d" % sum(e["inst"] for e in sm_usage.values()))
out("Total static triangles rendered (sum inst*tris): {:,}".format(total_static_tris))
out("  of which NON-Nanite triangles: {:,}   <-- VSM / shadow cost".format(total_nonnanite_tris))
out("HISM instances: {:,}  (hosts: {})   ISM instances: {:,}".format(hism_instances, foliage_hosts, ism_instances))
out("Skeletal mesh components (characters etc.): %d" % skel_count)
out("Niagara actors: %d   Decal actors: %d   PostProcessVolumes: %d   Cesium actors: %d" % (niagara, decals, ppv, cesium))

out("")
out("---- LIGHTS ----")
for lt, c in light_counts.most_common():
    out("  %s: %d" % (lt, c))
out("Dynamic shadow-casting lights: %d   <-- each is expensive in VR (x2 eyes)" % light_dynamic_shadow)
out("Movable lights: %d" % light_movable)

out("")
out("---- MATERIALS (heavy traits) ----")
out("Mesh-material slots using TRANSLUCENT blend: %d   <-- very costly in VR" % translucent_meshes)
out("Mesh-material slots two-sided: %d" % twosided_meshes)

out("")
out("---- TOP 25 HEAVIEST STATIC MESHES (tris * instances) ----")
ranked = sorted(sm_usage.values(), key=lambda e: e["tris"] * e["inst"], reverse=True)
for e in ranked[:25]:
    out("  {:>12,}  x{:<6} {}  {}".format(e["tris"] * e["inst"], e["inst"],
        "NANITE" if e["nanite"] else "no-nan", e["name"]))

out("")
out("---- NON-NANITE MESHES WITH >20k TRIS (Nanite candidates) ----")
for e in ranked:
    if not e["nanite"] and e["tris"] > 20000:
        out("  {:>10,} tris  x{:<5} {}".format(e["tris"], e["inst"], e["name"]))

out("")
out("---- ACTOR CLASS COUNTS (top 30) ----")
for cn, c in class_counts.most_common(30):
    out("  %d  %s" % (c, cn))

# ---- write file --------------------------------------------------------------
proj = unreal.Paths.project_saved_dir()
path = unreal.Paths.combine([proj, "VR_Perf_Audit.txt"])
try:
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(LOG))
    unreal.log("VRAUDIT: report written to %s" % path)
except Exception as e:
    unreal.log_error("VRAUDIT: could not write file: %s" % e)

unreal.log("VRAUDIT: DONE")
