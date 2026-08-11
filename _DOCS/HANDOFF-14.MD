# Handoff 14 - Spieleinladung

## Erledigt

- Neues textfreies Einladungsmotiv unter `print/assets/einladung-kraehenfels-bg.png`.
- Reproduzierbarer ReportLab-Builder unter `tools/build_invitation.py`.
- Ausgabe als `outputs/Einladung_Kraehenfels.pdf` plus gerenderte Handy-/Chat-Vorschau `outputs/Einladung_Kraehenfels.png`.
- Die Einladung nennt den Schauplatz und das Folk-Horror-Thema, erklärt Spielerzahl und Dauer und bittet die drei Mitspieler, ihre How-to-be-a-Hero-Charaktere vorab vorzubereiten.
- PDF wurde als A4 gerendert und visuell auf Textüberlauf, Kontrast und Lesbarkeit geprüft.

## Erneut erzeugen

```powershell
python tools/build_invitation.py
```

Die Datei nutzt ausschließlich relative Projektpfade und ersetzt nur die beiden Einladungsdateien im Ausgabeordner.
