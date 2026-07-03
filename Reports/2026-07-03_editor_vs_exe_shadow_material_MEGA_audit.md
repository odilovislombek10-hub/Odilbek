# MEGA AUDIT — Editor ↔ EXE vizualizatsiya farqi (soya + materiallar)
**Sana:** 2026-07-03 · **Levellar:** Glavniy_MirMIron / Pragulka / VR · **Muammo:** package qilingan EXE editordagidan "Medium/washed" ko'rinadi, ayrim materiallar tushmaydi, soya boshqacha.

---

## 0. QISQA XULOSA (3 haqiqiy sabab — hammasi dalil bilan tasdiqlangan)

| # | Sabab | Qayerda tasdiqlandi | Editor↔EXE farqimi? |
|---|---|---|---|
| **A** | **VSM (Virtual Shadow Map) overflow** — Nanite bo'lmagan CAD geometriya (`Level/Export`) soya xaritasini bosib ketadi, soya tushib qoladi | Package **runtime log**, 11250 & 11408-qatorlar | Ha — EXE'da qat'iy xotira, editorda zaxira ko'p |
| **B** | **Materiallar cook bo'lmagan** — `/MeshModelingToolsetExp/Textures/DefaultEmissive` + `DefaultOpacity` (editor-only plugin kontenti) package'ga tushmagan → shu teksturalarga bog'liq materiallar buziladi | Package log, 1215–1235+ qator: `Failed converting package name` | Ha — editorda bor, EXE'da yo'q |
| **C** | **Exposure/kontrast** — auto-exposure qulflanmagan + LocalExposure kontrast 0.8 ga bosilgan → yassi/oqargan tasvir | Package log 426–428, 1296/11270/11333; oldingi audit | Qisman — editor viewport boshqa exposure ishlatadi |

Qo'shimcha (ikkilamchi): Nanite EXE'da dag'alroq edi (`MaxPixelsPerEdge` 2 vs editor 1.0) — **bu hisobotda tuzatildi**. Ba'zi Lumen cvarlar package'da "deferred/dummy" holatda.

---

