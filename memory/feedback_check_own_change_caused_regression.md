---
name: feedback-check-own-change-caused-regression
description: "If something worked before my change and broke after, first check whether MY change is the regression — don't frame my own bug as an inherent tradeoff"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 21e349b1-59c6-4c93-be29-04347d952b75
---

2026-07-03: I added `vr.InstancedStereo=True` as a VR "optimization" (16:21). VR Play then crashed (17:11) with a RenderThread access-violation in the RT persistent-SBT build. I diagnosed it as the known "RT + Instanced Stereo" incompatibility and framed the fix (InstancedStereo=False) as a *tradeoff where we lose ~30-40% perf*. User pushed back: "it worked BEFORE your optimization, it crashed AFTER — this is YOUR mistake, check carefully." He was right. Git + crash log proved HWRT was on since the initial commit (VR worked), and MY 16:21 change is what created the crash pair. Setting it False loses NOTHING vs. the previously-working state — it just reverts my regression.

**Why:** Framing my own regression as a neutral "tradeoff" hides that I broke a working feature, and wastes the user's trust/time. The RT+InstancedStereo pair only existed because I added one half of it.

**How to apply:** When the user reports "it worked before, broke after your change," FIRST run `git log -S "<the setting/line I added>"` and check the crash log for MY cvar being active — confirm whether my change is the regression BEFORE proposing a fix or calling it a tradeoff. If my change caused it, say so plainly and treat the fix as a revert of my bug, not a compromise. See [[unreal_vr_perf_optimization]], [[feedback_respond_in_uzbek]].
