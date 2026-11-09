class_name ViewMapping
extends RefCounted
## Converts between the 2D physics plane (px, y down, ground at ground_y) and the 3D presentation
## (metres, y up, ground at 0). The physics plane is the z = 0 plane in 3D. 100 px = 1 m.

const PX_PER_METRE := 100.0


static func to_3d(point: Vector2, ground_y: float, z: float = 0.0) -> Vector3:
	return Vector3(point.x / PX_PER_METRE, (ground_y - point.y) / PX_PER_METRE, z)


static func to_2d(point: Vector3, ground_y: float) -> Vector2:
	return Vector2(point.x * PX_PER_METRE, ground_y - point.y * PX_PER_METRE)


static func size_to_3d(size: Vector2, depth_m: float) -> Vector3:
	return Vector3(size.x / PX_PER_METRE, size.y / PX_PER_METRE, depth_m)


## A 2D rotation (radians, clockwise on screen because y is down) as a 3D rotation about z.
static func rotation_to_3d(rotation: float) -> Vector3:
	return Vector3(0.0, 0.0, -rotation)


## A 2D direction as an angle in the 3D xy plane (counter-clockwise from +x).
static func direction_angle(direction: Vector2) -> float:
	return atan2(-direction.y, direction.x)
