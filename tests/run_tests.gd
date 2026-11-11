extends SceneTree
## Headless test runner. Run from the project root:
##   godot --headless --fixed-fps 60 -s tests/run_tests.gd            (all suites)
##   godot --headless --fixed-fps 60 -s tests/run_tests.gd -- --unit  (skip physics playthroughs)
##   godot --headless --fixed-fps 60 -s tests/run_tests.gd -- --only test_hud  (suites whose path contains the text)
##   godot --fixed-fps 60 -s tests/run_tests.gd                       (windowed: also runs GUI input routing checks)
## --fixed-fps disables real-time sync so physics suites run faster than real time.
## Exit code is 0 only when every test passes.

const UNIT_SUITES := [
	"res://tests/test_rules.gd",
	"res://tests/test_progress.gd",
	"res://tests/test_chapters.gd",
	"res://tests/test_music.gd",
	"res://tests/test_cinematics.gd",
	"res://tests/test_materials.gd",
	"res://tests/test_weapons.gd",
	"res://tests/test_damage.gd",
	"res://tests/test_structure.gd",
	"res://tests/test_mission_definition.gd",
	"res://tests/test_weapon_state.gd",
	"res://tests/test_mission_engine.gd",
	"res://tests/test_scoring.gd",
	"res://tests/test_progression.gd",
	"res://tests/test_audio.gd",
	"res://tests/test_assets.gd",
]
const PHYSICS_SUITES := [
	"res://tests/test_mission_world.gd",
	"res://tests/test_mission_screen.gd",
]


func _initialize() -> void:
	_run.call_deferred()


## Workstream suites live in one level of sub-folders (tests/levels/, tests/ui/, ...) and are
## discovered automatically, so adding a suite never means editing this file. A discovered suite
## that declares `const PHYSICS_SUITE := true` is skipped by `--unit`.
const TESTS_ROOT := "res://tests"


static func discover_suites() -> Array[String]:
	var found: Array[String] = []
	var root := DirAccess.open(TESTS_ROOT)
	if root == null:
		return found
	var folders := Array(root.get_directories())
	folders.sort()
	for folder: String in folders:
		if folder == "output" or folder.begins_with("."):
			continue
		var dir := DirAccess.open(TESTS_ROOT.path_join(folder))
		if dir == null:
			continue
		var files := Array(dir.get_files())
		files.sort()
		for file: String in files:
			if file.begins_with("test_") and file.ends_with(".gd"):
				found.append(TESTS_ROOT.path_join(folder).path_join(file))
	return found


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var unit_only := args.has("--unit")
	# `--only <text>`: run just the suites whose path contains <text> (workstream runs).
	var only := ""
	if args.has("--only") and args.find("--only") + 1 < args.size():
		only = args[args.find("--only") + 1]
	var suites: Array = UNIT_SUITES.duplicate()
	if not unit_only:
		suites.append_array(PHYSICS_SUITES)
	for path in discover_suites():
		var discovered: GDScript = load(path)
		if unit_only and discovered != null and discovered.get_script_constant_map().get("PHYSICS_SUITE", false):
			continue
		suites.append(path)
	if not only.is_empty():
		suites = suites.filter(func(p: String) -> bool: return only in p)
	var passed := 0
	var failed := 0
	var skipped := 0
	var start := Time.get_ticks_msec()
	for path: String in suites:
		var script: GDScript = load(path)
		# A suite with a parse error still loads as a non-null script that cannot be instantiated;
		# count it as a failure rather than silently running zero tests.
		if script == null or not script.can_instantiate():
			printerr("FAIL could not load suite %s" % path)
			failed += 1
			continue
		for method in script.get_script_method_list():
			var method_name: String = method.name
			if not method_name.begins_with("test_"):
				continue
			var suite: TestCase = script.new()
			suite.tree = self
			await suite.call(method_name)
			if suite.failures.is_empty() and not suite.skip_reason.is_empty():
				skipped += 1
				print("  SKIP %s::%s (%s)" % [path.get_file(), method_name, suite.skip_reason])
			elif suite.failures.is_empty():
				passed += 1
				print("  ok   %s::%s" % [path.get_file(), method_name])
			else:
				failed += 1
				printerr("  FAIL %s::%s" % [path.get_file(), method_name])
				for failure in suite.failures:
					printerr("         " + failure)
	print("\n%d passed, %d failed, %d skipped (%.1fs)" % [passed, failed, skipped, (Time.get_ticks_msec() - start) / 1000.0])
	MissionView.release_cached_set()
	quit(1 if failed > 0 else 0)
