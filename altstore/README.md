# AltStore-Feed

Der Feed liegt als [`source.json`](source.json) im Repository und ist aktuell auf den geprüften Release-Tag `v3.3.1` gepinnt. Der macOS-Release-Workflow erzeugt bei weiteren Versionen zusätzlich eine ausgefüllte `source.generated.json` mit Größe und SHA-256.

In AltStore Classic: `Sources` öffnen, `+` wählen und diese Feed-URL eintragen:

Aktueller Release-Feed (für die Installation von V3):

`https://github.com/nexis-cmyk/kraehenfels/releases/download/v3.3.1/source.generated.json`

Dauerhafter Feed:

`https://github.com/nexis-cmyk/kraehenfels/raw/refs/heads/main/altstore/source.json`

Danach **Krähenfels** auswählen und **Install** drücken. Alternativ kannst du auf dem Release die IPA laden und in AltStore über `+` bzw. die Teilen-Funktion öffnen. AltStore signiert die unsignierte IPA mit deinem eigenen Apple-Account; ohne diese Signierung lässt iOS die App nicht starten.

Für einen AltServer auf Windows: AltServer installieren, iPhone einmal per USB verbinden, dem Computer auf dem iPhone vertrauen und danach AltServer im Infobereich laufen lassen. Wenn AltStore bereits auf dem iPhone installiert ist, reicht der Feed oben; für die erste Installation von AltStore selbst nutzt du im AltServer-Menü **Install AltStore** und wählst dein iPhone aus.

Wenn ein Sound in der App nicht hörbar ist, öffne zuerst **Einstellungen** und starte **Audio-Selbsttest**. Prüfe danach iPhone-Lautstärke, Stummmodus und eine mögliche Bluetooth-Ausgabe. Die App zeigt an, welche Audio-Datei sie geladen hat.
