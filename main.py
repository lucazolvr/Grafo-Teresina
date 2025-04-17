import osmnx as ox
import json

# Definir o local
place_name = "Teresina, Piauí, Brazil"

# Baixar o grafo de ruas (somente para veículos)
graph = ox.graph_from_place(place_name, network_type="drive")

# Função para converter o grafo em JSON
def graph_to_json(graph):
    nodes = []
    edges = []

    # Extrair nós (interseções)
    for node, data in graph.nodes(data=True):
        nodes.append({
            "id": str(node),
            "latitude": data["y"],
            "longitude": data["x"]
        })

    # Extrair arestas (ruas)
    for u, v, key, data in graph.edges(keys=True, data=True):
        edges.append({
            "id": f"{u}-{v}-{key}",
            "source": str(u),
            "target": str(v),
            "length": data.get("length", 0.0),  # Comprimento em metros
            "travel_time": 0.0  # Será calculado no Java
        })

    return {"nodes": nodes, "edges": edges}

# Converter grafo para JSON
graph_json = graph_to_json(graph)

# Salvar como arquivo JSON
with open("teresina.json", "w") as f:
    json.dump(graph_json, f, indent=2)

#Visualizar o grafo para verificar
ox.plot_graph(graph, node_size=10, edge_linewidth=1, show=True)