## 1. METODOLOGIYA — nima audit qilindi
- **Config diff:** `Config/DefaultEngine.ini` (editor o'qiydi) ↔ `Config/DefaultDeviceProfiles.ini` `[Windows DeviceProfile]` (faqat package'da qo'llanadi). Device-profile editorda ISHLAMAYDI (editor `WindowsEditor` profilini oladi) — shuning uchun editor↔EXE farqi AYNAN shu ikki fayl orasidagi zid qiymatlardan chiqadi.
- **Package runtime log:** `E:\MIR MIRON PACKAGE\Windows\Odilbek\Saved\Logs\Odilbek.log` (2026-07-03 17:38 run) — real ishga tushirilgan EXE nima qilganini ko'rsatadi.
- **Level binar tahlili:** `Glavniy_MirMIron.umap` ichidagi `/Engine/` va light-mobility satrlari.
- **Community/UE tadqiqoti:** Epic forumlari + VSM/Lumen hujjatlari (havolalar §5).

---

## 2. SABAB A — VSM SOYA OVERFLOW (foydalanuvchi topgan "shadow" muammosi — TASDIQLANDI)

**Dalil (package log):**
```
[VSM] Non-Nanite Marking Job Queue overflow. Performance may be affected.
This occurs when many non-nanite meshes cover a large area of the shadow map.
  — 11250-qator (17:40:10) va 11408-qator (17:41:04)
```

**Sabab:** Virtual Shadow Maps faqat Nanite bilan yaxshi ishlaydi. Bu 3 levelda `Content/Level/Export/` dagi CAD import proplar (Shape/Cube/door/3dSolid — 43–57MB, Nanite EMAS) + to'liq-detal daraxtlar Nanite emas. Ular katta soya-xarita maydonini qoplaganda VSM "marking job queue" to'lib ketadi va **Nanite bo'lmagan geometriya soya berishdan tushib qoladi** → sahna yassilashadi, kontakt soyalar yo'qoladi ("Medium/washed" hissi).

**Muhim:** Biz oldin buni faqat `r.Shadow.Virtual.AllowScreenOverflowMessages=0` bilan **xabarini o'chirgandik**, muammoning o'zini emas. Editorda RAM zaxirasi ko'proq bo'lgani uchun kamroq bilinadi; package'da qat'iy pool → kuchliroq.

**Nega faqat bu 3 level:** interer levellar yopiq, kam va kichik soya maydoni, CAD prop kam. Bu 3 level ochiq osmon + ulkan CAD maydon → VSM overflow aynan shu yerda.

**Config farqi (tuzatildi):** device-profile'da Nanite dag'alroq edi —
`r.Nanite.MaxPixelsPerEdge`: EXE **2** → editor **1.0**, `r.Nanite.AllowTessellation`: EXE **True** → editor **False**. Ikkisi ham editornikiga tenglashtirildi (`DefaultDeviceProfiles.ini`).

---

## 3. SABAB B — MATERIALLAR COOK BO'LMAGAN ("ayrim materiallar tushmagani" — ANIQ SABAB)

**Dalil (package log, o'nlab marta takrorlanadi):**
```
LogPackageName: Error: GetLocalBaseFilenameWithPath: Failed converting package name
  "/MeshModelingToolsetExp/Textures/DefaultEmissive" to file name
  "/MeshModelingToolsetExp/Textures/DefaultOpacity" to file name
  — 1215–1235+ qatorlar
```

**Sabab:** `MeshModelingToolsetExp` — bu **editor-only** plagin (Modeling Mode). Uning `DefaultEmissive`/`DefaultOpacity` teksturalari package'ga **cook qilinmaydi**. Loyihada qandaydir material(lar) shu teksturalarga bog'langan (ehtimol Modeling tool bilan yasalgan mesh/material) → EXE'da ular yuklanmaydi → material **default/qora/noto'g'ri** ko'rinadi. Bu aynan community'da eng ko'p uchraydigan sabab (§5.1 — "engine/editor content Post Process yoki materialda ishlatilsa cook bo'lmaydi").

**Level Engine-kontent bog'liqliklari** (`Glavniy_MirMIron.umap`):
`/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud_Inst`, `/Engine/EngineMaterials/WorldGridMaterial`, `T_Default_Material_Grid_M/N`, `/Engine/Engine_MI_Shaders/Textures/Bokeh`. Bular odatda cook bo'ladi (engine "always-cook" to'plami), lekin WorldGridMaterial ko'rinsa = biror mesh materialsiz qolgan belgisi.

**Keyingi qadam:** MCP `get_referencers` bilan `/MeshModelingToolsetExp/Textures/DefaultEmissive` ni kim ishlatayotganini topib, o'sha materialning Emissive/Opacity nodini loyiha ichidagi teksturaga (yoki oddiy qiymatga) almashtirish.

---

## 4. SABAB C — EXPOSURE / KONTRAST (yassi/oqargan)

**Dalil (package log):**
```
r.DefaultFeature.LocalExposure.HighlightContrastScale = 0.8   (426-qator)
r.DefaultFeature.LocalExposure.ShadowContrastScale    = 0.8   (428-qator)
r.DefaultFeature.AutoExposure.Method = 1  (auto-exposure YONIQ, qulflanmagan)
r.EyeAdaptation.ExposureCompensationCurveLUT — true/false o'zgarib turadi (1296, 11270, 11333)
```

**Sabab:** (1) LocalExposure kontrast masshtabi 0.8 (<1.0) — soya ham, yorug' ham kontrastini kamaytiradi → sutli/yassi. (2) Auto-exposure hech qanday PostProcessVolume'da qulflanmagan → EXE editordan ~1 stop yorqinroq lanaydi (oldingi audit ham shuni topgan). Editor viewport o'zining exposure'ini ishlatadi, shuning uchun editorda "to'g'ri" ko'rinadi.

**Yechim:** level global PostProcessVolume yoki UDS post-process'da **exposure'ni qulflash** (Manual metering, Min EV100 = Max EV100) + LocalExposure kontrastni 1.0 ga yaqinlashtirish yoki o'chirish.

---

## 5. QOLGANLAR QANDAY HAL QILGAN — UE community / open-source tadqiqoti

**5.1 — Editor/Engine kontenti cook bo'lmaydi (Sabab B bilan bir xil)**
Epic forum: PostProcessVolume yoki materialda **Engine/editor-only kontent** (cubemap, tekstura) ishlatilsa, u package'ga cook bo'lmaydi → EXE qora/washed. **Yechim: shu assetlarni loyiha papkasiga nusxalab, undan referens qilish.**
→ *Shadows ok in editor but too dark in packaged build* — forums.unrealengine.com/t/359316

**5.2 — Static yorug'lik + Lumen ziddiyati**
UE5.6+ da Lumen bilan Static/Stationary yorug'liklar to'g'ri cook bo'lmaydi → package qorong'i/kam soya. **Yechim: barcha yorug'liklarni (Directional + SkyLight ham) Movable ga o'tkazish.** (Bizda `AllowStaticLighting=False` — hamma dinamik bo'lishi kerak, lekin actor mobility hali Static bo'lsa muammo bo'ladi; tekshirish kerak.)
→ *Unreal Editor and Packaged Build different results* — forums.unrealengine.com/t/2726142

