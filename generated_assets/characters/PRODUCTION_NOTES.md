# Characters: production notes (3d-kits stream)

`characters/shared/opr_chr_operative_a.glb` (`OPR-CHR-OPERATIVE-A`) is built by `destructibles/source/blender/runchar.py`. It is the hooded, faceless operative from SV-01, with a shorter ragged cape, a visor eye slit (cyan emission), armoured limbs and cyan accents. It has 2,806 tris (budget 6,000).

**Quality status:** pending_review. This is a stylised production candidate built procedurally. It reads clearly at game distance and in all poses, but it is not a sculpted hero character. A sculpted or skinned replacement can keep the same node names and clips.

## Rig (node hierarchy, no skin)

    opr_chr_operative_a
      hips
        torso
          head > hood
          arm_weapon (pivot at the right, camera-side shoulder) > forearm_weapon > weapon_socket
          arm_support > forearm_support
        leg_r > shin_r
        leg_l > shin_l

- The model faces +X. `arm_weapon` at rotation 0 aims along +X, and the aim angle is a rotation about +Z, as in OperativeRig.
- Mount a weapon glb on `weapon_socket` with no offset (weapon origin = grip).
- The support arm is a separate chain. If the far hand should follow a code-driven aim, copy a share of the `arm_weapon` rotation to `arm_support`.

## Animations

Clips are node TRS at 30 fps and in place (no root motion). Every node is keyed in every clip, so switching clips never leaves a node in a stale pose.

| Clip | Frames | Loop |
|---|---|---|
| idle | 61 | yes |
| ready | 41 | yes |
| aim_pose | 31 | yes |
| fire_recoil | 13 | no |
| reload | 37 | no |
| weapon_switch | 25 | no |
| victory | 61 | no |
| defeat (kneel) | 49 | no |
| reposition | 25 | yes |

When loaded at runtime with `GLTFDocument`, the root comes back as `<stem>2` because of a scene-root name clash. The file itself has a single root named after the stem.

## Commands

    cd generated_assets/destructibles/source/blender
    TFJ_SAMPLES=32 blender -b --factory-startup --python runchar.py [-- --no-render]
    xvfb-run -a -s "-screen 0 1280x720x24" godot --path <any project> --rendering-driver opengl3 \
      --script generated_assets/destructibles/source/godot/char_check.gd -- out.png <operative.glb> <weapon.glb> aim_pose:0.5 ready:0.3 idle:1.0

`char_check.gd` prints NODES and ANIMS lines and renders the poses with the weapon mounted. The results are in `previews/opr_chr_operative_godot_poses.webp` and `previews/opr_chr_operative_sheet.webp`.

## Rights

This is original procedural work. The scripted Blender code was written by the 3d-kits asset agent (AI-assisted authorship). The form language follows SV-01; no concept pixels are used. Ownership is not legally settled, and nothing is marked commercially cleared.

## Premium uplift pass: operative rebuilt to SV-01 (2026-11-10)

`characters/shared/opr_chr_operative_a.glb` was rebuilt in place. The id, the node names, `weapon_socket` and all nine clips are unchanged.

- **Look.** A dark hooded faceless figure: a deep cloth hood with a peak, a glossy black visor with two angled cyan slits, and a cowl and scarf. A layered tactical suit sits under gunmetal armour: angular two-layer pauldrons, chest chevrons with cyan lines, a back plate and pack, cross straps with a buckle, a belt with four pouches, bracers, gloves with knuckle plates, thigh plates and pouches, knee and shin guards, and boots with soles and toe caps.
- **Cape.** It is shorter than before, ending just above the knee. It is a cloth-like 8 x 6 strip mesh skinned to a small armature, `cape_rig`, parented under `torso`. The bones are `cape_root` plus three chains of three (`cape_0_0` to `cape_2_2`). Every clip keys a sway, plus a lift for `reposition`, `fire_recoil` and `defeat`. Godot imports it as a `Skeleton3D` with the `cape` mesh.
- **Material.** One baked 1024 set (albedo, normal, ORM, emission mask) is embedded in the glb, in the single slot `chr_operative_a`. The zone surfaces (carbon composite suit, rubber cloth, gunmetal plates, glass visor) were baked through one shared unique UV.
- **Size.** 3,516 tris (budget 6,000). The glb is 2.2 MB.
- **Checks.** The Godot 4.7.2 GL Compatibility check loads all nodes, the `Skeleton3D` and the nine animations, and mounts the weapon on `weapon_socket`.
- **Previews.**
  - `previews/opr_chr_operative_godot_poses.webp`: MissionView camera.
  - `previews/opr_chr_operative_showcase.webp`: graded frame with side, three-quarter and front views. Its layout is `environments/showcase/operative_showcase_layout.json`.
  - `previews/opr_chr_operative_sheet.webp`: Cycles, 8 poses.
- **Limits.** The plates are hard-surface boxes with soft bevels, and the cape has no cloth simulation. At close range it reads as a stylised game character, not a sculpted one.
