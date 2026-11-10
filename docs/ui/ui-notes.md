# UI notes (ui-ux workstream)

## Screen flow

Main menu (`CampaignScreen`, view MENU: Continue / Campaign / Settings) -> chapter select (5 tiles) ->
mission select (20 slots per chapter) -> mission (`MissionScreen`, owned by the orchestrator) -> result panel
(`MissionHud`: Next mission / Run it again or Retry / Missions) -> mission select. `SettingsScreen` is reached from
the menu and returns via `back_pressed`. Screens only emit signals (`mission_selected(id)`, `settings_requested`,
`sound_toggled`, `music_toggled`, `vibration_toggled`, `back_pressed`, HUD `next_pressed`, `exit_pressed`);
`main.gd` routes and saves. `go_back()` steps back inside CampaignScreen (also bound to `ui_cancel`).

## Slot states (mission select)

Completed (shows best Mission Points from `ProgressData.mission_result(id).best_points`, replayable),
Available (accent button), Locked (authored, previous authored mission not completed), Not yet available
(file absent). A chapter tile is locked until its first authored mission is unlocked. Continue = first
authored, unlocked, uncompleted mission in campaign order; disabled when none.

## Theme and fonts

One theme: `assets/ui/theme/tfj_theme.tres` (id `GAM-UI-THEME-A`), loaded via `AssetLibrary.resource`
when the screen's `library` property is set before it enters the tree; otherwise the built-in `UiKit.make_theme()`
fallback. Fonts come from that theme (no per-screen font resources); sizes are set with `font_size` overrides:
56 title, 40/32 headers, 28 settings rows, 20 tiles, 18 captions. Widgets are built with `UiKit` (primary/regular
buttons, labels); the warm accent marks only the single primary action. Colours come from `Palette`.

## Spacing scale and layout

8 / 16 / 24 / 32 px (`SPACE_S/M/L/XL`) on the 1280x720 base; screen margin 32, element gap 16. Touch targets
are at least 88 px tall. Lists are a vertical `ScrollContainer` around a `GridContainer` (1 column for chapters,
2 for missions) with horizontal scrolling disabled, so 20 slots and narrow or wide aspect ratios do not break the
layout (project uses `canvas_items` stretch, `expand` aspect).

## Audio

`audio` property (AudioService, null-safe) plays `ui_click`, `ui_confirm`, `ui_back` only.
