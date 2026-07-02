# Muslimatun — Odilbek UE ArchViz loyihasi bo'yicha ishlar arxivi

Bu repo Unreal Engine loyihasining o'zi emas (u juda katta, 20+ GB binary content) — bu yerda faqat
Claude bilan qilingan **audit va tuzatish ishlari** hujjatlashtirilgan: sessiyalar xotirasi (memory)
va Unreal Editor'dan eksport qilingan audit hisobotlari (JSON).

## Tarkib

- `memory/` — har bir mavzu bo'yicha yig'ilgan bilim: loyiha tuzilishi, level'lar, ArchVizExplorer
  freymvorki, perf/texture audit, 2026-07-01 dagi tuzatishlar, 2026-07-02 dagi Wood material
  shading-model bug fix va h.k.
- `AuditExport/` — `Content/Python/audit_level_export.py` orqali eksport qilingan xom Details-panel
  ma'lumotlari (har bir level uchun actor/light/material qiymatlari), texture/lightmap audit
  natijalari va yig'ma summary report.

## 2026-07-02: Wood material tuzatildi

`/Game/Mavrid/Default_M/Base_Material` materialining Shading Model'i noto'g'ri `MSM_TwoSidedFoliage`
(barglar uchun) bo'lib turgani sababli barcha `Wood_*`/`welo_*`/`Soil*` va ba'zi avtomobil detal
materiallari (jami 19 ta asset) oq/xira ko'rinar edi. `MSM_DefaultLit`ga o'zgartirilib tuzatildi.
Batafsil: `memory/unreal_wood_material_shading_model_fix.md`.
