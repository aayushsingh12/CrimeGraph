import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.widgets import Slider, Button
import os

def load_and_visualize(file_path='scene_graph.json'):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Force-Unwrap Logic for nested lists
    while isinstance(data, list) and len(data) > 0:
        data = data[0]
    
    if not isinstance(data, dict):
        print("Error: Invalid JSON structure.")
        return

    entities = data.get('entities', [])
    relationships = data.get('relationships', [])
    
    # FIX: Priority check for 'description', then 'label'
    entity_lookup = {}
    for e in entities:
        eid = e.get('id') or e.get('entity_id')
        if eid:
            # Use 'description' as the primary label, fall back to 'label', then ID
            display_name = e.get('description') or e.get('label') or eid
            e['display_name'] = display_name
            entity_lookup[eid] = e

    raw_times = list(set([rel.get('timestamp') for rel in relationships if rel.get('timestamp')]))
    timestamps = sorted([t for t in raw_times if t is not None])
    if not timestamps: timestamps = ["Unknown"]

    color_map = {
        "Person": "#3498db", "Object": "#2ecc71", "Location": "#e74c3c", 
        "Emotion": "#9b59b6", "Attribute": "#f1c40f", "Unknown": "#95a5a6"
    }

    fig, ax = plt.subplots(figsize=(15, 10))
    plt.subplots_adjust(bottom=0.25, right=0.8)

    current_view = {"mode": "Global", "time": timestamps[-1]}
    
    def draw_graph():
        ax.clear()
        G = nx.MultiDiGraph()
        
        if current_view["mode"] == "Temporal":
            limit = current_view["time"]
            filtered_rels = [r for r in relationships if r.get('timestamp', '') <= limit]
            ax.set_title(f"CrimeGraph: Timeline View (Up to {limit})", fontsize=14, fontweight='bold')
        else:
            filtered_rels = relationships
            ax.set_title("CrimeGraph: Global Atomic Reconstruction", fontsize=14, fontweight='bold')

        for rel in filtered_rels:
            s_id = rel.get('source') or rel.get('subject_id')
            t_id = rel.get('target') or rel.get('object_id')
            if not s_id or not t_id: continue
            
            s_info = entity_lookup.get(s_id, {'display_name': s_id, 'type': 'Unknown'})
            t_info = entity_lookup.get(t_id, {'display_name': t_id, 'type': 'Unknown'})
            
            G.add_node(s_id, label=s_info['display_name'], type=s_info.get('type', 'Unknown'))
            G.add_node(t_id, label=t_info['display_name'], type=t_info.get('type', 'Unknown'))
            
            G.add_edge(s_id, t_id, label=f"[{rel.get('timestamp', '??')}]\n{rel.get('predicate', 'rel')}")

        if G.number_of_nodes() > 0:
            pos = nx.spring_layout(G, k=2.5, seed=42)
            node_labels = nx.get_node_attributes(G, 'label')
            colors = [color_map.get(G.nodes[n].get('type'), "#95a5a6") for n in G.nodes()]
            
            nx.draw(ax=ax, G=G, pos=pos, labels=node_labels, with_labels=True,
                    node_color=colors, node_size=3500, font_size=7, font_weight="bold",
                    edge_color="#bdc3c7", arrowsize=15, connectionstyle='arc3, rad = 0.1')
            
            edge_labels = {(u, v): d['label'] for u, v, d in G.edges(data=True)}
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='#c0392b', font_size=6, ax=ax)

        legend_handles = [mpatches.Patch(color=v, label=k) for k, v in color_map.items() if k != "Unknown"]
        ax.legend(handles=legend_handles, loc='upper left', bbox_to_anchor=(1.02, 1), title="Node Types", shadow=True)
        ax.axis('off')
        plt.draw()

    # UI Controls
    ax_slider = plt.axes([0.2, 0.1, 0.45, 0.03])
    time_slider = Slider(ax_slider, 'Time Scrub ', 0, len(timestamps) - 1, valinit=len(timestamps)-1, valstep=1)

    def update_time(val):
        current_view["mode"] = "Temporal"
        current_view["time"] = timestamps[int(val)]
        draw_graph()

    time_slider.on_changed(update_time)

    ax_btn = plt.axes([0.7, 0.09, 0.12, 0.05])
    btn_global = Button(ax_btn, 'Reset Global', color='#ecf0f1', hovercolor='#95a5a6')

    def reset_view(event):
        current_view["mode"] = "Global"
        draw_graph()

    btn_global.on_clicked(reset_view)

    draw_graph()
    plt.show()

if __name__ == "__main__":
    load_and_visualize()
