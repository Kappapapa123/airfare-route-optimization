"""Code for project2"""
from __future__ import annotations
import csv
import heapq
from typing import Any
import networkx as nx
import visual_graph as VG

from project2_statev2 import REGIONS

import project2_statev2 as state


class _Vertex:
    """A vertex in an airport graph, representing an airport.

    Each vertex stores the airport code and the city where the airport is located.

    Instance Attributes:
        - airport_code: The unique code of the airport (e.g., 'JFK').
        - city: The city where the airport is located (e.g., 'New York City, NY (Metropolitan Area)').
        - lati: The latitude of this airport
        - longi: The longitude of this airport
        - neighbours: A dictionary where keys are adjacent _Vertex objects,
                      and values are lists of three integers which representing edge
                      [distance, fare, lowest_fare].
    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
        - isinstance(self.city, str)

    Preconditions:
        - isinstance(airport_code, str)
        - isinstance(city, str)
        - isinstance(lati, float)
        - isinstance(longi, float)
    """
    airport_code: str
    city: str
    lati: float
    longi: float
    neighbours: dict[_Vertex: list[int, int, int]]

    def __init__(self, airport_code: str, city: str, lati: float, longi: float) -> None:
        """Initialize a new vertex representing an airport.

        This vertex is initialized with no neighbours.

        Preconditions:
            - isinstance(airport_code, str)
            - isinstance(city, str)
            - isinstance(lati, float)
            - isinstance(longi, float)
        """
        self.airport_code = airport_code
        self.city = city
        self.lati = lati
        self.longi = longi
        self.neighbours = {}

    def degree(self) -> int:
        """Return the degree of this vertex."""
        return len(self.neighbours)

    def possible_airports_budget(self, budget: float, visited: set[_Vertex]) -> set:
        """Retrun a set of all airport codes that can be reached from the origin airport
        based on the budget
        """
        if budget <= 0:
            return set()
        else:
            possible_airports = {self.airport_code}
            visited.add(self)
            for airport in self.neighbours:
                neighbor_info = self.neighbours[airport]
                fare = neighbor_info[1]
                if airport not in visited:
                    possible_airports.update(airport.possible_airports_budget(budget - fare, visited))

        return possible_airports

    def possible_airport_region(self, budget: float, region: str, visited: set[_Vertex]) -> set:
        """Retrun a set of all airport codes that can be reached from the origin airport,
        which are in the desired region, based on the budget
        """
        if budget <= 0:
            return set()
        else:
            possible_airports = set()
            if state.get_region(self.city) == region:
                possible_airports.update({self.airport_code})
            visited.add(self)
            for airport in self.neighbours:
                neighbor_info = self.neighbours[airport]
                fare = neighbor_info[1]
                if airport not in visited:
                    possible_airports.update(airport.possible_airport_region(budget - fare, region, visited))

        return possible_airports

    def possible_airports_direction(self, coordinate: tuple[float, float], budget: float, direction: str,
                                    visited: set[_Vertex]) -> set:
        """Returns the set of all airports in the given direction,
        based on the budget
        """
        if budget <= 0:
            return set()
        else:
            lati = coordinate[0]
            longi = coordinate[1]
            possible_airports = set()
            if is_in_direction(lati, longi, self.lati, self.longi, direction):
                possible_airports.add(self)
            visited.add(self)
            for airport in self.neighbours:
                neighbor_info = self.neighbours[airport]
                fare = neighbor_info[1]
                if airport not in visited:
                    possible_airports.update(airport.possible_airports_direction((lati, longi), budget - fare,
                                                                                 direction, visited))

        return possible_airports


