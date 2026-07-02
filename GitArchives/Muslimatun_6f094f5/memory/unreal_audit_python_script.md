---
name: unreal-audit-python-script
description: Where to find and how to run the Details-panel-level actor/mesh/light/material audit script for the Odilbek UE project
metadata: 
  node_type: memory
  type: reference
  originSessionId: 4a418fe2-c49b-45d3-9e9e-325b8aca75b7
---

For exact per-actor Details-panel parameter values (things the filesystem/binary `.uasset` files cannot reveal — light intensity/color/attenuation/IES, material scalar/vector/texture parameter values, transforms, mobility, collision profile), use the script at:

`Content/Python/audit_level_export.py`

**How to run** (PythonScriptPlugin is already enabled in this project):
1. Open the target level in the Unreal Editor (e.g. `Content/Level/Odilbek/Glavniy_MirMIron.umap`, `Pragulka.umap`, or `VR.umap` — see [[unreal-project-levels]]).
2. Window > Developer Tools > Output Log, switch the input dropdown to "Python", type: `import audit_level_export; audit_level_export.run()`
   — or via console command: `py "Content/Python/audit_level_export.py"`
3. Output JSON lands at `Saved/AuditExport/level_audit_<map>_<timestamp>.json`.

**What it captures per actor:** label, class, folder path, transform, tags, all `StaticMeshComponent`/`SkeletalMeshComponent` (mesh path, full material parameter dump: scalars/vectors/textures/static switches, mobility, cast_shadow, collision profile), all light components (`LightComponentBase` subclasses: intensity, light_color, temperature, attenuation_radius, source_radius/soft_radius, cone angles, IES texture, cast_shadows, mobility, intensity_units, etc.), plus a best-effort generic `exposed_properties` dump via Python reflection (reliable for native-class properties, may miss some Blueprint-only Class Default variables — see the script's docstring for the exact caveat).

**Why:** the user asked for a full audit of the project "down to the Details panel parameters," which is only possible with the Editor running (`.uasset`/`.umap` are binary and unreadable from disk alone). This script was written 2026-07-01 specifically to fill that gap; the `unreal-mcp` MCP server in this harness was still "connecting" at that time with no live tools exposed, so this script is the fallback until/unless that MCP connection produces real editor-introspection tools (see [[unreal-project-overview]]).
**How to apply:** whenever the user wants exact numeric values for lights/materials/transforms in a specific level, point them at (or offer to walk them through) running this script, then read the resulting JSON to answer their question — don't try to guess values from binary `.uasset` files.
