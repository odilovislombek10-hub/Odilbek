---
name: unreal_packaging_workflow
description: How to package the Odilbek project to E:\MIR MIRON PACKAGE — the two gotchas (long-path + MCP port 8000) and the working command sequence
metadata: 
  node_type: memory
  type: project
  originSessionId: adacb46f-19fa-47a9-8a7e-6f008e069169
---

2026-07-03: Successfully packaged Odilbek (UE 5.8, Win64 Development) to **E:\MIR MIRON PACKAGE** — 28GB total, Odilbek.exe + Odilbek-Windows.pak (27GB). Done via command-line RunUAT `BuildCookRun` (NOT the Editor menu — external headless process, so no progress shows in the open Editor; that's normal). Engine at `C:\Program Files\Epic Games\UE_5.8`. Compiled with VS 2022 Community 14.44. Cook = 5375 packages, ~16 min; pak+archive ~13 min.

**TWO blocking gotchas, both must be handled:**

1. **Long-path (MAX_PATH 260) cook errors.** Project sits at deep path `D:\mirmironnnn oxirgiiii\Unreal Engine\Unreal Engine\Odilbek\` (~61 chars) + long asset names (e.g. `Content/Statik_tree/Tuvak_gullar/Collection_Indoor_outdoor_plant_163_concrete_dirt_vase_pot_palm_cactus/...`) → cooked path exceeds 260 → `LogCook: Error: Couldn't save package, filename is too long (273 >= 260)`. Windows LongPathsEnabled=0 and we're NOT admin. FIX (no admin, no file move, no asset rename): created a **directory junction `D:\O` → project dir** via PowerShell `New-Item -ItemType Junction`, then packaged with `-project="D:\O\Odilbek.uproject"`. Shortens cook path by ~56 chars → under 260. Junction persists; reuse it.

2. **MCP HttpListener port 8000 conflict.** The `ModelContextProtocol` plugin binds 127.0.0.1:8000. When the user's **open Editor** already holds that port, the cook commandlet logs `LogHttpListener: Error: HttpListener unable to bind to 127.0.0.1:8000` → this SINGLE error makes cook return `ExitCode=25 (Error_UnknownCookFailure)` even though all 5375 packages cooked fine on disk. FIX options: (a) close the Editor before a full cook, OR (b) since cook output (D:\O\Saved\Cooked\Windows\Odilbek, 27GB, has CookMetadata.ucookmeta + packagestore.manifest) is complete and valid, re-run with **`-skipbuild -skipcook -stage -pak -archive`** — stage/pak/archive don't bind the port, so it succeeds. Used (b) → BUILD SUCCESSFUL.

**Working command (via junction), full:**
`RunUAT.bat BuildCookRun -project="D:\O\Odilbek.uproject" -noP4 -platform=Win64 -clientconfig=Development -build -cook -stage -pak -archive -prereqs -archivedirectory="E:\MIR MIRON PACKAGE" -utf8output -nocompileeditor`
For the skipcook finish: replace `-build -cook` with `-skipbuild -skipcook`.

**CRITICAL — `-prereqs` flag (added 2026-07-03):** The first package (28GB) was built WITHOUT `-prereqs`, so the VC++ redist was NOT staged → on a clean PC the bootstrap `Odilbek.exe` shows *"The following component(s) are required to run this program: Microsoft Visual C++ 2015-2022 Redistributable (x64)"* and exits. `DefaultGame.ini` already has `IncludePrerequisites=True`, but command-line BuildCookRun needs the explicit `-prereqs` flag to actually stage the redist. Engine ships `vc_redist.x64.exe` at `C:\Program Files\Epic Games\UE_5.8\Engine\Extras\Redist\en-us\`. Fix = always include `-prereqs`; it copies vc_redist into the staged build and the bootstrap launcher auto-installs it on first run. NO editor or .ini change needed — pure command-line flag.

**How I ran it:** PowerShell `Start-Process -FilePath <RunUAT.bat> -ArgumentList <argline> -RedirectStandardOutput $log -RedirectStandardError $err -Wait -NoNewWindow` in background (Bash tool's Git-Bash mangles the "Program Files" space — use PowerShell). Gave user a live log via a separate `Start-Process powershell -NoExit -Command "Get-Content -LiteralPath '<log>' -Wait -Tail 40"` window titled 'MIR MIRON PACKAGE - LIVE LOG' (keep the inline command ASCII-only — an apostrophe in "yo'l" caused a parse error and a blank window). Kill only `UnrealEditor-Cmd`/`ShaderCompileWorker`/`UnrealPak`/`AutomationTool`(dotnet) to stop a run — NOT `UnrealEditor.exe` (the user's open editor).

Non-blocking warning seen: `M_Roofs` material fails to compile for PCD3D_SM5 (a TextureSample node missing its input texture) → uses default material in-game on SM5 only; pre-existing content bug, not packaging-caused. See [[unreal_project_overview]].
