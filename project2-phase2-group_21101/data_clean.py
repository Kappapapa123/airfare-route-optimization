import pandas as pd

df = pd.read_csv('US Airline Flight Routes and Fares 1993-2024.csv')

df_clean = df.dropna(subset=['Geocoded_City1', 'Geocoded_City2'])

df = df_clean


def correct_geocode(value):
    """correct wrong geo info"""
    if isinstance(value, str):
        # Check and correct for Key West, FL
        if "Key West, FL" in value and "(70.129129, -143.63129)" in value:
            # Correct coordinates for Key West, FL
            return "Key West, FL (24.5551, -81.7799)"
        # Check and correct for Tulsa, OK
        elif "Tulsa, OK" in value and "(61.096484, -160.967455)" in value:
            # Correct coordinates for Tulsa, OK
            return "Tulsa, OK (36.1539816, -95.992775)"
    return value


df["Geocoded_City1"] = df["Geocoded_City1"].apply(correct_geocode)
df["Geocoded_City2"] = df["Geocoded_City2"].apply(correct_geocode)

df.to_csv("airports_corrected1.csv", index=False)
