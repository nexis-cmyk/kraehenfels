# Übergabe 05: Krähenfels 2.0

## Spielleitungs-Leitstand

Das Manifest enthält pro Szene Vorleseimpuls, SL-Notizen, NPC- und Hinweis-IDs, Eskalationsstufe, Sound-Preset, Hilfen bei festgefahrener Gruppe, Abschluss-Checkliste und ein Szenenbild. Die App stellt diese Informationen frei navigierbar dar und speichert abgehakte Hinweise sowie Checklisten lokal.

Die fünf NPCs und elf Pflichtspuren liegen zentral in `content/manifest.json`. `tools/validate_project.py` prüft alle Verweise sowie die Synchronität des App-Manifests.

## Audio

`audio/generate_audio.py` erzeugt 46 eigene Dateien. Neu sind zwei Atmosphären-Layer und neun punktuelle Effekte, darunter Wasser im Flutstollen, verzögerte Schritte, Klopfen, Resonanz und ein Resonanzabbruch.

`AudioEngine.swift` verwendet eine Playback-Audiosession, meldet fehlende Dateien oder Startfehler sichtbar, zeigt die Ausgaberoute an und bietet einen hörbaren Selbsttest. Master, Atmosphäre, Musik und Effekte besitzen getrennte Regler. Das Preset startet die Atmosphären- und Musik-Layer einer Szene; einzelne Cues bleiben separat steuerbar.

## Druckpaket

Die sieben neuen Graphic-Novel-Szenenbilder liegen in `print/assets/` und zusätzlich unter `app/Kraehenfels/Resources/Art/`. Sie werden in der App und in der Bildstrecke am Ende von `10_SL_Abenteuer.pdf` verwendet.

Die Handouts wurden noch einmal als unterschiedliche Requisiten überarbeitet: Ticket mit Frachtanhänger, Zeitung mit Kleinanzeige, beschädigtes Register, Kabinettfoto, Liedblatt mit gezeichneten Noten, Werkbuch mit markierter Platte, Feldnotiz mit Kartenausschnitt, handschriftliche Aussage und handgeschriebener Brief.

Jeder Druckbogen trägt über jedem Prop eine ID und einen Ausgabehinweis. Schnittmarken an den vier Ecken, eine gestrichelte Mittellinie und ein Scherensymbol machen deutlich, dass zwei getrennte A5-Handouts auf einem A4-Bogen stehen. H04/H06, H08 plus Grubenplan sowie H11/H06 sind ausdrücklich als zusammengehörige Ausgabemomente markiert.

Neu: `outputs/12_SL_Am_Tisch.pdf` ist die einseitige laufende Referenz mit Handouts, Hinweisen, nächstem Impuls, Sound und Eskalation je Szene.

## Prüfschritte

```powershell
python audio/generate_audio.py
python tools/build_print_pack.py
python tools/validate_project.py
```

Die finalen PDFs wurden mit Poppler gerendert und visuell geprüft. Auf Windows ist kein Xcode vorhanden; den finalen Swift/iOS-Build prüft der GitHub-Actions-Release-Workflow auf macOS.
