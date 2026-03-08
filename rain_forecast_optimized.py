import requests
import geocoder
from datetime import datetime, timedelta
from ast import literal_eval

# ─────────────────────────────────────────
#  Rain Forecast Program - Optimized
#  Uses a WeatherForecast class to handle
#  caching, file I/O and API requests
# ─────────────────────────────────────────

CACHE_FILE = "rain_cache.txt"

API_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude={lat}&longitude={lon}"
    "&daily=precipitation_sum"
    "&timezone=Europe%2FLondon"
    "&start_date={date}&end_date={date}"
)


# ─────────────────────────────────────────
#  WeatherForecast CLASS
# ─────────────────────────────────────────

class WeatherForecast:
    """
    Handles weather forecast storage, file I/O and API requests.

    Usage:
        forecast = WeatherForecast()
        forecast["2024-06-15"] = 3.2         # save a result
        print(forecast["2024-06-15"])         # get a result
        for date in forecast:                # iterate over known dates
            print(date)
        for date, value in forecast.items(): # iterate over date+value pairs
            print(date, value)
    """

    def __init__(self):
        # Internal dictionary: { "date|lat|lon": precipitation_value }
        self._data = self._load()

    # ── File: Load ──
    def _load(self):
        """Load saved results from the cache file."""
        try:
            with open(CACHE_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return literal_eval(content)
        except FileNotFoundError:
            pass  # No cache yet, that's fine
        except Exception as e:
            print(f"  ⚠ Could not read cache file: {e}")
        return {}

    # ── File: Save ──
    def _save(self):
        """Save all results to the cache file."""
        try:
            with open(CACHE_FILE, "w") as f:
                f.write(repr(self._data))
        except Exception as e:
            print(f"  ⚠ Could not save cache: {e}")

    # ── Dunder: set item ──
    def __setitem__(self, key, value):
        """
        Save a forecast result.
        Example: forecast["2024-06-15|41.9|12.4"] = 3.2
        """
        self._data[key] = value
        self._save()  # save to file every time we store a new result

    # ── Dunder: get item ──
    def __getitem__(self, key):
        """
        Get a forecast result by key.
        Example: forecast["2024-06-15|41.9|12.4"]
        Returns None if not found.
        """
        return self._data.get(key, None)

    # ── Dunder: iter ──
    def __iter__(self):
        """
        Iterate over all known keys (date|lat|lon).
        Example:
            for date in forecast:
                print(date)
        """
        return iter(self._data)

    # ── items: generator ──
    def items(self):
        """
        Generator of (key, value) tuples for all saved results.
        Example:
            for date, value in forecast.items():
                print(date, value)
        """
        for key, value in self._data.items():
            yield key, value

    # ── Check if key exists ──
    def __contains__(self, key):
        """Allows: if key in forecast"""
        return key in self._data


# ─────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────

def get_date_from_user():
    """Ask user for a date. If blank, use tomorrow."""
    date_str = input("Enter a date (YYYY-MM-DD) or press Enter for tomorrow: ").strip()

    if date_str == "":
        tomorrow = datetime.now() + timedelta(days=1)
        date_str = tomorrow.strftime("%Y-%m-%d")
        print(f"  ℹ No date entered. Using tomorrow: {date_str}")
        return date_str

    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        print("  ✖ Invalid date format. Please use YYYY-MM-DD (e.g. 2024-06-15).")
        return None


def get_location_from_user():
    """Ask user for a city name and resolve it to lat/lon using geocoder."""
    city = input("Enter a city name (or press Enter for Rome, Italy): ").strip()

    if city == "":
        print("  ℹ Using default location: Rome, Italy")
        return 41.9028, 12.4964, "Rome, Italy"

    try:
        result = geocoder.osm(city)
        if result.ok:
            print(f"  ✔ Found: {result.address}")
            return result.lat, result.lng, result.address
        else:
            print(f"  ✖ Could not find '{city}'. Using Rome, Italy as default.")
            return 41.9028, 12.4964, "Rome, Italy"
    except Exception as e:
        print(f"  ✖ Geocoder error: {e}. Using Rome, Italy as default.")
        return 41.9028, 12.4964, "Rome, Italy"


def fetch_precipitation(lat, lon, date_str):
    """Call the Open-Meteo API and return the precipitation value."""
    url = API_URL.format(lat=lat, lon=lon, date=date_str)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        values = data.get("daily", {}).get("precipitation_sum", [])
        if values and values[0] is not None:
            return values[0]
        return None

    except requests.exceptions.ConnectionError:
        print("  ✖ No internet connection. Could not reach the API.")
        return None
    except requests.exceptions.Timeout:
        print("  ✖ Request timed out. Try again later.")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"  ✖ API error: {e}")
        return None
    except Exception as e:
        print(f"  ✖ Unexpected error: {e}")
        return None


def interpret_precipitation(value):
    """Return a human-readable rain forecast message."""
    if value is None or value < 0:
        return "I don't know"
    elif value == 0.0:
        return "It will not rain"
    else:
        return f"It will rain (precipitation: {value} mm)"


# ─────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────

def main():
    print("=" * 45)
    print("         🌧  Rain Forecast Program")
    print("=" * 45)

    # Create the WeatherForecast object (loads cache automatically)
    weather_forecast = WeatherForecast()

    # Get date from user
    date_str = get_date_from_user()
    if date_str is None:
        return

    # Get location from user
    lat, lon, location_name = get_location_from_user()

    # Build cache key
    cache_key = f"{date_str}|{lat}|{lon}"

    # Check cache using __contains__ and __getitem__
    if cache_key in weather_forecast:
        print(f"\n  ℹ Result loaded from cache (no API call needed).")
        precipitation = weather_forecast[cache_key]   # uses __getitem__
    else:
        # Fetch from API
        print(f"\n  🌐 Fetching weather for {date_str} in {location_name}...")
        precipitation = fetch_precipitation(lat, lon, date_str)

        # Save using __setitem__ (also saves to file)
        weather_forecast[cache_key] = precipitation   # uses __setitem__

    # Display result
    result = interpret_precipitation(precipitation)
    print(f"\n  📅 Date:     {date_str}")
    print(f"  📍 Location: {location_name}")
    print(f"  🌧 Forecast: {result}")

    # Show all saved results using items() generator
    print("\n── All saved forecasts ──")
    for key, value in weather_forecast.items():       # uses items() generator
        print(f"  {key} → {interpret_precipitation(value)}")


# ─────────────────────────────────────────
main()