class Graph:
    """A graph used to represent an airport network.

    This graph stores airports as vertices and the connections between them (flights) as edges.
    Each edge can have associated information such as distance, fare, and lowest fare.
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps airport code to _Vertex object.
    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    @property
    def vertices(self) -> dict[Any, _Vertex]:
        """Return the vertices of the graph."""
        return self._vertices

    def add_vertex(self, airport_code: str, city: str, lati: float, longi: float) -> None:
        """Add a vertex with the given airport code and city to this graph.

        The new vertex is not adjacent to any other vertices.
        Does nothing if the given airport code is already in this graph.
        """
        if airport_code not in self._vertices:
            self._vertices[airport_code] = _Vertex(airport_code, city, lati, longi)

    def add_edge(self, airport_code1: str, airport_code2: str, flight_info: list[float]) -> None:
        """Add a directed edge between the two vertices with the given airport codes in this graph.

        The edge goes from airport_code1 to airport_code2, and also from airport_code2 to airport_code1,
        representing a connection between the two airports.
        The edge stores the distance, fare, and lowest fare for this connection.

        Raise a ValueError if airport_code1 or airport_code2 do not appear as vertices in this graph.

        Preconditions:
            - airport_code1 != airport_code2
        """
        distance = flight_info[0]
        fare = flight_info[1]
        lowest_fare = flight_info[2]
        if airport_code1 in self._vertices and airport_code2 in self._vertices:
            v1 = self._vertices[airport_code1]
            v2 = self._vertices[airport_code2]

            v1.neighbours[v2] = [distance, fare, lowest_fare]
            v2.neighbours[v1] = [distance, fare, lowest_fare]
        else:
            raise ValueError

    def adjacent(self, airport_code1: str, airport_code2: str) -> bool:
        """Return whether airport_code1 and airport_code2 are adjacent vertices in this graph.

        Return False if airport_code1 or airport_code2 do not appear as vertices in this graph.
        """
        if airport_code1 in self._vertices and airport_code2 in self._vertices:
            v1 = self._vertices[airport_code1]
            return any(v2.item == airport_code2 for v2 in v1.neighbours)
        else:
            return False

    def get_neighbours(self, airport_code: str) -> set:
        """Return a set of the airport codes of the neighbours of the given airport code.

        Raise a ValueError if the given airport code does not appear as a vertex in this graph.
        """
        if airport_code in self._vertices:
            v = self._vertices[airport_code]
            return {neighbour.airport_code for neighbour in v.neighbours}
        else:
            raise ValueError

    def get_city(self, airport_code: str) -> str:
        """Retrusn the name of the city which the airport is in"""
        return self._vertices[airport_code].city

    def get_all_vertices(self) -> set:
        """Return a set of all airport codes representing vertices in this graph.
        """
        return {self._vertices[v].airport_code for v in self._vertices}

    def shortest_budget_path(self, origin_code: str, destination_code: str) -> tuple[float, list[str]]:
        """Returns the cost and the path between two airports using fare as weight."""
        pq = [(0, origin_code, [])]
        visited = set()
        while pq:
            cost, node, path = heapq.heappop(pq)
            if node in visited:
                continue
            visited.add(node)
            path = path + [node]
            if node == destination_code:
                return cost, path
            for neighbor, info in self._vertices[node].neighbours.items():
                weight = info[1]
                if neighbor.airport_code not in visited:
                    heapq.heappush(pq, (cost + weight, neighbor.airport_code, path))
        return float("inf"), []

    def shortest_distance_path(self, origin_code: str, destination_code: str) -> tuple[float, list[str]]:
        """Returns the cost and the path between two airports using distance as weight."""
        pq = [(0, origin_code, [])]
        visited = set()
        while pq:
            cost, node, path = heapq.heappop(pq)
            if node in visited:
                continue
            visited.add(node)
            path = path + [node]
            if node == destination_code:
                return cost, path
            for neighbor, info in self._vertices[node].neighbours.items():
                weight = info[0]
                if neighbor.airport_code not in visited:
                    heapq.heappush(pq, (cost + weight, neighbor.airport_code, path))
        return float("inf"), []

    def airport_budget(self, origin_code: str, budget: float) -> set:
        """Retrun a set of all airport codes that can be reached from the origin airport
        based on the budget

        Precoditions:
            - origin_code in self._vertices
        """
        return self._vertices[origin_code].possible_airports_budget(budget, set())

    def airport_region(self, origin_code: str, budget: float, region: str) -> set:
        """Retrun a set of all airport codes that can be reached from the origin airport,
        which is in the desired region, based on the budget

        Precoditions:
            - origin_code in self._vertices
        """
        return self._vertices[origin_code].possible_airport_region(budget, region, set())

    def airport_direction(self, origin_code: str, budget: float, direction: str) -> str:
        """Returns the airport that is the furthest from the origin airport in the given direction,
        based on the budget
        """
        origin_airport = self._vertices[origin_code]
        furthest_airports = origin_airport.possible_airports_direction((origin_airport.lati, origin_airport.longi),
                                                                       budget, direction, set())

        if furthest_airports:
            furthest_airport = furthest_in_direction(furthest_airports, direction)
            return furthest_airport.airport_code
        else:
            return "Sorry, there is no airport that is in your desired direction"

    def to_networkx(self, max_vertices: int = 5000) -> nx.Graph:
        """Convert this graph into an airport network.

        max_vertices specifies the maximum number of vertices that can appear in the graph.
        (This is necessary to limit the visualization output for large graphs.)
        """
        graph_nx = nx.Graph()
        for v in self._vertices.values():
            graph_nx.add_node(v.airport_code, kind='airport')

            for u in v.neighbours:
                if graph_nx.number_of_nodes() < max_vertices:
                    graph_nx.add_node(u.airport_id, kind='airport')

                if u.airport_id in graph_nx.nodes:
                    graph_nx.add_edge(v.airport_code, u.airport_id)

            if graph_nx.number_of_nodes() >= max_vertices:
                break

        return graph_nx

    def visualization(self) -> None:
        """
        Visualize the graph interactively using Plotly.

        - Each node shows airport info (code, city, and region) on hover.
        - Each edge shows flight details (distance, fare, lowest fare) plus the departure region on hover.
        - Nodes are colored by region (determined from their city via get_state and get_region).
        - Edges are colored based on the departure region (taken from the first endpoint).
        - Multiple intermediate invisible markers are sampled along each edge to enlarge the hover area.
        """

        VG.visualize_graph(self)

    def path_visual(self, path: list[str]) -> None:
        """visualiza the path"""
        VG.visualize_graph_with_path(self, path)


def load_review_graph(reviews_file: str) -> Graph:
    """Return an airport graph corresponding to the given airline dataset.

    The airport graph stores all the information from airline_file as follows:
    Create one vertex for each unique airport (identified by its airport code) in the dataset.
    Edges represent a flight between two airports. The edge between two airports stores the
    distance, fare, and lowest fare for that route.

    Preconditions:
        - airline_file is the path to a CSV file containing airline data.
          The expected columns are (in order):
        - 0: flight_number
        - 1: airline
        - 2: scheduled_departure_time
        - 3: departure_time
        - 4: scheduled_arrival_time
        - 5: arrival_time
        - 6: origin_city
        - 7: origin_airport
        - 8: destination_city
        - 9: destination_airport
        - 10: distance
        - 11: duration
        - 12: scheduled_duration
        - 13: total_fare
        - ... (other columns might exist but are ignored)
        - 19: lowest_fare
    """
    airport_graph = Graph()
    airport_vertices = set()

    with open(reviews_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == 'tbl':
                continue
            city_names = (row[5], row[6])
            air_codes = (row[9], row[10])
            distance = row[11]
            fare = row[13]
            fare_low = row[19]
            origin_geocode = get_coordinate(row[20])
            destination_geocode = get_coordinate(row[21])

            if fare_low == '':
                fare_low = fare

            if air_codes[0] not in airport_vertices:
                airport_graph.add_vertex(air_codes[0], state.get_state(city_names[0]), origin_geocode[0],
                                         origin_geocode[1])
                airport_vertices.add(air_codes[0])
            if air_codes[1] not in airport_vertices:
                airport_graph.add_vertex(air_codes[1], state.get_state(city_names[1]), destination_geocode[0],
                                         destination_geocode[1])
                airport_vertices.add(air_codes[1])

            airport_graph.add_edge(air_codes[0], air_codes[1], [float(distance), float(fare), float(fare_low)])

    return airport_graph


def get_coordinate(geocode: str) -> tuple[float, float]:
    """Returns the latitude and longitude from the geocode string"""
    geocode = geocode.split('(')
    geocode = geocode[-1].split(',')
    lati = geocode[0]
    longi = geocode[1].strip(')')
    loc = (float(lati), float(longi))
    return loc


def is_in_direction(lati1: float, longi1: float, lati2: float, longi2: float, direction: str) -> bool:
    """Returns whether the airport with the coordinates lati2 and longi2 are in the correct direction
    with respect to the first airport with coordinates lati1 and longi1
    """
    if direction == 'north':
        return lati2 > lati1
    elif direction == 'south':
        return lati2 < lati1
    elif direction == 'east':
        return longi2 > longi1
    else:
        return longi2 < longi1


def furthest_in_direction(airport_set: set, direction: str) -> Any:
    """Returns the airport object that is the furthest in the given direction.
    If airport_set is empty, return None
    """
    if not airport_set:
        return None

    if direction in {'north', 'east'}:
        return max(airport_set, key=lambda airport: airport.lati if direction == 'north' else airport.longi)
    else:
        return min(airport_set, key=lambda airport: airport.lati if direction == 'south' else airport.longi)


def load_airport_codes(csv_file: str) -> set:
    """Load airport codes from a CSV file and return a set of valid airport codes."""
    airport_codes = set()

    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)

        for row in reader:
            if row[0] == 'tbl':
                continue
            if len(row) > 9:
                airport_codes.add(row[9])
                airport_codes.add(row[10])

    return airport_codes


if __name__ == "__main__":

    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['csv', 'heapq', 'typing', 'Visual_Graph', 'project2_statev2', 'networkx', 'networkx.classes',
                          'python_ta', "visual_graph"],
        'allowed-io': ['print', 'open', 'input', 'load_review_graph', 'load_airport_codes'],
        'max-line-length': 120
    })

    csv_file_path = "data/airports_corrected1.csv"
    valid_airport_codes = load_airport_codes(csv_file_path)
    airline_graph = load_review_graph(csv_file_path)
    airline_graph.visualization()
    exit_program = False

    while not exit_program:
        ac_input = input(
            "From which airport do you want to depart? Please enter the 3-letter airport code (e.g., JFK) "
            "or type 'end' to quit: "
        ).strip().upper()
        if ac_input.lower() == 'end':
            exit_program = True
            break
        if ac_input not in valid_airport_codes:
            print("Sorry, airport code not found in the database. Please try again.")
            continue
        ac = ac_input
        print(f"You decided to depart from {ac}.")

        budge = 0.0
        while True:
            budge = input(
                "What is your budget for this trip? Please enter a number (in USD) or type 'end' to quit: "
            ).strip()
            if budge.lower() == 'end':
                exit_program = True
                break
            try:
                budge = float(budge)
                if budge <= 0:
                    print("Please enter a valid budget greater than 0.")
                else:
                    print(f"Your budget is set to ${budge:.2f}.")
                    break
            except ValueError:
                print("Invalid input. Please enter a numeric value.")
        if exit_program:
            break

        while True:
            print("\nAvailable regions:")
            for regio in REGIONS:
                print(f"- {regio}")
            destination_option = input(
                "\nDo you have a specific region in mind? (yes/no/end): "
            ).strip().lower()
            if destination_option == 'end':
                exit_program = True
                break

            if destination_option == 'yes':
                destination_region_input = ""
                while True:
                    destination_region_input = input(
                        "Which region do you want to travel to? Please enter the region name or type 'end' to quit: "
                    ).strip()
                    if destination_region_input.lower() == 'end':
                        exit_program = True
                        break
                    if destination_region_input in REGIONS:
                        print(f"You chose to travel to the {destination_region_input} region.")
                        print("Here are the possible airports within your budget:")
                        print(airline_graph.airport_region(ac, budge, destination_region_input))
                        break
                    else:
                        print("Invalid region name. Please select from the list above.")
                if exit_program:
                    break
                break
            elif destination_option == 'no':
                furthest_airport1 = ""
                while True:
                    direction_input = input(
                        "In which direction would you like to travel? Please enter from these options "
                        "(North, West, East, South), "
                        "or type 'no' if you don't have any idea, or 'end' to quit: "
                    ).strip().lower()
                    if direction_input == 'end':
                        exit_program = True
                        break
                    if direction_input in ['north', 'south', 'east', 'west']:
                        print(f"You chose to travel to the {direction_input} direction.")
                        furthest_airport1 = airline_graph.airport_direction(ac, budge, direction_input)
                        print(
                            f"Based on your budget and direction, the furthest possible destination is:"
                            f" {furthest_airport1}")
                        break
                    elif direction_input == "no":
                        print(f"Here are the possible airports based on your budget from {ac}:")
                        print(airline_graph.airport_budget(ac, budge))
                        break
                    else:
                        print("Invalid direction name. Please select from the list above.")
                if exit_program:
                    break
                break
            else:
                print("Invalid option. Please enter 'yes', 'no', or 'end'.")
        if exit_program:
            break

        while True:
            action_input = input(
                "\nWould you like to know more about our recommended trip? "
                "(options: paths, city, new trip, end): "
            ).strip().lower()
            if action_input == 'end':
                exit_program = True
                break

            if action_input == 'paths':
                print("\nAvailable path options:")
                print("- Cheapest path: Cheapest path to the airport")
                print("- Shortest path: Shortest path (by distance) to the airport")
                while True:
                    path_option_input = input(
                        "Enter the path option you want to see "
                        "('cheapest path' or 'shortest path', or 'back' to go back, 'end' to quit): "
                    ).strip().lower()
                    if path_option_input == 'end':
                        exit_program = True
                        break
                    if path_option_input == 'back':
                        break
                    if path_option_input not in ['cheapest path', 'shortest path']:
                        print("Invalid path option. Please try again.")
                        continue

                    destination_airport = ""
                    while True:
                        destination_airport_input = input(
                            "Enter the destination airport code or type 'end' to quit: "
                        ).strip().upper()
                        if destination_airport_input.lower() == 'end':
                            exit_program = True
                            break
                        if destination_airport_input not in valid_airport_codes:
                            print("Invalid airport code. Please try again.")
                            continue
                        else:
                            destination_airport = destination_airport_input
                            break
                    if exit_program:
                        break

                    cost1 = float('inf')
                    path1 = []
                    path_found = False

                    if path_option_input == 'cheapest path':
                        cost1, path1 = airline_graph.shortest_budget_path(ac, destination_airport)
                        if path1 and cost1 != float("inf"):
                            airline_graph.path_visual(path1)
                            print(f"Cheapest path for {destination_airport} costs {cost1} dollars: {path1}")
                            path_found = True
                        else:
                            print(f"No path found from {ac} to {destination_airport}.")
                    elif path_option_input == 'shortest path':
                        cost1, path1 = airline_graph.shortest_distance_path(ac, destination_airport)
                        if path1 and cost1 != float("inf"):
                            airline_graph.path_visual(path1)
                            print(f"Shortest path for {destination_airport} is {cost1} miles: {path1}")
                            path_found = True
                        else:
                            print(f"No path found from {ac} to {destination_airport}.")

                    break
                if exit_program:
                    break

            elif action_input == 'city':

                destination_airport = ""
                while True:
                    destination_airport_input = input(
                        "Enter the destination airport code or type 'end' to quit: "
                    ).strip().upper()
                    if destination_airport_input.lower() == 'end':
                        exit_program = True
                        break
                    if destination_airport_input not in valid_airport_codes:
                        print("Invalid airport code. Please try again.")
                        continue
                    destination_airport = destination_airport_input
                    try:
                        city_name = airline_graph.get_city(destination_airport)
                        print(f"This destination is in: {city_name} state")
                    except KeyError:
                        print(f"Airport code '{destination_airport}' not found.")
                    break
                if exit_program:
                    break
            elif action_input == 'new trip':
                break
            else:
                print("Invalid action. Please choose from 'paths', 'city', 'new trip', or 'end'.")

        if exit_program:
            break

    print("Exiting the airport planner. Thank you for using our services.")