**5.3 — VSM Non-Nanite overflow (Sabab A bilan bir xil)**
Epic forum + VSM hujjati: "VSM faqat Nanite uchun mo'ljallangan; yo har bir meshni Nanite qil, yoki Shadow Map Method'ni oddiy Shadow Maps'ga o'zgartir (Project Settings → Engine → Rendering → Shadows)." **Yechim: og'ir CAD/foliage meshlarni Nanite'ga o'tkazish** (asosiy), yoki bu geometriya uchun oddiy soya-xarita.
→ *Non-nanite Marking Job Queue Overflow warning* — forums.unrealengine.com/t/2172645
→ *VSM Non-Nanite Marking Job Queue overflow* — forums.unrealengine.com/t/2606445

**5.4 — Rendering API farqi (D3D12 vs D3D11)**
Agar package D3D11'ga tushsa, VSM/Nanite o'chadi (UE4-uslub soya). **Yechim: D3D12 majburlash** (`-dx12` / Project Settings default RHI = DX12). Bizda log D3D12 ko'rsatyapti, lekin tekshirishga arziydi.
→ VSM hujjati: dev.epicgames.com/documentation/.../virtual-shadow-maps-in-unreal-engine

---

## 6. TUZATISHLAR

### ✅ Shu hisobotda qilindi
- `Config/DefaultDeviceProfiles.ini`: `r.Nanite.MaxPixelsPerEdge` 2→**1.0**, `r.Nanite.AllowTessellation` True→**False** (EXE geometriya/soyani editorga tenglashtirish). **Qayta package kerak** — device-profile `.pak` ichiga bakolanadi, tayyor EXE'da loose config yo'q.

### 🔜 Tavsiya (muhimlik tartibida)
1. **Sabab B (materiallar):** MCP `get_referencers` → `/MeshModelingToolsetExp/Textures/DefaultEmissive` va `DefaultOpacity` ni ishlatgan materialni topib, teksturalarni loyiha ichidagilarga almashtirish. **Eng aniq va tez g'alaba.**
2. **Sabab C (exposure):** 3 levelning global PostProcessVolume/UDS'ida exposure qulflash + LocalExposure kontrast 0.8→1.0.
3. **Sabab A (VSM soya):** yorug'lik mobility tekshirish (§5.2 — Movable), so'ng og'ir `Level/Export` CAD proplarni Nanite'ga o'tkazish (asl yechim). Vaqtinchalik: shu geometriya uchun VSM o'rniga oddiy soya.
4. **Qayta package qilib** editor bilan yonma-yon solishtirish (diag texnikasi: inner binary + `exec diag.txt` + HighResShot — [[unreal_packaged_vs_editor_exposure]]).

---

## 7. HAVOLALAR (manbalar)
- Shadows ok in editor but too dark in packaged build — https://forums.unrealengine.com/t/shadows-ok-in-editor-but-too-dark-in-packaged-build/359316
- Unreal Editor and Packaged Build different results — https://forums.unrealengine.com/t/unreal-editor-and-packaged-build-different-results/2726142
- Non-nanite Marking Job Queue Overflow warning — https://forums.unrealengine.com/t/non-nanite-marking-job-queue-overflow-warning/2172645
- [VSM] Non-Nanite Marking Job Queue overflow — https://forums.unrealengine.com/t/vsm-non-nanite-marking-job-queue-overflow/2606445
- VSM overflow despite all meshes Nanite — https://forums.unrealengine.com/t/vsm-non-nanite-marking-job-queue-overflow-warning-despite-all-meshes-being-nanite-enabled/2718622
- Virtual Shadow Maps (UE hujjati) — https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-shadow-maps-in-unreal-engine
