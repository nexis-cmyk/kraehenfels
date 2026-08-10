# Übergabe 04: Restliche Drucksachen

## Überarbeitung

Die beiden Grubenpläne verwenden jetzt einen eigens erzeugten, gefalteten Vermessungsplan als Untergrund. Die Spielerfassung bleibt unvollständig, lesbar und ohne Spoiler. Die SL-Fassung markiert den Widerhall und den Flutstollen in einem separaten roten Hinweisfeld statt die Planbeschriftung zu überdecken.

Die zweite Seite von `03_Figurenbau.pdf` ist nun eine vollständige Tischreferenz: Probe, Begabung, Geistesblitz und Schaden sind als vier große Regelkarten angelegt. Die erste Seite bleibt bewusst offen für handschriftliche Angaben.

## Neues Asset

- `print/assets/alter-grubenplan-survey.png`

## Prüfung

```powershell
python -m py_compile tools/build_print_pack.py
python tools/build_print_pack.py
python tools/validate_project.py
```

Die neue Spieler- und SL-Variante des Grubenplans sowie die zweite Seite des Figurenbogens wurden per Poppler gerendert und visuell geprüft.
