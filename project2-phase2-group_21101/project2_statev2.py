"""Code for project2
This module defines functions to determine the region of a US state and the state abbreviation of a city."""
import python_ta


def get_region(state_abbr: str) -> str:
    """Returns the region of which the state is in.
    If region does not exist, return "Unknown"
    """
    for region, states in REGIONS.items():
        if state_abbr in states:
            return region
    return "Unknown"


def get_state(city_name: str) -> str:
    """Returns the two letter abbreviated state name of the city"""
    for name in STATE_NAME:
        if name in city_name:
            return name
    return None


REGIONS = {
    "Pacific": ["CA", "OR", "WA", "AK", "HI"],
    "Mountain": ["NV", "ID", "MT", "WY", "UT", "CO", "AZ", "NM"],
    "West North Central": ["ND", "SD", "NE", "KS", "MN", "IA", "MO"],
    "East North Central": ["WI", "MI", "IL", "IN", "OH"],
    "West South Central": ["OK", "TX", "AR", "LA"],
    "East South Central": ["KY", "TN", "MS", "AL"],
    "South Atlantic": ["DE", "MD", "DC", "VA", "WV", "NC", "SC", "GA", "FL"],
    "Mid-Atlantic": ["NY", "NJ", "PA"],
    "New England": ["ME", "NH", "VT", "MA", "RI", "CT"],
}

STATE_NAME = ["CA", "OR", "WA", "AK", "HI", "NV", "ID", "MT", "WY", "UT", "CO", "AZ", "NM",
              "ND", "SD", "NE", "KS", "MN", "IA", "MO", "WI", "MI", "IL", "IN", "OH", "CT",
              "OK", "TX", "AR", "LA", "KY", "TN", "MS", "AL", "DE", "MD", "DC", "VA", "WV",
              "NC", "SC", "GA", "FL", "NY", "NJ", "PA", "ME", "NH", "VT", "MA", "RI"]

if __name__ == "__main__":
    python_ta.check_all(config={
        'extra-imports': ['python_ta'],
        'allowed-io': [],
        'max-line-length': 120,
    })
