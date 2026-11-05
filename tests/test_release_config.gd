extends TestCase
## Release configuration guards (instructions §7): one version, one package id, only the permissions
## the game needs, icons that exist, and no signing secrets in the committed presets.

const PRESETS := "res://export_presets.cfg"
const PACKAGE := "dev.imrn.perfectsmash"
## Vibration is the only Android permission the game uses (haptics on hits and wins).
const ALLOWED_PERMISSIONS := ["permissions/vibrate"]


func _presets() -> ConfigFile:
	var cfg := ConfigFile.new()
	var err := cfg.load(PRESETS)
	assert_eq(err, OK, "export_presets.cfg loads")
	return cfg


func _android_option_sections(cfg: ConfigFile) -> Array[String]:
	var list: Array[String] = []
	for section in cfg.get_sections():
		if section.ends_with(".options") and cfg.get_value(section.trim_suffix(".options"), "platform", "") == "Android":
			list.append(section)
	return list


func test_presets_share_one_version_and_package() -> void:
	var cfg := _presets()
	var sections := _android_option_sections(cfg)
	assert_true(sections.size() >= 2, "debug and release presets exist")
	var codes := {}
	for s in sections:
		codes[int(cfg.get_value(s, "version/code", 0))] = true
		# Empty name means Godot uses application/config/version, the single version-name source.
		assert_eq(str(cfg.get_value(s, "version/name", "x")), "", "%s takes its version name from project.godot" % s)
		assert_eq(str(cfg.get_value(s, "package/unique_name", "")), PACKAGE, "%s package id" % s)
	assert_eq(codes.size(), 1, "every Android preset uses the same version code")
	assert_true(int(codes.keys()[0]) >= 1, "version code is positive")
	var version := str(ProjectSettings.get_setting("application/config/version", ""))
	assert_true(version.split(".").size() == 3, "project version is MAJOR.MINOR.PATCH: %s" % version)


func test_no_secrets_and_minimal_permissions() -> void:
	var cfg := _presets()
	for s in _android_option_sections(cfg):
		for key in ["keystore/release", "keystore/release_user", "keystore/release_password", "keystore/debug_password"]:
			assert_eq(str(cfg.get_value(s, key, "")), "", "%s %s must stay empty (use GODOT_ANDROID_KEYSTORE_* env vars)" % [s, key])
		for key in cfg.get_section_keys(s):
			if key.begins_with("permissions/") and cfg.get_value(s, key) == true:
				assert_true(ALLOWED_PERMISSIONS.has(key), "%s requests unexpected %s" % [s, key])
			if key == "permissions/custom_permissions":
				assert_eq(Array(cfg.get_value(s, key)), [], "%s has custom permissions" % s)


func test_launcher_icons_exist() -> void:
	var cfg := _presets()
	for s in _android_option_sections(cfg):
		for key in cfg.get_section_keys(s):
			if key.begins_with("launcher_icons/"):
				var path := str(cfg.get_value(s, key))
				assert_true(path != "" and FileAccess.file_exists(path), "%s %s -> %s exists" % [s, key, path])


func test_release_presets_target_play_architectures() -> void:
	var cfg := _presets()
	for s in _android_option_sections(cfg):
		var preset := s.trim_suffix(".options")
		if str(cfg.get_value(preset, "name")).begins_with("Android Release"):
			assert_true(cfg.get_value(s, "architectures/arm64-v8a"), "%s ships 64-bit ARM (Play requirement)" % preset)
			assert_true(str(cfg.get_value(preset, "exclude_filter")).contains("tests/*"), "%s leaves tests out" % preset)


## Voice narration on Android 11+ needs the TTS <queries> manifest entry, which addons/android_tts adds
## only in Gradle builds. Release builds must therefore use Gradle and the plugin must be enabled.
func test_release_builds_can_narrate() -> void:
	assert_true(ProjectSettings.get_setting("audio/general/text_to_speech", false), "text-to-speech enabled")
	var plugins: PackedStringArray = ProjectSettings.get_setting("editor_plugins/enabled", PackedStringArray())
	assert_true(plugins.has("res://addons/android_tts/plugin.cfg"), "TTS query export plugin enabled")
	var cfg := _presets()
	for s in _android_option_sections(cfg):
		var preset := s.trim_suffix(".options")
		if str(cfg.get_value(preset, "name")).begins_with("Android Release"):
			assert_true(cfg.get_value(s, "gradle_build/use_gradle_build"), "%s uses Gradle (manifest plugin applies)" % preset)
		assert_true(str(cfg.get_value(preset, "exclude_filter")).contains("addons/*"), "%s leaves editor plugins out" % preset)
