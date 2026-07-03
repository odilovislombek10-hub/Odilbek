"""
capture_play_diag.py
=====================
Play (PIE) davomida RT-geometry + texture-streaming xotira holatini
LOG va memreport faylga yozib oladi. "0 B / 15,999 EiB" over-budget
xatosining HAQIQIY raqamlarini taxminsiz ko'rish uchun.

QANDAY ISHLATILADI:
  1. Editor'da kerakli levelni (VR yoki Glavniy_MirMIron) oching.
  2. PLAY (yoki VR Preview) tugmasini bosing.
  3. Play ishlab turgan payt Output Log'dagi buyruq qatorini
     "Python" rejimiga o'tkazib, quyidagini yozing:
         import capture_play_diag
     (yoki qayta ishga tushirish uchun:)
         import importlib, capture_play_diag; importlib.reload(capture_play_diag)
  4. Log'da ===== markerlar orasida natija chiqadi; to'liq breakdown
     Saved/Profiling/MemReports/ ichidagi .memreport faylida bo'ladi.

Eslatma: buyruqlar AKTIV world'ga yuboriladi — Play ishlayotgan bo'lsa
PIE world'iga (ya'ni haqiqiy Play holati) boradi.
"""
import unreal

def _world():
    # Play ishlab turgan bo'lsa PIE world'ini, aks holda editor world'ini qaytaradi
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    try:
        w = ues.get_game_world()
    except Exception:
        w = None
    if w is None:
        w = unreal.EditorLevelLibrary.get_editor_world()
    return w

def _exec(world, cmd):
    unreal.log("===== [DIAG] exec: {} =====".format(cmd))
    unreal.SystemLibrary.execute_console_command(world, cmd)

def run():
    w = _world()
    is_pie = False
    try:
        is_pie = w is not None and w.get_name().startswith("UEDPIE")
    except Exception:
        pass
    unreal.log("########## capture_play_diag START (world={}, PIE={}) ##########".format(
        w.get_name() if w else "None", is_pie))

    if not is_pie:
        unreal.log_warning("[DIAG] Play (PIE) ISHLAMAYAPTI — avval PLAY bosing, keyin skriptni qayta ishga tushiring. "
                           "Hozir editor world'i o'lchanadi (xato faqat Play'da chiqishi mumkin).")

    # 1) Joriy kalit cvar qiymatlari (haqiqatan qo'llangan qiymat log'ga chiqadi)
    for cv in [
        "r.Streaming.PoolSize",
        "r.RayTracing.ResidentGeometryMemoryPoolSizeInMB",
        "r.RayTracing.UseReferenceBasedResidency",
        "r.RayTracing.NumAlwaysResidentLODs",
        "r.Lumen.HardwareRayTracing",
    ]:
        _exec(w, cv)              # argumentsiz -> joriy qiymatni log'ga bosadi

    # 2) Texture streaming holati (pool nechchi MB, nechta oshgan)
    _exec(w, "Streaming.ListStreamingTextures")
    _exec(w, "r.Streaming.LimitPoolSizeToVRAM")

    # 3) RHI / RT-scene xotira breakdown
    _exec(w, "rhi.DumpMemory")

    # 4) To'liq memory report — Saved/Profiling/MemReports/ ga fayl yozadi
    #    (RTX Geometry, Mesh, Texture bo'limlari bilan)
    _exec(w, "memreport -full")

    unreal.log("########## capture_play_diag END — natija: Output Log + Saved/Profiling/MemReports/*.memreport ##########")

# import qilinganda avtomatik ishga tushadi
run()
