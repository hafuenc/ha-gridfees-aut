# Gridfees AUT

Home-Assistant-Integration für die lokale Berechnung österreichischer variabler
Netzgebühren und Abgaben, netto in EUR/kWh. Grundlage ist `fcn_gridfees_AUT.m`.
Die Integration benötigt keine externe API und keine MATLAB-Installation.

## Stand: 0.1.0 – Einrichtungsgrundgerüst

Diese erste Entwicklungsfassung enthält den Einrichtungsdialog auf Deutsch und
Englisch. Sie speichert Tarifprofile mit Netzgebiet, Bezugsart und den jeweils
relevanten Abgaben- und SNAP-Einstellungen. Mehrere unterschiedliche Profile
können parallel angelegt werden; identische Profile werden abgewiesen.

**Noch keine Preissensoren oder Tarifberechnung.** Eine erfolgreiche Einrichtung
prüft in dieser Version ausschließlich, ob die Integration geladen und das Profil
gespeichert werden kann. Berechnungen, Zeitreihen und nachträgliche Änderungen
der Einstellungen folgen in den nächsten Schritten. Bis dahin kann ein Profil
gelöscht und neu angelegt werden.

## Manuell installieren und prüfen

1. Den Ordner `custom_components/gridfees_aut` vollständig in das
   Konfigurationsverzeichnis von Home Assistant kopieren. Das Ergebnis muss
   `<config>/custom_components/gridfees_aut/manifest.json` enthalten.
2. Home Assistant neu starten.
3. Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** nach
   **Gridfees AUT** suchen.
4. Netzgebiet und Bezugsart auswählen, dann die Tarifannahmen bestätigen.
5. Prüfen, ob das Profil unter Geräte & Dienste erscheint. Es werden in dieser
   Version noch keine Geräte oder Entitäten angelegt.
6. Optional ein anderes Profil hinzufügen und anschließend entfernen. Ein
   identisches Profil soll mit einer Meldung abgewiesen werden.

Die Dateien müssen auf dem HA-System liegen. Ein Browserzugang über Home
Assistant Cloud allein überträgt noch keine Dateien; dafür wird beispielsweise
ein vorhandener Dateieditor mit Upload-Funktion oder Studio Code Server benötigt.

Das Repository ist für die spätere HACS-Verteilung vorbereitet. Für die reguläre
HACS-Verteilung muss es öffentlich sein; eine Aufnahme in den HACS-Katalog ist
damit noch nicht erfolgt.

## Geplanter Berechnungsumfang

- 14 österreichische Netzgebiete, entsprechend dem MATLAB-Datensatz.
- Netzebene 7, nicht gemessene Leistung, Eintarif.
- Regulärer Netzbezug sowie zugeteilte lokale und regionale EEG-Energie.
- Netznutzung, Netzverlust, Elektrizitätsabgabe und variable Bestandteile des
  Erneuerbaren-Förderbeitrags sowie deren Summe.
- Aktuelle Sensorwerte und lokal berechnete Zeitreihen.
- Tarifgrenzen nach `Europe/Vienna`, einschließlich Sommer-/Winterzeit.
- Keine Fortschreibung unbekannter Tarifjahre.

Nicht enthalten sind Energiebezugspreis, Umsatzsteuer, fixe Grund- und
Leistungspreise, Messentgelte und weitere im MATLAB-Modell ausgeschlossene
Positionen. Die hypothetische WiNAP-Variante ist nicht Teil des regulären Modells.

## Entwicklung

Alle Laufzeitdateien liegen unter `custom_components/gridfees_aut/`.
`manifest.json` enthält die Integrationsversion; `config_flow.py` den Dialog.
`translations/de.json` und `translations/en.json` enthalten die Oberflächentexte.

Python-Syntax, JSON-Dateien und übereinstimmende Übersetzungsschlüssel wurden
lokal geprüft. Die Funktion in einer echten Home-Assistant-Instanz ist noch zu
prüfen; lokal ist Home Assistant nicht installiert.

Referenzen: [Config Flow](https://developers.home-assistant.io/docs/core/integration/config_flow/)
und [Manifest](https://developers.home-assistant.io/docs/creating_integration_manifest/).
