# Handoff 36 – AltStore source format fix

## Status

- The `v4.1.0` release remains published and the IPA is unchanged.
- The release asset `source.generated.json` was replaced in place at the same URL:
  `https://github.com/nexis-cmyk/kraehenfels/releases/download/v4.1.0/source.generated.json`
- The corrected feed was downloaded again and parsed successfully.

## Fix

The feed generator now emits the current AltStore `versions` array in addition to the legacy flat version fields. The empty privacy permissions value is an object (`{}`), matching the AltStore Classic source schema instead of an array.

## Future releases

`tools/update_altstore_feed.py` applies the same format automatically when the macOS release workflow creates a new `source.generated.json`. Keep `altstore/source.json` aligned with the latest release metadata when updating the documented feed.
