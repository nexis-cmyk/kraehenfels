#!/usr/bin/env python3
"""Fill an AltStore source template for a concrete GitHub release."""

from __future__ import annotations

import argparse
import hashlib
import json
import plistlib
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def read_bundle_info(ipa: Path) -> dict:
    """Read the single app Info.plist from an IPA and reject ambiguous packages."""
    with zipfile.ZipFile(ipa) as archive:
        plist_paths = [
            name
            for name in archive.namelist()
            if name.startswith("Payload/")
            and name.endswith(".app/Info.plist")
            and name.count("/") == 2
        ]
        if len(plist_paths) != 1:
            raise ValueError(
                f"Expected exactly one Payload/*.app/Info.plist, found {len(plist_paths)}."
            )
        return plistlib.loads(archive.read(plist_paths[0]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="GitHub owner/repository")
    parser.add_argument("--tag", required=True, help="Release tag, with or without a leading v")
    parser.add_argument("--ipa", type=Path, required=True)
    parser.add_argument("--template", type=Path, default=Path("altstore/source.json"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--download-url",
        help="Stable IPA URL. Defaults to the repository's GitHub Pages mirror.",
    )
    args = parser.parse_args()

    data = json.loads(args.template.read_text(encoding="utf-8"))
    if not isinstance(data.get("apps"), list) or not data["apps"]:
        raise ValueError("AltStore template must contain at least one app.")
    app = data["apps"][0]
    if not isinstance(app, dict):
        raise ValueError("AltStore template app entry must be an object.")

    ipa_bytes = args.ipa.read_bytes()
    info_plist = read_bundle_info(args.ipa)
    version = str(info_plist["CFBundleShortVersionString"])
    build_version = str(info_plist["CFBundleVersion"])
    bundle_identifier = str(info_plist["CFBundleIdentifier"])
    expected_bundle_identifier = str(app.get("bundleIdentifier", ""))
    if bundle_identifier != expected_bundle_identifier:
        raise ValueError(
            f"IPA bundle ID {bundle_identifier} does not match template {expected_bundle_identifier}."
        )
    release_version = args.tag.removeprefix("v")
    app_version = release_version.split("-", 1)[0]
    if version != app_version:
        raise ValueError(
            f"IPA version {version} does not match release tag {release_version}."
        )
    owner, repository = args.repo.split("/", 1)
    release_url = args.download_url or (
        f"https://{owner}.github.io/{repository}/Kraehenfels.ipa"
    )
    raw_root = f"https://raw.githubusercontent.com/{args.repo}/main"
    app["version"] = version
    app["buildVersion"] = build_version
    app["versionDate"] = datetime.now(timezone.utc).date().isoformat()
    app["downloadURL"] = release_url
    app["versionDescription"] = (
        f"Release Candidate {release_version}"
        if "-" in release_version
        else f"Release {release_version}"
    )
    app["iconURL"] = f"{raw_root}/altstore/icon.png"
    app["size"] = len(ipa_bytes)
    app["sha256"] = hashlib.sha256(ipa_bytes).hexdigest()
    app["versions"] = [
        {
            "version": version,
            "buildVersion": build_version,
            "date": app["versionDate"],
            "localizedDescription": app["versionDescription"],
            "downloadURL": release_url,
            "size": len(ipa_bytes),
            "sha256": app["sha256"],
        }
    ]
    data["iconURL"] = f"{raw_root}/altstore/icon.png"
    data["website"] = f"https://github.com/{args.repo}"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output} for {args.repo} v{version}")


if __name__ == "__main__":
    main()
