class_name Narrator
extends Node
## Speaks dialogue lines with the device's built-in text-to-speech engine, giving each speaker its
## own pitch. Uses no network and no permission; when the device has no TTS voice (or narration is
## off) it does nothing and the UI simply shows the text. Text is always displayed regardless.

## Emitted when the current line has finished speaking (or straight away if nothing is spoken).
signal line_finished

## Speech rate relative to the engine's default; a touch slower than normal suits radio chatter.
const RATE := 0.95
const VOLUME := 80

var enabled := true
var _voice := ""
var _available := false
var _next_id := 1
var _speaking_id := -1


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	if not ProjectSettings.get_setting("audio/general/text_to_speech", false):
		return
	var voices := DisplayServer.tts_get_voices_for_language("en")
	if voices.is_empty():
		return
	_voice = voices[0]
	_available = true
	DisplayServer.tts_set_utterance_callback(DisplayServer.TTS_UTTERANCE_ENDED, _on_utterance_done)
	DisplayServer.tts_set_utterance_callback(DisplayServer.TTS_UTTERANCE_CANCELED, _on_utterance_done)


## True when the device offers a text-to-speech voice at all.
func is_available() -> bool:
	return _available


## True when lines will actually be spoken aloud.
func is_speaking_enabled() -> bool:
	return enabled and _available


## Speaks one line. Returns false when narration is off or unavailable (the caller paces by text).
func speak(text: String, pitch: float = 1.0) -> bool:
	stop()
	if not is_speaking_enabled():
		return false
	_speaking_id = _next_id
	_next_id += 1
	# Strip quote marks and ellipses that some engines read out literally.
	var spoken := text.replace("'", "").replace("...", ", ")
	DisplayServer.tts_speak(spoken, _voice, VOLUME, clampf(pitch, 0.5, 2.0), RATE, _speaking_id)
	return true


func stop() -> void:
	if _available and _speaking_id >= 0:
		_speaking_id = -1
		DisplayServer.tts_stop()


func _on_utterance_done(id: int) -> void:
	if id == _speaking_id:
		_speaking_id = -1
		# Some platforms report from a TTS thread; hop to the main loop before touching the UI.
		line_finished.emit.call_deferred()
