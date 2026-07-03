# vr_material_audit.py
# Lists the actual TWO-SIDED and TRANSLUCENT materials used in the CURRENTLY OPEN level,
# with how many mesh-slots use each, so we can safely target the biggest performance
# offenders WITHOUT touching visual quality.
# Run in the Unreal Editor (NOT PIE) Python console:
#   exec(open(r"D:/mirmironnnn oxirgiiii/Unreal Engine/Unreal Engine/Odilbek/Content/Python/vr_material_audit.py").read())
# Writes  <Project>/Saved/VR_Material_Audit.txt  and logs  VRMAT:  lines.

import unreal
from collections import Counter

LOG = []
def out(s=""):
    LOG.append(str(s))
    unreal.log("VRMAT: " + str(s))

def safe(fn, d=None):
    try:
        return fn()
    except Exception:
        return d

try:
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = eas.get_all_level_actors()
except Exception:
    actors = unreal.EditorLevelLibrary.get_all_level_actors()

# material path -> stats
two_sided = Counter()          # usage count (mesh slots)
translucent = Counter()
masked = Counter()
mat_isinstance = {}            # path -> True if MaterialInstance (cheap to fix via parent)
seen = {}

def analyze(mat):
    if mat is None:
        return None
    p = safe(lambda: mat.get_path_name())
    if not p:
        return None
    if p in seen:
        return seen[p]
    base = safe(lambda: mat.get_base_material(), mat)
    ts = bool(safe(lambda: base.get_editor_property("two_sided"), False))
    bm = safe(lambda: base.get_editor_property("blend_mode"))
    tr = (bm == unreal.BlendMode.BLEND_TRANSLUCENT)
    mk = (bm == unreal.BlendMode.BLEND_MASKED)
    is_inst = isinstance(mat, unreal.MaterialInstance)
    seen[p] = (ts, tr, mk, is_inst)
    return seen[p]

for a in actors:
    for smc in (safe(lambda: a.get_components_by_class(unreal.StaticMeshComponent), []) or []):
        mats = safe(lambda: smc.get_materials(), []) or []
        for m in mats:
            r = analyze(m)
            if not r:
                continue
            p = m.get_path_name()
            ts, tr, mk, is_inst = r
            mat_isinstance[p] = is_inst
            if ts: two_sided[p] += 1
            if tr: translucent[p] += 1
            if mk: masked[p] += 1

def dump(title, counter, note):
    out("")
    out("==== %s (%d unique materials) ====" % (title, len(counter)))
    out(note)
    for p, c in counter.most_common():
        kind = "INST" if mat_isinstance.get(p) else "MAT "
        out("  x%-5d %s %s" % (c, kind, p))

out("================ VR MATERIAL AUDIT ================")
out("Level: %s" % safe(lambda: unreal.EditorLevelLibrary.get_editor_world().get_name(), "?"))
dump("TWO-SIDED materials", two_sided,
     "Two-sided doubles shading. SAFE to switch to one-sided ONLY if the mesh is solid/closed "
     "(walls, props, cars). NOT safe for single-plane geometry (leaves, curtains, decals, paper).")
dump("TRANSLUCENT materials", translucent,
     "Translucency = heavy overdraw in VR (glass, water). Consider: cheaper glass, or cull at distance. "
     "Do NOT make real glass opaque if it must show-through.")
dump("MASKED materials", masked,
     "Masked (alpha-test) = no early-Z, foliage/fences. Usually fine; listed for completeness.")

out("")
out("---- SUMMARY ----")
out("Unique two-sided: %d   (total slot uses: %d)" % (len(two_sided), sum(two_sided.values())))
out("Unique translucent: %d (total slot uses: %d)" % (len(translucent), sum(translucent.values())))
out("Unique masked: %d      (total slot uses: %d)" % (len(masked), sum(masked.values())))
out("Tip: 'INST' materials are MaterialInstances - two-sided is inherited from the parent Material; "
    "fixing the parent fixes all instances at once.")

proj = unreal.Paths.project_saved_dir()
path = unreal.Paths.combine([proj, "VR_Material_Audit.txt"])
try:
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(LOG))
    unreal.log("VRMAT: report written to %s" % path)
except Exception as e:
    unreal.log_error("VRMAT: write failed: %s" % e)
unreal.log("VRMAT: DONE")
