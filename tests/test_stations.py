import services.stations as stations


def test_stations_module_imports() -> None:
    assert stations is not None


def test_fallback_stations_non_empty() -> None:
    assert isinstance(stations._FALLBACK_STATIONS, list)
    assert len(stations._FALLBACK_STATIONS) > 0
    assert "icao" in stations._FALLBACK_STATIONS[0]


def test_find_nearest_station_with_mock_list() -> None:
    mock_stations = [
        {"icao": "KABC", "name": "Alpha", "state": "KS", "lat": 39.0, "lon": -95.0, "elevation": 900.0, "type": "NEXRAD"},
        {"icao": "KXYZ", "name": "Bravo", "state": "MO", "lat": 40.0, "lon": -94.0, "elevation": 800.0, "type": "NEXRAD"},
    ]
    result = stations.find_nearest_station(39.1, -95.1, stations=mock_stations)
    assert result is not None
    assert result["icao"] == "KABC"


def test_search_stations_by_icao() -> None:
    mock_stations = [
        {"icao": "KTLX", "name": "Oklahoma City", "state": "OK", "lat": 35.3, "lon": -97.3, "elevation": 1213.0, "type": "NEXRAD"},
        {"icao": "KICT", "name": "Wichita", "state": "KS", "lat": 37.6, "lon": -97.4, "elevation": 1335.0, "type": "NEXRAD"},
    ]
    result = stations.search_stations("KTLX", stations=mock_stations)
    assert len(result) == 1
    assert result[0]["icao"] == "KTLX"


def test_search_stations_by_name() -> None:
    mock_stations = [
        {"icao": "KTLX", "name": "Oklahoma City", "state": "OK", "lat": 35.3, "lon": -97.3, "elevation": 1213.0, "type": "NEXRAD"},
        {"icao": "KICT", "name": "Wichita", "state": "KS", "lat": 37.6, "lon": -97.4, "elevation": 1335.0, "type": "NEXRAD"},
    ]
    result = stations.search_stations("wichita", stations=mock_stations)
    assert len(result) == 1
    assert result[0]["icao"] == "KICT"


def test_parse_nexrad_line_valid() -> None:
    # Fixed-width line matching column positions:
    # ICAO:[9:13] NAME:[20:50] ST:[72:74] LAT:[106:115] LON:[116:126] ELEV:[127:133] TYPE:[140:190]
    parts = [" "] * 191
    for i, c in enumerate("KTLX"):
        parts[9 + i] = c
    for i, c in enumerate("Oklahoma City"):
        parts[20 + i] = c
    parts[72], parts[73] = "O", "K"
    for i, c in enumerate(" 35.3331"):
        parts[106 + i] = c
    for i, c in enumerate(" -97.2778"):
        parts[116 + i] = c
    for i, c in enumerate("1213.0"):
        parts[127 + i] = c
    for i, c in enumerate("NEXRAD"):
        parts[140 + i] = c
    line = "".join(parts)

    result = stations._parse_nexrad_line(line)
    assert result is not None
    assert result["icao"] == "KTLX"
    assert result["state"] == "OK"
    assert isinstance(result["lat"], float)


def test_parse_nexrad_line_too_short() -> None:
    result = stations._parse_nexrad_line("short line")
    assert result is None
