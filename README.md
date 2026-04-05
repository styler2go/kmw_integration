# Kachelmann Wetter Home Assistant Integration

Mit dieser Integration kannst du Wetterdaten von Kachelmann Wetter direkt in Home Assistant nutzen – inklusive 14-Tage-Vorhersage und aktuellem Wetter.

## Patch Notes (2026-04-05)
- **Multi-Standort:** Mehrere Wetterstandorte pro API Key moeglich (1 Integration = 1 API Key, N Standorte).
- **Zone Selector:** Standorte werden ueber Home Assistant Zonen hinzugefuegt, mit optionalem Override fuer Name und Koordinaten.
- **Geraete-Zuordnung:** Alle Entities (Wetter + Sensoren) sind jetzt einem Device zugeordnet und erscheinen gruppiert in der UI.
- **Parallele API-Aufrufe:** Alle 4 API-Endpoints werden gleichzeitig abgefragt (~900ms schneller pro Zyklus).
- **Benennbar:** Integration und Standorte koennen frei benannt werden.
- **Icon:** Kachelmann Wetter Logo als Integrations-Icon.
- **Migration:** Bestehende V1-Eintraege werden automatisch auf V2 migriert. Entities, History und Dashboards bleiben erhalten.

**Achtung:** Die meisten Hobby API Keys erlauben nur **einen** Standort. Mehrere Standorte erfordern ein entsprechendes API-Abo.

## Patch Notes (2026-02-05)
- Erweiterte stuendliche Vorhersage: 1h + 3h Daten werden zusammengefuehrt (24h Detail, danach 3h Schritt).
- Mehr Felder fuer Wetterkarten: zusaetzliche stuendliche und taegliche Attribute, inkl. Druck, Taupunkt, Feuchte.
- Aktueller Niederschlag nutzt jetzt `precCurrent`.

## Installation ueber HACS
1. Öffne HACS in Home Assistant.
2. Gehe zu **"Integrationen"** und klicke oben rechts auf die drei Punkte → **"Benutzerdefiniertes Repository hinzufügen"**.
3. Gib die URL dieses Repos ein und wähle **"Integration"** als Typ.
4. Suche nach "Kachelmann Wetter" in HACS und installiere die Integration.
5. Starte Home Assistant neu.

## Integration einrichten
1. Gehe zu **"Einstellungen" → "Integrationen"**.
2. Klicke auf **"Integration hinzufuegen"** und suche nach "Kachelmann Wetter".
3. Gib deinen API Key und optional einen Namen ein.
4. Klicke auf der Integrationsseite auf **"Standort hinzufuegen"**.
5. Waehle eine Home Assistant Zone aus (optional: Name und Koordinaten ueberschreiben).
6. Wiederhole Schritt 4-5 fuer weitere Standorte.

## API Key
Du benoetigst einen API Key von [Kachelmann Wetter](https://api.kachelmannwetter.com/v02/_doc.html). Registriere dich dort und trage den Key bei der Einrichtung ein.

**Achtung:** Die meisten Hobby API Keys erlauben nur **einen** Standort.

---
**Hinweis:** Diese Integration ist inoffiziell und steht in keiner Verbindung zu Kachelmann Wetter.
