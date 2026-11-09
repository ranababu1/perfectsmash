class_name StructuralDependencySystem
extends RefCounted
## Explicit structural relationships between components: which pieces rest on which supports.
## Deliberately not a structural solver. A level declares the load path; this system answers
## "what loses its support when X fails?", including cascades, in a deterministic order.
##
## A component with no supports is anchored (it stands on the ground or a static structure).
## By default a component needs all its supports; `min_supports` lets a redundant design stay up
## with fewer (e.g. a deck on three legs that only needs two). A component "fails" when it is
## destroyed or released; released components are handed to physics by the caller, and they no
## longer hold anything up, so their own dependents are evaluated next.

var errors := PackedStringArray()

var _order: Array[String] = []
var _supports := {}
var _min_supports := {}
var _dependents := {}
var _failed := {}


## Builds a system from data entries: {id, supports: [ids], min_supports?: int}. Check
## `errors` (via is_valid) before use.
static func from_entries(entries: Array) -> StructuralDependencySystem:
	var system := StructuralDependencySystem.new()
	for entry: Variant in entries:
		if not entry is Dictionary or not entry.get("id") is String or entry.id.is_empty():
			system.errors.append("structure entry needs a string 'id'")
			continue
		var supports: Array[String] = []
		var raw_supports: Variant = entry.get("supports", [])
		if raw_supports is Array and raw_supports.all(func(s: Variant) -> bool: return s is String):
			supports.assign(raw_supports)
		else:
			system.errors.append("'%s': supports must be an array of ids" % entry.id)
		var minimum: Variant = entry.get("min_supports", -1)
		system.add_component(entry.id, supports, int(minimum) if (minimum is int or minimum is float) else -1)
	system.errors.append_array(system.validate())
	return system


## Registers a component. `min_supports` < 0 means "needs every listed support".
func add_component(id: String, supports: Array[String] = [], min_supports: int = -1) -> void:
	if _supports.has(id):
		errors.append("duplicate component '%s'" % id)
		return
	_order.append(id)
	_supports[id] = supports.duplicate()
	_min_supports[id] = supports.size() if min_supports < 0 else min_supports
	if not _dependents.has(id):
		_dependents[id] = []


## Checks references, ranges and cycles. Returns the problems found (empty when valid).
func validate() -> PackedStringArray:
	var problems := PackedStringArray()
	for id in _order:
		var supports: Array = _supports[id]
		var seen := {}
		for support: String in supports:
			if support == id:
				problems.append("'%s' cannot support itself" % id)
			elif not _supports.has(support):
				problems.append("'%s' rests on unknown component '%s'" % [id, support])
			elif seen.has(support):
				problems.append("'%s' lists support '%s' twice" % [id, support])
			seen[support] = true
		var minimum: int = _min_supports[id]
		if minimum < 0 or minimum > supports.size() or (supports.size() > 0 and minimum == 0):
			problems.append("'%s': min_supports %d is invalid for %d supports" % [id, minimum, supports.size()])
	if problems.is_empty():
		_rebuild_dependents()
		var cycle := _find_cycle()
		if not cycle.is_empty():
			problems.append("support cycle: %s" % " -> ".join(cycle))
	return problems


func is_valid() -> bool:
	return errors.is_empty()


func has_component(id: String) -> bool:
	return _supports.has(id)


func supports_of(id: String) -> Array:
	return _supports.get(id, []).duplicate()


func dependents_of(id: String) -> Array:
	return _dependents.get(id, []).duplicate()


func is_anchored(id: String) -> bool:
	return _supports.has(id) and (_supports[id] as Array).is_empty()


func is_failed(id: String) -> bool:
	return _failed.has(id)


func intact_support_count(id: String) -> int:
	var count := 0
	for support: String in _supports.get(id, []):
		if not _failed.has(support):
			count += 1
	return count


## True while the component still has enough intact supports (anchored pieces always do).
func is_supported(id: String) -> bool:
	return _supports.has(id) and intact_support_count(id) >= int(_min_supports[id])


## Marks `id` as failed (destroyed or released) and returns every component that loses its
## required support as a result, in cascade order. Unknown or already-failed ids return [].
func fail(id: String) -> Array[String]:
	var released: Array[String] = []
	if not _supports.has(id):
		push_warning("StructuralDependencySystem: fail() on unknown component '%s'" % id)
		return released
	if _failed.has(id):
		return released
	_failed[id] = true
	var queue: Array[String] = [id]
	while not queue.is_empty():
		var current: String = queue.pop_front()
		for dependent: String in _dependents.get(current, []):
			if _failed.has(dependent) or is_supported(dependent):
				continue
			_failed[dependent] = true
			released.append(dependent)
			queue.append(dependent)
	return released


func reset() -> void:
	_failed.clear()


func _rebuild_dependents() -> void:
	_dependents.clear()
	for id in _order:
		_dependents[id] = []
	# Insertion order keeps cascades deterministic.
	for id in _order:
		for support: String in _supports[id]:
			(_dependents[support] as Array).append(id)


## Depth-first search over "rests on" edges; returns the ids forming a cycle, or [].
func _find_cycle() -> Array[String]:
	var state := {}  # id -> 1 visiting, 2 done
	var path: Array[String] = []
	for id in _order:
		var cycle := _visit(id, state, path)
		if not cycle.is_empty():
			return cycle
	return []


func _visit(id: String, state: Dictionary, path: Array[String]) -> Array[String]:
	if state.get(id, 0) == 2:
		return []
	if state.get(id, 0) == 1:
		var start := path.find(id)
		var cycle: Array[String] = path.slice(start)
		cycle.append(id)
		return cycle
	state[id] = 1
	path.append(id)
	for support: String in _supports[id]:
		var cycle := _visit(support, state, path)
		if not cycle.is_empty():
			return cycle
	path.pop_back()
	state[id] = 2
	return []
