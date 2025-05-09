import osmnx as ox
import os
import re
import json
import matplotlib.pyplot as plt
import math

# Configurações do OSMnx
ox.settings.use_cache = False
ox.settings.log_file = False
ox.settings.log_console = False

# Definir o local
place_name = "Centro, Teresina, Piauí, Brazil"

def create_safe_filename(place_name):
    safe_name = re.sub(r'[^\w\s,-]', '', place_name)
    return safe_name.replace(' ', '').replace(',', '').replace('-', '_')

# Cria diretório de saída na raiz do projeto
cache_dir = "mapa"
os.makedirs(cache_dir, exist_ok=True)

file_base_name = create_safe_filename(place_name)
graph = ox.graph_from_place(place_name, network_type="drive")

def infer_direction(graph, node_id, nodes_gdf):
    # Obtém arestas conectadas ao nó do semáforo
    in_edges = [(u, v, k, d) for u, v, k, d in graph.in_edges(node_id, keys=True, data=True)]
    out_edges = [(u, v, k, d) for u, v, k, d in graph.out_edges(node_id, keys=True, data=True)]
    
    # Verifica se há arestas oneway
    for _, _, _, data in in_edges:
        if data.get("oneway", False):
            return "backward"  # Semáforo controla fluxo oposto à entrada oneway
    for _, _, _, data in out_edges:
        if data.get("oneway", False):
            return "forward"  # Semáforo controla fluxo na direção da saída oneway
    
    # Se não houver oneway, usa coordenadas para direção cardinal
    node_data = nodes_gdf.loc[node_id]
    node_lat, node_lon = node_data['y'], node_data['x']
    
    # Analisa uma aresta representativa (primeira de entrada ou saída)
    edges = in_edges + out_edges
    if not edges:
        return "unknown"  # Sem arestas conectadas
    
    # Pega o nó conectado pela primeira aresta
    u, v, _, _ = edges[0]
    other_node_id = u if v == node_id else v
    other_node_data = nodes_gdf.loc[other_node_id]
    other_lat, other_lon = other_node_data['y'], other_node_data['x']
    
    # Calcula diferenças de coordenadas
    delta_lat = other_lat - node_lat
    delta_lon = other_lon - node_lon
    
    # Determina direção cardinal com base no ângulo
    angle = math.degrees(math.atan2(delta_lon, delta_lat))
    if -45 <= angle < 45:
        return "north"
    elif 45 <= angle < 135:
        return "east"
    elif 135 <= angle < 225:
        return "south"
    else:
        return "west"

def graph_to_json(graph):
    # Converte nós
    nodes = [{"id": str(node), "latitude": data["y"], "longitude": data["x"]} for node, data in graph.nodes(data=True)]
    
    # Converte arestas
    edges = []
    for u, v, key, data in graph.edges(keys=True, data=True):
        maxspeed = data.get("maxspeed", 50)
        if isinstance(maxspeed, list):
            maxspeed = maxspeed[0]
        try:
            maxspeed = float(maxspeed)
        except:
            maxspeed = 50
        edges.append({
            "id": f"{u}-{v}-{key}",
            "source": str(u),
            "target": str(v),
            "length": data.get("length", 0.0),
            "travel_time": 0.0,
            "oneway": data.get("oneway", False),
            "maxspeed": maxspeed
        })
    
    # Obtém informações dos semáforos
    nodes_gdf, _ = ox.graph_to_gdfs(graph)
    traffic_lights = nodes_gdf[nodes_gdf['highway'] == 'traffic_signals']
    traffic_lights_data = []
    for idx, row in traffic_lights.iterrows():
        # Infere a direção do semáforo
        direction = infer_direction(graph, idx, nodes_gdf)
        traffic_light = {
            "id": str(idx),
            "latitude": row['y'],
            "longitude": row['x'],
            "attributes": {
                "highway": row.get('highway', 'traffic_signals'),
                "destination": row.get('destination', None),
                "ref": row.get('ref', None),
                "traffic_signals:direction": direction
            }
        }
        traffic_lights_data.append(traffic_light)
    
    print("\nInformações dos Semáforos:")
    print(traffic_lights)
    
    return {
        "nodes": nodes,
        "edges": edges,
        "traffic_lights": traffic_lights_data
    }

# Converter grafo para JSON
graph_json = graph_to_json(graph)

# Salvar como arquivo JSON
json_filename = os.path.join(cache_dir, f"{file_base_name}.json")
with open(json_filename, "w") as f:
    json.dump(graph_json, f, indent=2)

# Visualizar o grafo
fig, ax = ox.plot_graph(graph, node_size=10, edge_color="yellow", edge_linewidth=1, show=True)

print(f"\nO arquivo foi gerado: '{json_filename}'.")