#!/usr/bin/env python3
"""Validate an AltStore source feed and, optionally, its IPA payload."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import plistlib
import sys
import zipfile
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")


def error(errors: list[str], message: str) -> None:
    errors.append(message)


def require_string(container: dict, key: str, location: str, errors: list[str]) -> str | None:
    value = container.get(key)
    if not isinstance(value, str) or not value.strip():
        error(errors, f"{location}.{key} must be a non-empty string")
        return None
    return value


def validate_url(value: str | None, location: str, errors: list[str], suffix: str | None = None) -> None:
    if value is None:
        return
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        error(errors, f"{location} must be an HTTPS URL")
    if suffix and not parsed.path.lower().endswith(suffix):
        error(errors, f"{location} must point to a {suffix} file")


def validate_hash_and_size(record: dict, location: str, errors: list[str]) -> None:
    size = record.get("size")
    if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
        error(errors, f"{location}.size must be a positive integer")
    digest = record.get("sha256")
    if not isinstance(digest, str) or not HEX_SHA256.fullmatch(digest):
        error(errors, f"{location}.sha256 must be a lowercase SHA-256 digest")


def validate_version_record(record: object, location: str, errors: list[str]) -> dict | None:
    if not isinstance(record, dict):
        error(errors, f"{location} must be an object")
        return None
    version = require_string(record, "version", location, errors)
    if version and not VERSION.fullmatch(version):
        error(errors, f"{location}.version is not a valid semantic version: {version}")
    build_version = require_string(record, "buildVersion", location, errors)
    if build_version and not build_version.isdigit():
        error(errors, f"{location}.buildVersion must contain only digits")
    description = require_string(record, "localizedDescription", location, errors)
    download_url = require_string(record, "downloadURL", location, errors)
    validate_url(download_url, f"{location}.downloadURL", errors, ".ipa")
    record_date = require_string(record, "date", location, errors)
    if record_date:
        try:
            date.fromisoformat(record_date)
        except ValueError:
            error(errors, f"{location}.date must be an ISO-8601 date")
    validate_hash_and_size(record, location, errors)
    return {
        "version": version,
        "buildVersion": build_version,
        "localizedDescription": description,
        "downloadURL": download_url,
        "date": record_date,
        "size": record.get("size"),
        "sha256": record.get("sha256"),
    }


def validate_source(path: Path) -> tuple[dict | None, list[str]]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"Could not read {path}: {exc}"]

    if not isinstance(data, dict):
        return None, ["Feed root must be an object"]
    for key in ("name", "identifier", "subtitle", "description", "iconURL", "website"):
        require_string(data, key, "feed", errors)
    validate_url(data.get("iconURL"), "feed.iconURL", errors, ".png")
    validate_url(data.get("website"), "feed.website", errors)

    apps = data.get("apps")
    if not isinstance(apps, list) or not apps:
        error(errors, "feed.apps must be a non-empty array")
        return data, errors

    for index, app in enumerate(apps):
        location = f"apps[{index}]"
        if not isinstance(app, dict):
            error(errors, f"{location} must be an object")
            continue
        for key in ("name", "bundleIdentifier", "developerName", "subtitle", "version", "buildVersion", "versionDate", "versionDescription", "downloadURL", "localizedDescription", "iconURL", "tintColor"):
            require_string(app, key, location, errors)
        version = app.get("version")
        if isinstance(version, str) and not VERSION.fullmatch(version):
            error(errors, f"{location}.version is not a valid semantic version: {version}")
        build_version = app.get("buildVersion")
        if isinstance(build_version, str) and not build_version.isdigit():
            error(errors, f"{location}.buildVersion must contain only digits")
        app_date = app.get("versionDate")
        if isinstance(app_date, str):
            try:
                date.fromisoformat(app_date)
            except ValueError:
                error(errors, f"{location}.versionDate must be an ISO-8601 date")
        download_url = app.get("downloadURL")
        validate_url(download_url, f"{location}.downloadURL", errors, ".ipa")
        validate_url(app.get("iconURL"), f"{location}.iconURL", errors, ".png")
        validate_hash_and_size(app, location, errors)

        permissions = app.get("appPermissions")
        if not isinstance(permissions, dict):
            error(errors, f"{location}.appPermissions must be an object")
        elif not isinstance(permissions.get("entitlements"), list) or not isinstance(permissions.get("privacy"), dict):
            error(errors, f"{location}.appPermissions must contain entitlements[] and privacy{{}}")

        versions = app.get("versions")
        if not isinstance(versions, list) or not versions:
            error(errors, f"{location}.versions must be a non-empty array")
            continue
        normalized_app = {
            "version": app.get("version"),
            "buildVersion": app.get("buildVersion"),
            "localizedDescription": app.get("versionDescription"),
            "downloadURL": app.get("downloadURL"),
            "date": app.get("versionDate"),
            "size": app.get("size"),
            "sha256": app.get("sha256"),
        }
        for version_index, record in enumerate(versions):
            normalized_record = validate_version_record(record, f"{location}.versions[{version_index}]", errors)
            if normalized_record and version_index == 0:
                for key, expected in normalized_app.items():
                    if normalized_record.get(key) != expected:
                        error(
                            errors,
                            f"{location}.versions[0].{key} must match the app-level value",
                        )

    return data, errors


def read_ipa_metadata(path: Path) -> tuple[dict, bytes]:
    ipa_bytes = path.read_bytes()
    with zipfile.ZipFile(path) as archive:
        plist_paths = [
            name
            for name in archive.namelist()
            if name.startswith("Payload/") and name.endswith(".app/Info.plist") and name.count("/") == 2
        ]
        if len(plist_paths) != 1:
            raise ValueError(f"expected exactly one Payload/*.app/Info.plist, found {len(plist_paths)}")
        metadata = plistlib.loads(archive.read(plist_paths[0]))
    return metadata, ipa_bytes


def validate_ipa(feed: dict, ipa_path: Path, errors: list[str]) -> None:
    try:
        metadata, ipa_bytes = read_ipa_metadata(ipa_path)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, plistlib.InvalidFileException) as exc:
        error(errors, f"Could not inspect IPA {ipa_path}: {exc}")
        return

    if not feed or not isinstance(feed.get("apps"), list) or not feed["apps"]:
        return
    app = feed["apps"][0]
    expected = {
        "CFBundleIdentifier": app.get("bundleIdentifier"),
        "CFBundleShortVersionString": app.get("version"),
        "CFBundleVersion": app.get("buildVersion"),
    }
    for key, value in expected.items():
        actual = str(metadata.get(key, ""))
        if actual != str(value):
            error(errors, f"IPA {key}={actual!r} does not match feed value {value!r}")
    actual_size = len(ipa_bytes)
    actual_hash = hashlib.sha256(ipa_bytes).hexdigest()
    if actual_size != app.get("size"):
        error(errors, f"IPA size {actual_size} does not match feed size {app.get('size')}")
    if actual_hash != app.get("sha256"):
        error(errors, f"IPA SHA-256 {actual_hash} does not match feed sha256 {app.get('sha256')}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("feed", type=Path, help="AltStore source JSON")
    parser.add_argument("--ipa", type=Path, help="Optional IPA to compare with the feed")
    args = parser.parse_args()

    feed, errors = validate_source(args.feed)
    if args.ipa:
        validate_ipa(feed or {}, args.ipa, errors)
    if errors:
        for message in errors:
            print(f"ERROR: {message}", file=sys.stderr)
        return 1
    print(f"AltStore feed valid: {args.feed}")
    if args.ipa:
        print(f"IPA matches feed: {args.ipa}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
