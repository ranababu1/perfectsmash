@tool
extends EditorPlugin
## Export-time only: adds a <queries> entry for the TTS service to the Android manifest. Since
## Android 11, apps must declare which services they look up; without this the device's
## text-to-speech engine is invisible to the game and voice narration is silently unavailable.
## No permission is added.

var _export_plugin: TtsQueryExport


func _enter_tree() -> void:
	_export_plugin = TtsQueryExport.new()
	add_export_plugin(_export_plugin)


func _exit_tree() -> void:
	remove_export_plugin(_export_plugin)
	_export_plugin = null


class TtsQueryExport extends EditorExportPlugin:
	func _get_name() -> String:
		return "AndroidTtsQuery"

	func _supports_platform(platform: EditorExportPlatform) -> bool:
		return platform is EditorExportPlatformAndroid

	func _get_android_manifest_element_contents(_platform: EditorExportPlatform, _debug: bool) -> String:
		return """
	<queries>
		<intent>
			<action android:name="android.intent.action.TTS_SERVICE" />
		</intent>
	</queries>
"""
