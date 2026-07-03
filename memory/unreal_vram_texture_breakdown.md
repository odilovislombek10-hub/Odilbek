---
name: unreal_vram_texture_breakdown
description: "Why VRAM/memory looks full — fixed pool reservations vs actual texture working set; 1777 project textures, which are/aren't in Glavniy_MirMIron"
metadata: 
  node_type: memory
  type: project
  originSessionId: a5c93420-2dd1-430e-8bf1-950df8a06e13
---

2026-07-03: Foydalanuvchi "VRAM nega 12-14 GB to'lyapti, hamma teksturamiz 2K-ku, xotirani nima to'ldiryapti, 1777 tekstura hammasi levelda bormi?" deb so'radi.

**Fakt 1 — VRAM "to'la" ko'rinishi asosan config POOL REZERVLARIdan (haqiqiy ishlatish emas):**
- `r.Streaming.PoolSize=12288` (12 GB) + `r.Streaming.UseFixedPoolSize=1` → texture streaming budjeti 12 GB. Budjet katta bo'lgani uchun streamer teksturalarni agressiv rezident saqlaydi (kam evict qiladi) → VRAM ~12 GB gacha to'ladi.
- `r.Nanite.Streaming.PoolSize=4096` (4 GB)
- `r.RayTracing.ResidentGeometryMemoryPoolSizeInMB=3072` (3 GB, Lumen HWRT uchun)
- Jami faqat pool'lar ~19 GB / 24 GB (RTX 3090). + Lumen surface/radiance cache + VSM + render target + Cesium runtime tayl teksturalari.
- Log tasdiqi: "LogRHI: Texture pool is 14839 MB (70% of 21198 MB)". Streaming ISHLAYAPTI (proof: Woodchip_4K get_size hozir 32×32 = ekranda yo'q, evict qilingan). Ya'ni haqiqiy rezident < 12 GB, lekin fixed budjet baribir band ko'rsatadi.
- FIX: r.Streaming.PoolSize 12288→6144, UseFixedPoolSize 1→0, Lumen HWRT off (3GB RT pool bo'shaydi), Nanite pool 4096→2048.

**Fakt 2 — hamma tekstura 2K EMAS.** Butun /Game da 1777 Texture2D = disk 11.94 GB. Bucket'lar: 8K+ 11 fayl=1.25GB, 4K 127 fayl=4.47GB, 2K 424 fayl=4.41GB, 1K 580=1.61GB, <=512 635=0.2GB. Eng og'ir teksturalar: paving_granite_plates_RANDOM_normal 220MB, PAVING_02..._Normal 181MB, uexlbdbn_8K_Albedo/Normal ~124MB, tlomaeady_8K_Albedo 112MB, AutomotiveMaterials Leather 4K ~90MB, Megascans Woodchip/Asphalt/Concrete 4K. DIQQAT: uexlbdbn "8K" nomli lekin get_size 2048 qaytardi (MaxTextureSize cap yoki oldingi downsize) — disk hajmi = MAX/manba, VRAM = stream qilingan mip.

**Fakt 3 — 1777 teksturaning HAMMASI Glavniy_MirMIron da EMAS.** Level direct-deps dump'ida bu paketlar YO'Q → VRAM'ga yuklanmaydi, faqat disk shishiradi:
- PosedHumansPack1 = 2.56 GB (254 fayl) — get_referencers: T_Man49_N faqat o'z MI_Man49 → levelda ishlatilmaydi
- StarterContent = 0.48 GB — T_Brick_Cut_Stone_D faqat o'z materiali → ishlatilmaydi
- PosedHumansShoppingPack1 ~0.28 GB
Levelda ISHLATILADIGANLAR: ArchvisDefault (materials/cars/bruschatka/asphalt), TwinEra, ba'zi Megascans (Concrete_Wall, Dark_Patterned_Tiles, Painted_Gun_Metal — hammasi emas), Statik_tree/Speed_tree, Mavrid, Parallax (Hotel_PARALLAX EXR oyna interyerlari), BlankDefault mebel, Level/Export geometriya, Planerovka+3Drazrez, PLOSHATKA, UltraDynamicSky.
- FIX: ishlatilmagan paketlarni (PosedHumansPack1 ~2.6GB, StarterContent) o'chirish → loyiha diskda ~3.3GB yengillashadi.

MCP cheklovi: konsol buyrug'i (stat rhi/memreport/listtextures) MCP orqali yo'q; get_dependencies stale/redirector ссылкага urilsa BUTUN skriptni to'xtatadi (try/except ushlamaydi) — rekursiya o'rniga get_referencers/disk-scan ishlatildi. Bog'liq: [[unreal_cesium_3dtiles_weight]], [[unreal_perf_texture_audit]].
