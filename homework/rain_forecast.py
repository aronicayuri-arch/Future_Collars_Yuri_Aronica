import requests
import geocoder
from datetime import datetime, timedelta
from ast import literal_eval

# ─────────────────────────────────────────
#  Rain Forecast Program
#  Uses Open-Meteo API (free, no key needed)
#  Includes optional challenge: custom location via geocoder
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
#  CACHE: LOAD & SAVE
# ─────────────────────────────────────────

def load_cache():
    """Load saved query results from file. Returns a dict."""
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


def save_cache(cache):
    """Save query results dict to file."""
    try:
        with open(CACHE_FILE, "w") as f:
            f.write(repr(cache))
    except Exception as e:
        print(f"  ⚠ Could not save cache: {e}")


# ─────────────────────────────────────────
#  DATE INPUT & VALIDATION
# ─────────────────────────────────────────

def get_date_from_user():
    """Ask user for a date. If blank, use tomorrow."""
    date_str = input("Enter a date (YYYY-MM-DD) or press Enter for tomorrow: ").strip()

    if date_str == "":
        tomorrow = datetime.now() + timedelta(days=1)
        date_str = tomorrow.strftime("%Y-%m-%d")
        print(f"  ℹ No date entered. Using tomorrow: {date_str}")
        return date_str

    # Validate format
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        print("  ✖ Invalid date format. Please use YYYY-MM-DD (e.g. 2024-06-15).")
        return None


# ─────────────────────────────────────────
#  LOCATION INPUT (Optional Challenge)
# ─────────────────────────────────────────

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


# ─────────────────────────────────────────
#  API REQUEST
# ─────────────────────────────────────────

def fetch_precipitation(lat, lon, date_str):
    """Call the Open-Meteo API and return the precipitation value."""
    url = API_URL.format(lat=lat, lon=lon, date=date_str)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Navigate to the precipitation value
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


# ─────────────────────────────────────────
#  INTERPRET RESULT
# ─────────────────────────────────────────

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

    # Load existing cache
    cache = load_cache()

    # Get date from user
    date_str = get_date_from_user()
    if date_str is None:
        return  # Invalid date entered

    # Get location from user (optional challenge)
    lat, lon, location_name = get_location_from_user()

    # Build a unique cache key: date + location
    cache_key = f"{date_str}|{lat}|{lon}"

    # Check cache first
    if cache_key in cache:
        print(f"\n  ℹ Result loaded from cache (no API call needed).")
        precipitation = cache[cache_key]
    else:
        # Fetch from API
        print(f"\n  🌐 Fetching weather for {date_str} in {location_name}...")
        precipitation = fetch_precipitation(lat, lon, date_str)

        # Save result to cache
        cache[cache_key] = precipitation
        save_cache(cache)

    # Display result
    result = interpret_precipitation(precipitation)
    print(f"\n  📅 Date:     {date_str}")
    print(f"  📍 Location: {location_name}")
    print(f"  🌧 Forecast: {result}\n")


# ─────────────────────────────────────────
main()
