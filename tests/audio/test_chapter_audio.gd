extends TestCase
## Chapter-level audio plans (data/audio.json "chapters"): every referenced file exists, each chapter
## 1-5 resolves to a complete plan, missions without their own plan inherit their chapter's plan, and
## the baseline ids frozen in docs/interfaces.md section 6 are unchanged.

const BASELINE_SOUNDS := ["breach_detonate", "breach_launch", "component_destroyed", "core_critical", "core_destroyed",
		"impact_composite", "impact_concrete", "impact_electronic", "impact_generic", "impact_glass", "impact_metal",
		"kinetic_fire", "machine_failure", "mission_fail", "mission_success", "objective_complete", "reload_ready",
		"secondary_blast", "structure_collapse", "ui_back", "ui_click", "ui_confirm", "weapon_switch"]
const BASELINE_MUSIC := ["helix_prep", "helix_gameplay", "helix_combat", "helix_critical_layer", "victory_mission",
		"defeat_mission", "legacy_bed", "menu", "cinematic"]
const BASELINE_AMBIENCE := ["helix_server_hall", "helix_core", "helix_cooling"]


func test_catalog_is_valid_and_every_file_resolves() -> void:
	var catalog := AudioCatalog.load_from_file()
	assert_true(catalog.is_valid(), ", ".join(catalog.errors))
	for id: String in catalog.sounds:
		var spec := catalog.get_sound(id)
		assert_true(PackedStringArray(AudioCatalog.PROCEDURAL).has(spec.fallback), "%s has a procedural fallback" % id)
		for path in spec.files:
			assert_true(ResourceLoader.exists(path), "%s file %s exists" % [id, path])
	for cue: AudioCatalog.MusicCue in catalog.music.values() + catalog.ambience.values():
		assert_false(cue.file.is_empty(), "cue %s names a file" % cue.id)
		assert_true(ResourceLoader.exists(cue.file), "cue %s file %s exists" % [cue.id, cue.file])


func test_each_chapter_has_a_complete_plan() -> void:
	var catalog := AudioCatalog.load_from_file()
	assert_eq(catalog.chapters.size(), 5, "five chapter plans")
	for number in range(1, 6):
		var plan := catalog.chapter_plan(number)
		var theme: String = AudioCatalog.CHAPTER_THEMES[number - 1]
		assert_false(plan.is_empty(), "chapter %d (%s) has a plan" % [number, theme])
		assert_eq(plan.intensity.size(), 3, "%s: preparation, tension, combat" % theme)
		for key: String in ["critical_layer", "victory", "defeat", "ambience", "theme", "boss"]:
			assert_false(str(plan[key]).is_empty(), "%s plan has %s" % [theme, key])
		for cue_id: String in plan.intensity + [plan.critical_layer, plan.victory, plan.defeat, plan.theme, plan.boss]:
			assert_true(catalog.get_cue(cue_id) != null, "%s cue %s" % [theme, cue_id])
		assert_true(catalog.get_ambience(plan.ambience) != null, "%s ambience %s" % [theme, plan.ambience])
		assert_eq(catalog.chapter_plan(theme), plan, "lookup by theme name matches the number")
	assert_true(catalog.chapter_plan(0).is_empty() and catalog.chapter_plan(6).is_empty(), "out-of-range chapters have no plan")


func test_chapters_have_distinct_beds_and_music() -> void:
	var catalog := AudioCatalog.load_from_file()
	var beds := {}
	var combat := {}
	for number in range(1, 6):
		var plan := catalog.chapter_plan(number)
		beds[plan.ambience] = true
		combat[catalog.get_cue(plan.intensity[2]).file] = true
	assert_eq(beds.size(), 5, "each chapter has its own ambience bed")
	assert_eq(combat.size(), 5, "each chapter has its own combat track")


func test_mission_without_a_plan_gets_its_chapter_plan() -> void:
	var catalog := AudioCatalog.load_from_file()
	assert_eq(catalog.plan_for("helix_01", 1), catalog.mission_plan("helix_01"), "a mission plan wins")
	assert_eq(catalog.plan_for("helix_02", 1), catalog.chapter_plan(1))
	assert_eq(catalog.plan_for("vita_03", 2), catalog.chapter_plan(2))
	assert_eq(catalog.plan_for("nova_grid_20", 3), catalog.chapter_plan(3))
	assert_eq(catalog.plan_for("civitas_07", 4), catalog.chapter_plan(4))
	assert_eq(catalog.plan_for("meridian_20", 5), catalog.chapter_plan(5))
	assert_true(catalog.plan_for("unknown_mission", 0).is_empty(), "no plan and no chapter keeps the caller's fallback")
	assert_true(catalog.plan_for("unknown_mission", 9).is_empty(), "unknown chapter keeps the caller's fallback")


func test_mission_plan_overrides_chapter_plan() -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(AudioCatalog.DEFAULT_PATH))
	data.missions["vita_01"] = {"intensity": ["helix_prep"], "ambience": "helix_core"}
	var catalog := AudioCatalog.from_json_text(JSON.stringify(data))
	assert_true(catalog.is_valid(), ", ".join(catalog.errors))
	assert_eq(catalog.plan_for("vita_01", 2).ambience, "helix_core")
	assert_eq(catalog.plan_for("vita_02", 2).ambience, "vita_bioreactor")


func test_invalid_chapter_plans_are_reported() -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(AudioCatalog.DEFAULT_PATH))
	data.chapters["atlantis"] = {"intensity": []}
	data.chapters.vita = {"intensity": ["no_such_cue"]}
	var catalog := AudioCatalog.from_json_text(JSON.stringify(data))
	assert_false(catalog.is_valid(), "unknown theme and unknown cue are errors")
	assert_false(catalog.chapters.has("atlantis"))


func test_baseline_ids_unchanged() -> void:
	var catalog := AudioCatalog.load_from_file()
	for id in BASELINE_SOUNDS:
		assert_true(catalog.has_sound(id), "baseline sound %s" % id)
	for id in BASELINE_MUSIC:
		assert_true(catalog.get_cue(id) != null, "baseline music %s" % id)
	for id in BASELINE_AMBIENCE:
		assert_true(catalog.get_ambience(id) != null, "baseline ambience %s" % id)
	assert_eq(catalog.mission_plan("helix_01").ambience, "helix_server_hall")
	assert_eq(catalog.mission_plan("helix_01").intensity, ["helix_prep", "helix_gameplay", "helix_combat"])
	assert_eq(catalog.get_cue("helix_gameplay").file, "res://assets/audio/music/helix/hlx_mus_gameplay_tension.ogg")
