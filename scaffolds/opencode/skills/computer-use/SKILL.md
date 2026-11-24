---
name: Computer Use
description: Native Windows desktop Computer Use via zyren-ufo (Microsoft UFO + Gemini 3.8 Live). Use whenever the user asks for computer use, التحكم في الشاشة, clicking Windows taskbar/desktop/toolbar icons, launching or driving native Windows apps and games, or visually verifying desktop GUIs — instead of the in-app browser skill.
---

# Native Windows Computer Use (`zyren-ufo`)

Use the `zyren-ufo` MCP tools whenever the user asks to control the computer screen, use "computer use" (`التحكم في الشاشة` / `التحكم في الكمبيوتر`), click icons on the Windows desktop, taskbar, or application toolbars, automate native Windows applications or games, or inspect/verify real OS windows visually.

## Choosing Computer Use vs In-App Browser

- **Use `zyren-ufo` (`ufo_*`) tools** when the request refers to the OS desktop, taskbar icons, window toolbars, native Windows apps, games, external browsers already on screen, file dialogs, or explicitly asks to "use your computer use feature". Do **not** load the `browser` skill as a substitute for OS/desktop/taskbar interaction.
- **Use the `browser` skill** only when specifically inspecting/automating web DOM tabs inside OpenCode's embedded browser.

## Direct Computer-Use Workflow

1. Check state or see the desktop & taskbar with annotated UIA IDs:
   - `ufo_capture_desktop_view(annotate=True)` — returns an annotated JPEG screenshot of the real Windows desktop + taskbar icons with numeric `control_id` labels (`id`, `name`, `center_xy`).
   - `ufo_list_desktop_windows(include_screenshot=False)` — lists open windows and their `window_id` and `name`.
2. Focus windows or inspect controls inside an active app:
   - `ufo_select_window(window_name="...", maximize=False)` or `ufo_select_window(window_id="...")`
   - `ufo_inspect_active_window(filter_query="", annotate=True)`
3. Act on controls or coordinates:
   - `ufo_click_control(control_id="...", button="left", double=False)` (automatically double-clicks desktop shortcut icons when left-clicked)
   - `ufo_click_coordinates(x=..., y=..., button="left", double=False, space="auto")`
   - `ufo_drag_coordinates(start_x=..., start_y=..., end_x=..., end_y=...)`
   - `ufo_type_text(text="...", control_id="...", clear_existing=False, press_enter=False)`
   - `ufo_press_keys(keys="enter", hold_seconds=0.0, repeat=1)`
   - `ufo_scroll_window(direction="down", clicks=3)`
   - `ufo_launch_application(command="notepad.exe")`
   - `ufo_game_control(...)` for low-level DirectInput / scancode holds and camera movement
4. Verify the real screen outcome:
   - `ufo_reflect_and_verify(expected_state="...", include_desktop=True)`

## Delegating to Live Voice vs Direct Atomic Control

- `ufo_run_visual_goal(goal="...", max_steps=15, timeout_seconds=120)`:
  - When **Live Voice (`gemini-3.8-live`) is ON**, routes the visual goal into that active singleton Live Voice + Vision session so there is never a second conflicting model.
  - When **Live Voice is OFF**, returns a fresh annotated desktop screenshot (`status: "voice_inactive"`, `mode: "direct_mcp_required"`) so you execute the steps directly using the atomic `ufo_*` tools without invoking any other hidden model.

## Safety Gate

- Call `ufo_status()` anytime to inspect `elevated` (Administrator UIPI status), `voice_running`, and `execution_enabled`.
- If any `ufo_*` tool returns `status: "execution_paused"`, desktop automation is paused by the user's emergency safety gate. Inform the user clearly and do **not** claim actions were performed.
