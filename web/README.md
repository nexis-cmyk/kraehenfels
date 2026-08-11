# Krähenfels Web-Test

Die Web-Testversion ist eine offlinefähige Vorschau des Spielleiter-Leitstands. Sie nutzt dieselben Szenen, Handouts, NPCs und Audio-Dateien wie die iPhone-App.

## Lokal testen

Im Projektordner einmal die Web-Dateien aktualisieren:

```powershell
python tools/build_web_preview.py
```

Danach einen lokalen Server starten:

```powershell
python -m http.server 4173 --directory web
```

Im Browser `http://localhost:4173` öffnen. Der Browser muss dafür geöffnet bleiben. Beim ersten Ton startet der Browser die Audiowiedergabe. Nutze zuerst **Audio testen**. Wenn das nicht hörbar ist, prüfe Windows-Lautstärke und die aktuell gewählte Audioausgabe.

## Was geprüft werden kann

- Szenenwechsel, Vorlesetexte, Hinweise und Checklisten
- NPCs inklusive der Handouts, die sie geben können
- Spoiler-Schalter und Spielerhandouts
- Szenen-Presets, einzelne Effekte und Lautstärkemischung
- Stopp-Taste, Fortschritt und Speicherung im Browser
- drei Reisende, allgemeine Sessionnotiz und eine eigene Notiz pro Szene

Die Browser-Version ist ein Testleitstand. Die spätere Installation auf dem iPhone erfolgt weiterhin über die signierte IPA in AltStore.
