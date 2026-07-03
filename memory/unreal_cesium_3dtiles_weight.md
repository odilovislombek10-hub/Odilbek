---
name: unreal_cesium_3dtiles_weight
description: Diagnostics-panel yellow warning root cause = Cesium Google 3D Tiles + Lumen HWRT; Cesium lightened 2026-07-03
metadata: 
  node_type: memory
  type: project
  originSessionId: a5c93420-2dd1-430e-8bf1-950df8a06e13
---

2026-07-03: Foydalanuvchi "Diagnostics panelida ogohlantirish (sariq ⚠) nega turibdi, loyihani nima og'irlashtiryapti" deb so'radi. Status-bar Diagnostics widget'i sariq — bu umumiy performans ogohlantirishi (kadr vaqti/GPU/hitching chegaradan oshgan), alohida xato emas.

Glavniy_MirMIron.umap dagi og'irlik manbalari (og'irdan yengilga):
1. **Cesium + Google Photorealistic 3D Tiles** — eng katta yuk. 2 ta Cesium3DTileset actor: `Cesium3DTileset_0` (IonAssetID=0, bo'sh/leftover) va `Cesium3DTileset_1` ("Google Photorealistic 3D Tiles", IonAssetID=2275207). Real-dunyo shahar geometriyasini oqim bilan yuklaydi. Yana `CesiumGaussianSplatSystemActor` (class CesiumGaussianSplatActor) — Niagara GaussianSplatSystem compile 28.7s olgan; Google tayllar splat saqlamaydi, shuning uchun render qilmaydi, faqat startup compile yeydi (plagin qayta yaratishi mumkin — o'chirilmadi).
2. Lumen Hardware Ray Tracing YONIQ (r.Lumen.HardwareRayTracing:1 + Reflections + HitLighting) — og'ir, [[unreal_gpu_crash_lumen_hwrt_pagefault]] bilan bog'liq (biz faqat Async=0 qilgandik, HWRT o'zi hali yoniq). HALI TUZATILMAGAN.
3. 200+ PSO creation hitches, 0 precached — tutilish (stutter). PSO cache ishlamayapti.
4. ~2600 alohida StaticMeshActor (instancing yo'q) Glavniy_MirMIron da.
5. 8 ta Nanite mesh + translucent glass material (Frame, UE_BYD_Seagull_Object001, UE_COBALT_LTZ_windshield×3, wicker, wicker1, Cylinder001) — Nanite fallback + log spam. HALI TUZATILMAGAN (Disallow Nanite kerak).

**Cesium yengillashtirildi (2026-07-03, MCP orqali, level saqlandi):** ikkala tilesetda MaximumScreenSpaceError 48→64 (dag'aroq LOD), CreatePhysicsMeshes true→false (real tayllarga kolliziya keraksiz, katta CPU/xotira yutug'i), MaximumSimultaneousTileLoads 20→8, Tileset_1 da PreloadSiblings true→false, LoadingDescendantLimit 20→10. Google tileset config: EnableFrustum/Fog/OcclusionCulling allaqachon true, Cache=256MB.

**Cesium LOD chuqurroq optimizatsiya (2026-07-03, RT-geometry over-budget uchun, MCP orqali, level saqlandi):** Cesium3DTileset'da RT'ni o'chiradigan property YO'Q (CanEnableRayTracing yo'q; list_properties'da ray/nanite toggle topilmadi) — RT yuki faqat geometriya miqdoriga bog'liq, shuning uchun eng kuchli richag = LOD dag'aroqlashtirish + ekrandan tashqari tayllarni tushirish. IKKALA tilesetga (`_1`=Google IonAssetID=2275207 asosiy, `_0`=IonAssetID=0 bo'sh/leftover) qo'llandi: `MaximumScreenSpaceError` 64→**128** (dag'aroq LOD, ~2× kam uchburchak/BLAS), `CulledScreenSpaceError` 64→**192**, `EnforceCulledScreenSpaceError` false→**true** (ko'rinmaydigan tayllarni agressiv tushiradi → resident RT geometriya kamayadi). CreatePhysicsMeshes=false, MaximumCachedBytes=256MB (o'zgarmadi), MaxSimultaneousTileLoads=8 (o'zgarmadi). Actorlar "external emas" => save_actor ishlamadi, AssetTools.save_assets('/Game/Level/Odilbek/Glavniy_MirMIron') bilan saqlandi. Bog'liq: [[unreal_rt_overbudget_spurious_and_diag_technique]] (=1 fix bilan birga sinaladi).

Keyingi qadamlar (foydalanuvchi so'rasa): Lumen HWRT o'chirish, 8 glass meshga Disallow Nanite, Gaussian splat actor o'chirish/tekshirish, bo'sh Cesium3DTileset_0'ni butunlay o'chirish.
