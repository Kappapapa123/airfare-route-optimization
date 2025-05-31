"""Visualization helper file, two main functions are here."""
from __future__ import annotations
from typing import Any, List, Dict, Tuple
import re
import plotly.graph_objects as go
import networkx as nx
import project2_statev2 as state


def visualize_graph(graph: Any) -> None:
    """
    Visualize the given graph interactively using Plotly.

    - Each node displays airport info (code, city, region, and coordinates) on hover.
    - Each edge displays flight details (distance, fare, lowest fare) plus the departure region on hover.
    - Nodes are colored by region (using get_state and get_region).
    - Edges are colored based on the departure region (from the first endpoint).
    - Vertices are positioned using their precise geographic coordinates.
    """

    def safe_float(val: Any, default: float = 0.0) -> float:
        """Convert str to float"""
        try:
            return float(val)
        except ValueError:
            match = re.search(r"[-+]?[0-9]*\.?[0-9]+", str(val))
            if match:
                return float(match.group())
            return default

    region_colors: Dict[str, str] = {
        "Pacific": "#1f77b4",         # blue
        "Mountain": "#ff7f0e",        # orange
        "West North Central": "#2ca02c",  # green
        "East North Central": "#d62728",  # red
        "West South Central": "#9467bd",    # purple
        "East South Central": "#8c564b",    # brown
        "South Atlantic": "#e377c2",        # pink
        "Mid-Atlantic": "#7f7f7f",            # grey
        "New England": "#bcbd22",             # olive
        "Unknown": "#17becf"                 # cyan (default)
    }

    G: nx.Graph = nx.Graph()

    for airport_code, vertex in graph.vertices.items():
        state_abbr: str = state.get_state(vertex.city)
        region: str = state.get_region(state_abbr)
        G.add_node(airport_code,
                   city=vertex.city,
                   region=region,
                   lati=vertex.lati,
                   longi=vertex.longi)

    # Add edges.
    added_edges: set[Tuple[str, str]] = set()
    for airport_code, vertex in graph.vertices.items():
        for neighbour, flight_info in vertex.neighbours.items():
            edge_key: Tuple[str, str] = tuple(sorted([airport_code, neighbour.airport_code]))
            if edge_key not in added_edges:
                G.add_edge(
                    airport_code,
                    neighbour.airport_code,
                    distance=flight_info[0],
                    fare=flight_info[1],
                    lowest_fare=flight_info[2]
                )
                added_edges.add(edge_key)

    # Use stored coordinates: x = longitude and y = latitude.
    pos: Dict[str, Tuple[float, float]] = {
        node: (safe_float(data["longi"]), safe_float(data["lati"]))
        for node, data in G.nodes(data=True)
    }

    node_x: List[float] = []
    node_y: List[float] = []
    node_hover: List[str] = []
    node_colors: List[str] = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        city: str = G.nodes[node]["city"]
        region: str = G.nodes[node]["region"]
        node_hover.append(f"Airport: {node}<br>City: {city}<br>Region: {region}<br>Coordinates: ({x:.4f}, {y:.4f})")
        node_colors.append(region_colors.get(region, "#000000"))

    node_trace: go.Scatter = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        hoverinfo="text",
        hovertext=node_hover,
        marker={"size": 15, "color": node_colors, "line_width": 2}
    )

    edge_traces: List[Any] = []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        dep_region: str = G.nodes[edge[0]]["region"]
        edge_color: str = region_colors.get(dep_region, "#888")
        hover_text: str = (
            f"Airports: {edge[0]} - {edge[1]}<br>"
            f"Departure Region: {dep_region}<br>"
            f"Distance: {edge[2]['distance']}<br>"
            f"Fare: {edge[2]['fare']}<br>"
            f"Lowest Fare: {edge[2]['lowest_fare']}"
        )
        num_points: int = 10
        x_points: List[float] = [x0 + (x1 - x0) * t / (num_points - 1) for t in range(num_points)]
        y_points: List[float] = [y0 + (y1 - y0) * t / (num_points - 1) for t in range(num_points)]
        edge_trace: go.Scatter = go.Scatter(
            x=x_points,
            y=y_points,
            mode="lines+markers",
            line={"width": 2, "color": edge_color},
            marker={"size": 10, "color": "rgba(0,0,0,0)"},
            hoverinfo="text",
            hovertext=hover_text
        )
        edge_traces.append(edge_trace)

    fig: go.Figure = go.Figure(
        data=edge_traces + [node_trace],
        layout=go.Layout(
            title="Interactive Airport Graph (Geo Positioned)",
            titlefont_size=16,
            showlegend=False,
            hovermode="closest",
            margin={"b": 20, "l": 5, "r": 5, "t": 40},
            xaxis={"title": "Longitude", "showgrid": True, "zeroline": False, "showticklabels": True},
            yaxis={"title": "Latitude", "showgrid": True, "zeroline": False, "showticklabels": True}
        )
    )
    fig.show()


