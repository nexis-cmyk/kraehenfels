# AltStore-Feed

Der Feed liegt als [`source.json`](source.json) im Repository und ist auf den iPad-Release `v4.0.0` ausgelegt. Der macOS-Release-Workflow erzeugt bei weiteren Versionen zusätzlich eine ausgefüllte `source.generated.json` mit Größe und SHA-256.

In AltStore Classic: `Sources` öffnen, `+` wählen und diese Feed-URL eintragen:

Aktueller Release-Feed (für die Installation von V3):

`https://github.com/nexis-cmyk/kraehenfels/releases/download/v4.0.0/source.generated.json`

Dauerhafter Feed:

`https://github.com/nexis-cmyk/kraehenfels/raw/refs/heads/main/altstore/source.json`

Danach **Krähenfels** auswählen und **Install** drücken. Alternativ kannst du auf dem Release die IPA laden und in AltStore über `+` bzw. die Teilen-Funktion öffnen. AltStore signiert die unsignierte IPA mit deinem eigenen Apple-Account; ohne diese Signierung lässt iOS die App nicht starten.

Für einen AltServer auf Windows: AltServer installieren, das iPad einmal per USB verbinden, dem Computer auf dem iPad vertrauen und danach AltServer im Infobereich laufen lassen. Wenn AltStore bereits auf dem iPad installiert ist, reicht der Feed oben; für die erste Installation von AltStore selbst nutzt du im AltServer-Menü **Install AltStore** und wählst dein iPad aus.

Wenn ein Sound in der App nicht hörbar ist, öffne zuerst **Einstellungen** und starte **Audio-Selbsttest**. Prüfe danach die iPad-Lautstärke und eine mögliche Bluetooth-Ausgabe. Die App zeigt an, welche Audio-Datei sie geladen hat.
