extends SceneTree
## Times MissionScreen rebuilds on desktop the way the app root restarts a mission (remove the
## old screen, queue it for deletion, add the new one in the same frame).
##   godot_console --path . --script res://tools/perf/restart_timing.gd

func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var previous: MissionScreen = null
	for i in 6:
		var t0 := Time.get_ticks_usec()
		if previous != null:
			root.remove_child(previous)
			previous.queue_free()
		var screen := MissionScreen.new()
		root.add_child(screen)
		var t1 := Time.get_ticks_usec()
		await process_frame
		var t2 := Time.get_ticks_usec()
		await process_frame
		var t3 := Time.get_ticks_usec()
		print("RESTART_TIMING %d reused=%s ready=%.1fms frame1=%.1fms frame2=%.1fms sets=%d" % [i, screen.view.reused_set, (t1 - t0) / 1000.0, (t2 - t1) / 1000.0, (t3 - t2) / 1000.0, screen.view.set_root.get_child_count()])
		previous = screen
	root.remove_child(previous)
	previous.free()
	MissionView.release_cached_set()
	await process_frame
	quit()
