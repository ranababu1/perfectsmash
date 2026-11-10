# Manifest fragments

One JSON file per production stream: `<stream>.json` = `{"stream": "<name>", "updated": "YYYY-MM-DD", "entries": [ ... ]}`.
Entry schema and field meanings: `assets/docs/ASSET_CONTRACT.md` section 17. Only list files that exist.
The integration stream merges all fragments into `assets/asset_manifest.json` with
`python3 assets/tools/validate_asset_manifest.py --merge`. Do not edit `asset_manifest.json` directly.
