# Kachelmann Wetter API v02 - Reference

Source: https://api.kachelmannwetter.com/v02/_doc.json

## Authentication
- Header: `X-API-Key` or query parameter
- Rate limits: 120-250 requests/minute depending on tier

## Endpoints

### 1. Current Weather
`GET /current/{lat}/{lon}`
- **Parameters:** lat, lon (path), units (query)
- **Response:** lat, lon, systemOfUnits, data (object with dateTime, name, value, type, source)

### 2. Three-Day Forecast
`GET /forecast/{lat}/{lon}/3day`
- **Parameters:** lat, lon (path), ForecastModel (query), units (query)
- **Response:** lat, lon, alt, resolution, timeZone, systemOfUnits, run, data[]
- **Data fields:** dateTime, dayName, tempMax, tempMin, precCurrent, windGust, windSpeed, windDirection, sunHours, cloudCoverage, weatherSymbol, risks, timeOfDay

### 3. Fourteen-Day Trend
`GET /forecast/{lat}/{lon}/trend14days`
- **Parameters:** lat, lon (path), units (query)
- **Response:** lat, lon, alt, timeZone, systemOfUnits, run, nextRun, data[]
- **Data fields:** dateTime, isWeekend, weekday, tempMax, tempMin, prec, windGust, sunHours, cloudCoverageEighths, cloudWord, weatherSymbol

### 4. Standard Parameters Forecast
`GET /forecast/{lat}/{lon}/standard/{timeSteps}`
- **Parameters:** lat, lon (path), timeSteps (1h/3h/6h), units (query)
- **Response:** lat, lon, alt, resolution, timeZone, systemOfUnits, run, data[]
- **Data fields:** dateTime, isDay, temp, dewpoint, pressureMsl, humidityRelative, windSpeed, windDirection, windGust, windGust3h, cloudCoverage, sunHours, precCurrent, prec6h, snowAmount, snowHeight

### 5. Advanced Parameters Forecast
`GET /forecast/{lat}/{lon}/advanced/{timeSteps}`
- **Parameters:** lat, lon (path), timeSteps (1h/3h/6h), units (query)
- **Response:** lat, lon, alt, resolution, timeZone, systemOfUnits, run, data[]
- **Data fields:** dateTime, isDay, temp, tempMin6h, tempMax6h, tempMin12h, tempMax12h, dewpoint, pressureMsl, humidityRelative, windSpeed, windDirection, windGust, windGust3h, cloudCoverage, cloudCoverageLow, cloudCoverageMedium, cloudCoverageHigh, sunHours, globalRadiation, precCurrent, prec6h, prec12h, prec24h, precTotal, snowAmount, snowAmount6h, snowAmount12h, snowAmount24h, snowHeight, wmoCode, weatherSymbol

### 6. Station Search
`GET /station/search/{lat}/{lon}`
- **Parameters:** lat, lon (path), radius (query, km)
- **Response:** Array of stations with: id, name, lat, lon, alt, precision, type, recentlyActive, distance

### 7. Station Observations - Latest
`GET /station/{stationId}/observations/latest`
- **Parameters:** stationId (path)
- **Response:** stationId, name, lat, lon, ele, data[] (dateTime, name, value)

### 8. Station Observations - Time Series
`GET /station/{stationId}/observations/{timeSteps}`
- **Parameters:** stationId (path), timeSteps (1d/1h/10min), threshold (query)
- **Response:** stationId, name, lat, lon, ele, data[]
- **Data fields:** dateTime, temp, tempMean, tempMin, tempMax, dewpointMean, precSum, precSumBest, precSumModified, prec24h, snowHeightMean, snowHeightMin, snowHeightMax, windSpeedMean, windSpeedMax, windGustMax, windDirectionMean, pressureMean, pressureMslMean, humidityRelativeMean, globalRadiationSum

### 9. Astronomical Information
`GET /tools/astronomy/{lat}/{lon}`
- **Parameters:** lat, lon (path)
- **Response:** lat, lon, alt, timeZone, run, data[] (astronomical parameters)

### 10. Weather Symbol
`GET /tools/weatherSymbol/{weatherSymbol}.{format}`
- **Parameters:** weatherSymbol (path), format (path, e.g. svg)
- **Response:** Image file
