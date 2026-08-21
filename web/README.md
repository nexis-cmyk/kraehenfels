# Krähenfels Web-Test

Die Web-Testversion ist eine offlinefähige Vorschau des aktuellen Spielleiter-Leitstands für `Krähenfels: Die letzte Kutsche`. Sie startet mit derselben Leitstand-Übersicht wie die native iPad-App und führt von dort in die Szenen. Sie wird aus dem Inhaltsmanifest und den nativen Ressourcen synchronisiert und nutzt dieselben Szenen, Handouts, NPCs, Karten und Audio-Dateien wie die iPad-App.

Die veröffentlichte Testversion liegt nach dem GitHub-Pages-Workflow unter `https://nexis-cmyk.github.io/kraehenfels/`. Falls GitHub Pages im Repository noch nicht aktiv ist, einmal **Settings → Pages → Build and deployment → Source: GitHub Actions → Save** wählen. Beim ersten Öffnen braucht die Seite Internet, danach stehen die bereits geladenen Inhalte offline zur Verfügung.

## Lokal testen

Im Projektordner die Web-Dateien auf den aktuellen Release-Stand bringen:

```powershell
python tools/build_web_preview.py
```

Der Befehl aktualisiert auch die Service-Worker-Cache-Version. Ein anschließendes Neuladen verwirft damit alte Szenen und Sounds aus dem Browser-Cache.

Danach einen lokalen Server starten:

```powershell
python -m http.server 4173 --directory web
```

Im Browser `http://localhost:4173` öffnen. Der Browser muss dafür geöffnet bleiben. Beim ersten Ton startet der Browser die Audiowiedergabe. Nutze zuerst **Audio testen**. Wenn das nicht hörbar ist, prüfe Windows-Lautstärke und die aktuell gewählte Audioausgabe.

Am PC zeigt die Vorschau automatisch den breiten Leitstand mit Szenenleiste links. Auf schmalen Browserfenstern wechselt sie in eine kompakte Ansicht. Wenn nach einem Update eine alte Oberfläche erscheint, die Seite einmal mit `Strg+F5` neu laden; der Versionssuffix der Web-Shell verwirft alte Service-Worker-Dateien.

## Was geprüft werden kann

- Szenenwechsel, Vorlesetexte, Hinweise, Fakten und Checklisten
- NPCs inklusive Zuständen und der Handouts, die sie geben können
- Figuren-Verbindungen, Karten und getrennte SL-Spoiler
- Spoiler-Schalter und Spielerhandouts
- Szenen-Presets, einzelne Effekte und Lautstärkemischung
- Stopp-Taste, Fortschritt und Speicherung im Browser
- drei Reisende, allgemeine Sessionnotiz und eine eigene Notiz pro Szene

Die Browser-Version ist ein Testleitstand. Die Installation auf dem iPad erfolgt über die signierte IPA in AltStore.
