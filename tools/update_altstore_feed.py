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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="GitHub owner/repository")
    parser.add_argument("--tag", required=True, help="Release tag without the leading v")
    parser.add_argument("--ipa", type=Path, required=True)
    parser.add_argument("--template", type=Path, default=Path("altstore/source.json"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--download-url",
        help="Stable IPA URL. Defaults to the repository's GitHub Pages mirror.",
    )
    args = parser.parse_args()

    data = json.loads(args.template.read_text(encoding="utf-8"))
    ipa_bytes = args.ipa.read_bytes()
    with zipfile.ZipFile(args.ipa) as archive:
        info_plist = plistlib.loads(archive.read("Payload/Kraehenfels.app/Info.plist"))
    version = str(info_plist["CFBundleShortVersionString"])
    build_version = str(info_plist["CFBundleVersion"])
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
    app = data["apps"][0]
    app["version"] = version
    app["buildVersion"] = build_version
    app["versionDate"] = datetime.now(timezone.utc).date().isoformat()
    app["downloadURL"] = release_url
    if "-" in release_version:
        app["versionDescription"] = f"Release Candidate {release_version}"
    app["iconURL"] = f"{raw_root}/altstore/icon.png"
    app["size"] = len(ipa_bytes)
    app["sha256"] = hashlib.sha256(ipa_bytes).hexdigest()
    data["iconURL"] = f"{raw_root}/altstore/icon.png"
    data["website"] = f"https://github.com/{args.repo}"
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output} for {args.repo} v{version}")


if __name__ == "__main__":
    main()
