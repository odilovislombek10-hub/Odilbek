# Play xatoliklari — diagnostika va tuzatish (2026-07-02)

## Qilingan ish
Foydalanuvchi Play tugmasini bosganda ekranga uchta xatolik chiqdi (skrinshot orqali berildi):
- `TEXTURE STREAMING POOL OVER 32,867 MiB BUDGET`
- `RAY TRACING GEOMETRY - ALWAYS RESIDENT MEMORY EXCEEDS 20% OF THE BUDGET (0 B / 15,999 EiB)`
- `RAY TRACING GEOMETRY - REQUESTED MEMORY OVER BUDGET 2,174 GiB / 15,999 EiB`

Ikkalasi ham to'liq audit qilindi va sababi aniqlangach jonli (`unreal-mcp` orqali, Editor ochiq holda) tuzatildi.

## 1-xato: Ray Tracing xotira portlashi

**Audit:** `Config/DefaultEngine.ini` va `Config/DefaultDeviceProfiles.ini` solishtirildi.

**Topilgan xato:** `DefaultEngine.ini`da ataylab o'chirilgan (`r.RayTracing.Shadows=False`, `r.RayTracing.Skylight=False`, izoh: "Lumen HWRT hammasini qiladi, alohida RT o'chirildi — 2x yukni oldi"), lekin `DefaultDeviceProfiles.ini` → `[Windows DeviceProfile]` bo'limida bu ikkalasi `True` qilib qayta yoqilgan edi. Device-profile CVarlari Play/Standalone paytida DefaultEngine.ini'dan keyin qo'llanadi va g'olib chiqadi — natijada Lumen HWRT ustiga yana alohida RT Shadows + Skylight passlari ham yoqilgan, bu esa Cesium orqali stream qilinayotgan katta dunyo geometriyasi uchun ray-tracing acceleration structure (BLAS) qurishni ikki barobar oshirgan.

**Tuzatish yo'li:** `Config/DefaultDeviceProfiles.ini`dagi ikkala qatorni `False` ga o'zgartirish, `DefaultEngine.ini` bilan mos qilish.

**Holat:** ✅ Tuzatildi. (Kuchga kirishi uchun Editor/game qayta ishga tushirilishi kerak — device profile CVarlari faqat startupda o'qiladi.)

## 2-xato: Texture Streaming Pool ~32GB oshib ketgan

**Audit:** Avvalgi sessiyaning `Saved/AuditExport/mcp_texture_audit_20260701.json` audit faylidagi 393 ta "oversized" (2048px dan katta) tekstura ro'yxati joriy xato bilan solishtirildi.

**Topilgan xato:** 393 ta tekstura siqilmagan holda hisoblansa ≈ **32.78 GB** — bu rasmdagi "32,867 MiB" xatosiga deyarli aynan mos keladi. Shundan **99 tasi** `Content/Level/Odilbek/Planerovka/` (va `Xonadonlar/1-8Block`) papkasidagi qavat-reja skanlari, ba'zilari 9925×7017 pikselgacha (~70 megapiksel). `unreal-mcp` orqali jonli tekshirildi (`ObjectTools.get_properties`):
- `CompressionSettings = TC_EditorIcon` — siqilmagan (4 bayt/piksel, oddiy BC7'dan 4x og'ir)
- `maxTextureSize = 0` — cheklovsiz, original o'lchamda (bu ataylab shunday — matn o'qilishi buzilmasin deb)
- **`NeverStream = true`** — asosiy sabab: bu tekstura hech qachon ko'rinmasa ham doimiy ravishda to'liq VRAM'da turadi

Bu uchtasi birgalikda ~18GB'ni doimiy band qilib turgan, garchi foydalanuvchi qavat-reja widgetini hech qachon ochmasa ham.

**Tuzatish yo'li:** Faqat `NeverStream` ni `false` qilish — o'lcham va sifat (matn aniqligi) o'zgarmaydi, faqat endi bu teksturalar normal streaming tizimiga bo'ysunadi: widget ko'rsatilmaganda xotiradan tushadi, ko'rsatilganda to'liq sifatda qayta yuklanadi.

**Bajarilishi:** `unreal-mcp` `ProgrammaticToolset.execute_tool_script` orqali barcha 99 ta `Texture2D` asseti (`AssetTools.find_assets`, `/Game/Level/Odilbek/Planerovka`, recursive) topildi, har biriga `ObjectTools.set_properties({"NeverStream": false})` qo'llanildi, so'ng `AssetTools.save_assets` bilan diskka saqlandi.

**Natija:**
```json
{"total_found": 99, "fixed": 99, "failed": [], "saved": true}
```

**Test:** Namuna tekstura (`4blok_tipovoy-page-00001`) uchun tuzatishdan keyin qayta `get_properties` chaqirildi — `NeverStream: false` tasdiqlandi.

**Holat:** ✅ Tuzatildi, jonli qo'llanildi va tasdiqlandi (99/99 muvaffaqiyat, xatosiz).

## Keyingi qadam
Foydalanuvchi Play'ni qayta bosib, xatoliklar yo'qolganini vizual tasdiqlashi kerak (RT tuzatishi Editor qayta ishga tushirilgandan keyin to'liq kuchga kiradi).
