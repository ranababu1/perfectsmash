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
