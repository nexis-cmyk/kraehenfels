# Handoff 26

## Arbeitsstand

Der Leitstand ist nach dem nächsten Release-Audit technisch gehärtet. Die Story und der geführte Ablauf bleiben unverändert: manipulierte Kutschfahrt, Schwarzer Keiler, Kirche, Schmiede, Waldspur, Archiv, Alte Eiche und drei Enden.

## Neue Abschlussänderungen

- Der native Bundle-Check erlaubt nur die 20 im Manifest referenzierten Cues plus den Audio-Selbsttest. 76 alte Audio-Dateien und sieben ungenutzte Graphic-Novel-Assets wurden aus dem iOS-Ressourcenordner entfernt; Generatoren behalten ihre Quellen unter `audio/` und `print/`.
- `process_audio_v5.py` verarbeitet die zwölf durch V6 ersetzten V5-Dateien weiterhin für Archiv und QA, kopiert sie aber nicht mehr in den nativen Bundle-Ordner.
- `generate_audio_v6.py` spiegelt die acht geprüften V5-Baseline-Cues explizit, bevor die zwölf V6-Ersatzdateien erzeugt werden. Ein sauberer Checkout kann dadurch kein zufälliges Altfile als Bundleinhalt verwenden.
- Der globale Audio-STOP setzt jetzt auch die Vorlese-Absenkung zurück. Der Vorlese-Dialog behandelt Swipe-to-dismiss und interaktives Zurück als Abbruch und stellt die normale Mischung wieder her.
- Die kanonische Native-Version ist `3.3.0`; die sichtbare Start-PDF-Version ist damit nicht mehr auf `3.3.0-rc1` festgenagelt.

## Nachweise

```powershell
python tools/validate_project.py
python tools/validate_audio_v6.py
python tools/validate_guided_flow.py
python -m compileall -q tools
git diff --check
```

Zusätzlich wurden alle 14 PDF-Ausgaben mit Poppler gerendert und visuell geprüft. Der lokale Bundle-Audit meldet 21 Audio-Dateien, 20 Art-Dateien und keine unreferenzierten nativen Ressourcen.

## Release-Hinweis

Die Änderungen benötigen vor der Nutzung in AltStore einen neuen iOS-Build. `v3.3.0-rc3` mit Build `4` ist veröffentlicht. Der Pages-Workflow hatte zunächst eine veraltete 100-MB-Mindestprüfung und wurde auf eine realistische 50-MB-Sanity-Prüfung korrigiert. Der Mirror liefert nun dieselbe 82.703.807-Byte-IPA mit SHA-256 `a6cb0ed6537c33ad64f06cffb684938ec04ec7e2258fb93819491052f6031586` wie das GitHub-Release. Der bisherige RC2 bleibt als Fallback installierbar.

## Offener physischer Test

Auf dem echten iPhone einmal den Audio-Check über Lautsprecher und Box durchführen, S01/S02 mit der Vorlese-Bestätigung prüfen und eine komplette Runde mit drei Spielern spielen. Das kann CI nicht ersetzen.
