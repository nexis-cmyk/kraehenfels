# AltStore-Feed

Die Datei [`source.json`](source.json) enthält den zuletzt veröffentlichten iPad-Release. Aktuell ist das `v4.3.0` (Build `10`). Der Code steht bereits auf `v5.0.0` (Build `11`). Der macOS-Release-Workflow erzeugt nach dem Build dafür einen neuen Feed mit den Daten der gebauten IPA.

In AltStore Classic: `Sources` öffnen, `+` wählen und diese Feed-URL eintragen:

Aktueller veröffentlichter Release-Feed (für die Installation von v4.3.0):

`https://github.com/nexis-cmyk/kraehenfels/releases/download/v4.3.0/source.generated.json`

Dauerhafter Feed:

`https://github.com/nexis-cmyk/kraehenfels/raw/refs/heads/main/altstore/source.json`

Danach **Krähenfels** auswählen und **Install** drücken. Alternativ kannst du auf dem Release die IPA laden und in AltStore über `+` bzw. die Teilen-Funktion öffnen. AltStore signiert die unsignierte IPA mit deinem eigenen Apple-Account; ohne diese Signierung lässt iOS die App nicht starten.

Sobald der neue Stand als `v5.0.0` veröffentlicht ist, verwendest du den gleichnamigen `source.generated.json`-Release-Feed. Er wird im Workflow direkt aus der gebauten IPA erzeugt und enthält deshalb die passende Bundle-Version, Buildnummer, Dateigröße und SHA-256-Prüfsumme.

Für einen AltServer auf Windows: AltServer installieren, das iPad einmal per USB verbinden, dem Computer auf dem iPad vertrauen und danach AltServer im Infobereich laufen lassen. Wenn AltStore bereits auf dem iPad installiert ist, reicht der Feed oben; für die erste Installation von AltStore selbst nutzt du im AltServer-Menü **Install AltStore** und wählst dein iPad aus.

Wenn ein Sound in der App nicht hörbar ist, öffne zuerst **Einstellungen** und starte **Audio-Selbsttest**. Prüfe danach die iPad-Lautstärke und eine mögliche Bluetooth-Ausgabe. Die App zeigt an, welche Audio-Datei sie geladen hat.
