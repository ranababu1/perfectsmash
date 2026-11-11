"""Regenerates the export filters and the release preset in export_presets.cfg (local file, gitignored).

Run after `godot_console --headless -s tools/release/export_manifest.gd`:
    python tools/release/make_export_presets.py [--version-name 1.0.0-rc1] [--version-code 2]

- Every preset's exclude_filter = tooling folders + every asset file the game does not use
  (docs/release/shipped-assets.json "excluded"), so retired / unverified files (e.g.
  assets/audio/music/gameplay_bed.ogg) can never ship.
- preset "Android Debug" (APK, signed with the editor's debug keystore) keeps its options.
- preset "Android Release AAB" is (re)created from the debug preset: Gradle build, AAB, unsigned
  (package/signed=false). The owner signs it; no keystore is referenced here.
Never writes keystore paths or passwords.
"""
import argparse
import json
import re

ALWAYS_EXCLUDED = ["tests/*", "tools/*", "docs/*", "assets/docs/*", "assets/tools/*", "*.md", "assets/asset_manifest.json",
                   "assets/manifest_parts/*", "android/build/*.md"]
RELEASE_NAME = "Android Release AAB"


def sections(text):
    """[(header, body_lines)] in order."""
    out = []
    for block in re.split(r"(?m)^(?=\[)", text):
        if not block.strip():
            continue
        header, _, body = block.partition("\n")
        out.append([header.strip(), body.rstrip("\n").split("\n") if body.strip() else []])
    return out


def set_key(lines, key, value):
    for i, line in enumerate(lines):
        if line.startswith(key + "="):
            lines[i] = "%s=%s" % (key, value)
            return
    lines.append("%s=%s" % (key, value))


def get_key(lines, key):
    for line in lines:
        if line.startswith(key + "="):
            return line.split("=", 1)[1]
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version-name", default=None)
    parser.add_argument("--version-code", default=None)
    args = parser.parse_args()
    shipped = json.load(open("docs/release/shipped-assets.json", encoding="utf8"))
    excluded = ALWAYS_EXCLUDED + [p.replace("res://", "") for p in shipped["excluded"]]
    exclude_value = '"%s"' % ", ".join(excluded)
    secs = sections(open("export_presets.cfg", encoding="utf8").read())
    # Drop an old release preset (it is rebuilt from the debug preset below).
    names = {}
    for header, body in secs:
        m = re.match(r"\[preset\.(\d+)\]$", header)
        if m:
            names[m.group(1)] = (get_key(body, "name") or "").strip('"')
    drop = [i for i, n in names.items() if n == RELEASE_NAME]
    secs = [s for s in secs if not any(s[0] in ("[preset.%s]" % i, "[preset.%s.options]" % i) for i in drop)]
    debug_index = next(i for i, n in names.items() if n == "Android Debug")
    debug = next(s for s in secs if s[0] == "[preset.%s]" % debug_index)
    debug_options = next(s for s in secs if s[0] == "[preset.%s.options]" % debug_index)
    for header, body in secs:
        if re.match(r"\[preset\.\d+\]$", header):
            set_key(body, "exclude_filter", exclude_value)
        if re.match(r"\[preset\.\d+\.options\]$", header):
            if args.version_name:
                if get_key(body, "version/name") is not None:
                    set_key(body, "version/name", '"%s"' % args.version_name)
                if get_key(body, "application/short_version") is not None:
                    set_key(body, "application/short_version", '"%s"' % args.version_name.split("-")[0])
                if get_key(body, "application/version") is not None:
                    set_key(body, "application/version", '"%s"' % args.version_name)
            if args.version_code and get_key(body, "version/code") is not None:
                set_key(body, "version/code", args.version_code)
    index = str(max(int(i) for i in names if i not in drop) + 1)
    release = list(debug[1])
    set_key(release, "name", '"%s"' % RELEASE_NAME)
    set_key(release, "runnable", "false")
    set_key(release, "export_path", '"build/temporal1-1.0.0-rc1-release-unsigned.aab"')
    release_options = list(debug_options[1])
    set_key(release_options, "gradle_build/use_gradle_build", "true")
    set_key(release_options, "gradle_build/export_format", "1")
    set_key(release_options, "package/signed", "false")
    set_key(release_options, "architectures/x86_64", "false")
    for key in ("keystore/release", "keystore/release_user", "keystore/release_password"):
        set_key(release_options, key, '""')
    secs.append(["[preset.%s]" % index, release])
    secs.append(["[preset.%s.options]" % index, release_options])
    text = "\n\n".join(h + ("\n" + "\n".join(b) if b else "") for h, b in secs) + "\n"
    open("export_presets.cfg", "w", encoding="utf8", newline="\n").write(text)
    print("presets: %s; excluded %d paths" % (", ".join(sorted(set(names.values()) - {RELEASE_NAME}) + [RELEASE_NAME]), len(excluded)))


if __name__ == "__main__":
    main()
