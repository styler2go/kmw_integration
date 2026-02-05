# Kachelmann Wetter Home Assistant Integration

Mit dieser Integration kannst du Wetterdaten von Kachelmann Wetter direkt in Home Assistant nutzen – inklusive 14-Tage-Vorhersage und aktuellem Wetter.

## Patch Notes (2026-02-05)
- Erweiterte stündliche Vorhersage: 1h + 3h Daten werden zusammengefuehrt (24h Detail, danach 3h Schritt).
- Mehr Felder fuer Wetterkarten: zusaetzliche stündliche und taegliche Attribute, inkl. Druck, Taupunkt, Feuchte.
- Aktueller Niederschlag nutzt jetzt `precCurrent`.

## Installation über HACS
1. Öffne HACS in Home Assistant.
2. Gehe zu **"Integrationen"** und klicke oben rechts auf die drei Punkte → **"Benutzerdefiniertes Repository hinzufügen"**.
3. Gib die URL dieses Repos ein und wähle **"Integration"** als Typ.
4. Suche nach "Kachelmann Wetter" in HACS und installiere die Integration.
5. Starte Home Assistant neu.

## Integration einrichten
1. Gehe zu **"Einstellungen" → "Integrationen"**.
2. Klicke auf **"Integration hinzufügen"** und suche nach "Kachelmann Wetter".
3. Folge dem Dialog und gib deinen persönlichen API Key ein.

## API Key
Du benötigst einen API Key von [Kachelmann Wetter](https://api.kachelmannwetter.com/v02/_doc.html). Registriere dich dort und trage den Key bei der Einrichtung ein.

---
**Hinweis:** Diese Integration ist inoffiziell und steht in keiner Verbindung zu Kachelmann Wetter.
