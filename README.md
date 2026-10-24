# Sää

Ad-free weather app: Finnish Meteorological Institute (Ilmatieteen laitos) forecast with expandable daily → hourly view, rain radar and a 2 h rain nowcast.

Tap the place name or 🔍 to search places (Nordics + Baltics), use 📍 for your current location, and ☆ to save favourites — all remembered on the device. A link can also preset a place: `https://reijar.github.io/saa/?lat=60.45&lon=22.27&nimi=Turku`. Default is central Helsinki.

Weather warnings: FMI's CAP feed has no CORS, so `.github/workflows/deploy.yml` runs `scripts/build_warnings.py` every 15 min and publishes `warnings.json` with the site.

Data: [FMI open data](https://en.ilmatieteenlaitos.fi/open-data) (CC BY 4.0), [MET Norway](https://api.met.no/) nowcast, [Open-Meteo](https://open-meteo.com/) place search. Icons: [metno/weathericons](https://github.com/metno/weathericons) (MIT). Map: Esri.
