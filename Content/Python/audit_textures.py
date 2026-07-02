"""
Texture audit/fix tool for the Odilbek project.

Run inside the Unreal Editor (Output Log > Python, or `py "Content/Python/audit_textures.py"`):

    import audit_textures
    audit_textures.report()                                  # read-only scan -> JSON report
    audit_textures.apply_downsize(dry_run=True)               # preview what would be capped to 2048
    audit_textures.apply_downsize(dry_run=False)               # actually cap oversized textures to 2048

What it does:
  - Scans every Texture2D asset in the project via the Asset Registry.
  - Flags textures whose longest side > `size_threshold` (default 2048, i.e. catches 4K/8K) as
    oversized, sorted by estimated GPU memory footprint (uncompressed estimate, biggest first).
  - Groups likely DUPLICATE textures by (original import filename, width, height) using each
    texture's AssetImportData — this is a heuristic (source-file-name + resolution match), not a
    byte-for-byte hash, so always eyeball a group before deleting anything. Nothing is ever
    deleted by this script; duplicate detection is report-only.
  - `apply_downsize` sets `MaxTextureSize` (non-destructive, reversible by setting back to 0) on
    oversized textures and saves them, capping the built/streamed resolution without touching the
    original imported source art. Defaults to dry_run=True so the first call never modifies
    anything — you must explicitly pass dry_run=False to commit changes.

Output JSON report: Saved/AuditExport/texture_audit_<timestamp>.json
"""
import unreal
import json
import os
import datetime
import collections


def _get_all_texture_asset_datas():
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    try:
        class_path = unreal.TopLevelAssetPath("/Script/Engine", "Texture2D")
        return registry.get_assets_by_class(class_path, search_sub_classes=True)
    except Exception:
        return registry.get_assets_by_class("Texture2D", True)


def _import_filename(tex):
    try:
        data = tex.get_editor_property("asset_import_data")
        if data is None:
            return None
        names = data.extract_filenames()
        if names:
            return os.path.basename(str(names[0]))
    except Exception:
        pass
    return None


def _estimate_bytes(width, height, has_mips=True):
    # Rough uncompressed-equivalent estimate (BC-compressed textures are ~1/4 to 1/8 of this,
    # but this is a stable, comparable relative-size metric across all textures).
    base = width * height * 4
    return int(base * 1.33) if has_mips else base


def scan(size_threshold=2048):
    asset_datas = _get_all_texture_asset_datas()
    all_textures = []
    oversized = []
    dupe_key_map = collections.defaultdict(list)

    for ad in asset_datas:
        try:
            tex = ad.get_asset()
            if tex is None:
                continue
            w = tex.blueprint_get_size_x()
            h = tex.blueprint_get_size_y()
            path = str(ad.package_name)
            import_name = _import_filename(tex)
            entry = {
                "path": path,
                "width": w,
                "height": h,
                "import_filename": import_name,
                "lod_group": str(tex.get_editor_property("lod_group")) if hasattr(tex, "get_editor_property") else None,
                "est_bytes": _estimate_bytes(w, h),
            }
            all_textures.append(entry)
            if max(w, h) > size_threshold:
                oversized.append(entry)
            key = (import_name or os.path.basename(path), w, h)
            dupe_key_map[key].append(path)
        except Exception as e:
            all_textures.append({"path": str(ad.package_name), "error": str(e)})

    oversized.sort(key=lambda e: e["est_bytes"], reverse=True)
    duplicate_groups = [
        {"key": "{}|{}x{}".format(k[0], k[1], k[2]), "paths": v}
        for k, v in dupe_key_map.items() if len(v) > 1
    ]
    duplicate_groups.sort(key=lambda g: len(g["paths"]), reverse=True)

    return {
        "total_textures": len(all_textures),
        "oversized_count": len(oversized),
        "oversized": oversized,
        "duplicate_groups": duplicate_groups,
        "all_textures": all_textures,
    }


def report(size_threshold=2048):
    data = scan(size_threshold)
    data["exported_at"] = datetime.datetime.now().isoformat()

    saved_dir = os.path.join(unreal.Paths.project_saved_dir(), "AuditExport")
    os.makedirs(saved_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(saved_dir, "texture_audit_{}.json".format(ts))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    unreal.log("[audit_textures] {} textures scanned, {} oversized (> {}px), {} duplicate groups -> {}".format(
        data["total_textures"], data["oversized_count"], size_threshold, len(data["duplicate_groups"]), out_path))
    return out_path


def apply_downsize(target_max_size=2048, size_threshold=2048, dry_run=True):
    data = scan(size_threshold)
    changed = []
    for entry in data["oversized"]:
        path = entry["path"]
        if dry_run:
            changed.append(path)
            continue
        try:
            tex = unreal.EditorAssetLibrary.load_asset(path)
            if tex is None:
                continue
            tex.set_editor_property("max_texture_size", target_max_size)
            unreal.EditorAssetLibrary.save_loaded_asset(tex, only_if_is_dirty=False)
            changed.append(path)
        except Exception as e:
            unreal.log_warning("[audit_textures] failed to cap {}: {}".format(path, e))

    verb = "would cap" if dry_run else "capped"
    unreal.log("[audit_textures] {} {} textures to MaxTextureSize={} (dry_run={})".format(
        verb, len(changed), target_max_size, dry_run))
    return changed


if __name__ == "__main__":
    report()
