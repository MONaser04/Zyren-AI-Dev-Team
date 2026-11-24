---
description: Check or control the Unified Gemini 3.8 Live + UFO desktop voice & computer-use status
---

Call `ufo_status` from the `zyren-ufo` MCP server right now and present a concise status summary covering:
1. Daemon health & Windows Administrator elevation (`elevated`)
2. Live Voice state (`voice_running`, `voice_model`, `audio_muted`, `narration_mode`)
3. Unified desktop safety gate (`execution_enabled`)
4. Currently active OpenCode agent & session

If `$ARGUMENTS` contains a concrete desktop/visual request, execute or inspect it using the `zyren-ufo` MCP tools (e.g., `ufo_list_desktop_windows`, `ufo_capture_desktop_view`, or `ufo_run_visual_goal`). Otherwise remind the user concisely of the Live Voice toolbar button / side panel (`Ctrl/Cmd+Shift+V` or Command Palette: `Zyren: Toggle Live Voice`) and standalone elevated launcher `<PATH_TO_UFO>/run_live_ufo.bat`.