def visualize_graph_with_path(graph: Any, path: List[str]) -> None:
    """
    Visualize the given graph interactively using Plotly, highlighting a specified path.

    Parameters:
      - graph: Your airport graph.
      - path: A list of airport codes (strings) representing a directed path.

    In the visualization:
      - Nodes and edges in the specified path are colored according to their region,
        with the edge color set to the color of the departure vertex.
      - All other nodes and edges are drawn in grey.
      - Path nodes are drawn larger with a thick black outline and have text labels
        that display their info (so the info is directly visible).
      - Path edges are drawn on top so they are not overlapped by other routes.
      - Positions use the stored geographic coordinates.
    """
    def safe_float(val: Any, default: float = 0.0) -> float:
        try:
            return float(val)
        except ValueError:
            match = re.search(r"[-+]?[0-9]*\.?[0-9]+", str(val))
            if match:
                return float(match.group())
            return default

    region_colors: Dict[str, str] = {
        "Pacific": "#1f77b4",  # blue
        "Mountain": "#ff7f0e",  # orange
        "West North Central": "#2ca02c",  # green
        "East North Central": "#d62728",  # red
        "West South Central": "#9467bd",  # purple
        "East South Central": "#8c564b",  # brown
        "South Atlantic": "#e377c2",  # pink
        "Mid-Atlantic": "#7f7f7f",  # grey
        "New England": "#bcbd22",  # olive
        "Unknown": "#17becf"  # cyan (default)
    }
    default_grey: str = "#cccccc"

    G: nx.Graph = nx.Graph()
    for airport_code, vertex in graph.vertices.items():
        state_abbr: str = state.get_state(vertex.city)
        region: str = state.get_region(state_abbr)
        G.add_node(airport_code,
                   city=vertex.city,
                   region=region,
                   lati=vertex.lati,
                   longi=vertex.longi)

    added_edges: set[Tuple[str, str]] = set()
    for airport_code, vertex in graph.vertices.items():
        for neighbour, flight_info in vertex.neighbours.items():
            edge_key: Tuple[str, str] = tuple(sorted([airport_code, neighbour.airport_code]))
            if edge_key not in added_edges:
                G.add_edge(
                    airport_code,
                    neighbour.airport_code,
                    distance=flight_info[0],
                    fare=flight_info[1],
                    lowest_fare=flight_info[2]
                )
                added_edges.add(edge_key)

    pos: Dict[str, Tuple[float, float]] = {
        node: (safe_float(data["longi"]), safe_float(data["lati"]))
        for node, data in G.nodes(data=True)
    }

    path_edges: List[Tuple[str, str]] = [(path[i], path[i + 1]) for i in range(len(path) - 1)]

    bg_node_x: List[float] = []
    bg_node_y: List[float] = []
    bg_node_hover: List[str] = []
    bg_node_colors: List[str] = []
    bg_node_size: List[int] = []
    path_node_x: List[float] = []
    path_node_y: List[float] = []
    path_node_hover: List[str] = []
    path_node_colors: List[str] = []
    path_node_size: List[int] = []
    path_node_text: List[str] = []
    for node in G.nodes():
        x, y = pos[node]
        city: str = G.nodes[node]["city"]
        region: str = G.nodes[node]["region"]
        hover: str = f"Airport: {node}<br>City: {city}<br>Region: {region}<br>Coords: ({x:.4f}, {y:.4f})"
        label: str = f"{node}<br>{city}<br>{region}"
        if node in set(path):
            path_node_x.append(x)
            path_node_y.append(y)
            path_node_hover.append(hover)
            path_node_colors.append(region_colors.get(region, "#000000"))
            path_node_size.append(22)
            path_node_text.append(label)
        else:
            bg_node_x.append(x)
            bg_node_y.append(y)
            bg_node_hover.append(hover)
            bg_node_colors.append(default_grey)
            bg_node_size.append(15)

    bg_node_trace: go.Scatter = go.Scatter(
        x=bg_node_x,
        y=bg_node_y,
        mode="markers",
        hoverinfo="text",
        hovertext=bg_node_hover,
        marker={"size": bg_node_size, "color": bg_node_colors, "line_width": 1, "line_color": default_grey}
    )

    path_node_trace: go.Scatter = go.Scatter(
        x=path_node_x,
        y=path_node_y,
        mode="markers+text",
        hoverinfo="text",
        hovertext=path_node_hover,
        text=path_node_text,
        textposition="top center",
        marker={"size": path_node_size, "color": path_node_colors, "line_width": 3, "line_color": "black"}
    )

    bg_edge_traces: List[Any] = []
    for edge in G.edges(data=True):
        u: str = edge[0]
        v: str = edge[1]
        if (u, v) in path_edges or (v, u) in path_edges:
            continue
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        hover_text: str = (
            f"Airports: {u} - {v}<br>"
            f"Distance: {edge[2]['distance']}<br>"
            f"Fare: {edge[2]['fare']}<br>"
            f"Lowest Fare: {edge[2]['lowest_fare']}"
        )
        num_points: int = 10
        x_points: List[float] = [x0 + (x1 - x0) * t / (num_points - 1) for t in range(num_points)]
        y_points: List[float] = [y0 + (y1 - y0) * t / (num_points - 1) for t in range(num_points)]
        trace: go.Scatter = go.Scatter(
            x=x_points,
            y=y_points,
            mode="lines",
            line={"width": 1, "color": default_grey},
            hoverinfo="text",
            hovertext=hover_text
        )
        bg_edge_traces.append(trace)

    path_edge_traces: List[Any] = []
    for (dep, arr) in path_edges:
        x0, y0 = pos[dep]
        x1, y1 = pos[arr]
        hover_text: str = (
            f"Airports: {dep} - {arr}<br>"
            f"Distance: {G.edges[dep, arr]['distance']}<br>"
            f"Fare: {G.edges[dep, arr]['fare']}<br>"
            f"Lowest Fare: {G.edges[dep, arr]['lowest_fare']}"
        )
        dep_region: str = G.nodes[dep]["region"]
        color: str = region_colors.get(dep_region, "#000000")
        num_points = 10
        x_points = [x0 + (x1 - x0) * t / (num_points - 1) for t in range(num_points)]
        y_points = [y0 + (y1 - y0) * t / (num_points - 1) for t in range(num_points)]
        trace: go.Scatter = go.Scatter(
            x=x_points,
            y=y_points,
            mode="lines",
            line={"width": 3, "color": color},
            hoverinfo="text",
            hovertext=hover_text
        )
        path_edge_traces.append(trace)

    fig: go.Figure = go.Figure(
        data=bg_edge_traces + path_edge_traces + [bg_node_trace, path_node_trace],
        layout=go.Layout(
            title="Interactive Airport Graph with Highlighted Path",
            titlefont_size=16,
            showlegend=False,
            hovermode="closest",
            margin={"b": 20, "l": 5, "r": 5, "t": 40},
            xaxis={"title": "Longitude", "showgrid": True, "zeroline": False, "showticklabels": True},
            yaxis={"title": "Latitude", "showgrid": True, "zeroline": False, "showticklabels": True}
        )
    )
    fig.show()
