import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
You are a Forensic Data Architect. Your task is to transform witness statements into an Atomic Temporal Scene Graph.

OBJECTIVE:
Everything must be a node. Do not use internal fields for physical traits or emotions. Link them as separate entities.

ENTITY TYPES:
- Person: The actors (e.g., P1, P2).
- Object: Physical items (e.g., O1).
- Location: The setting (e.g., L1).
- Emotion: Abstract internal states (e.g., E1 - "Terrified", E2 - "Triumphant").
- Attribute: Physical traits or clothing (e.g., A1 - "Blue Hair", A2 - "Jagged Scar").

RELATIONSHIP TYPES:
- Use [is_feeling] to link a Person to an Emotion.
- Use [has_appearance] to link a Person to an Attribute.
- Use [action] predicates (e.g., "lunged", "shouted") for Person-to-Object or Person-to-Person interactions.

INSTRUCTIONS:
- Atomize everything: If a man is "tall" and has "fair skin," create two separate Attribute nodes.
- Temporal Accuracy: Every relationship (including feelings and appearances) needs a timestamp. 
- IDs: Keep IDs consistent (e.g., P1 always refers to the same suspect).

OUTPUT: Valid JSON with "entities" and "relationships" keys.
STRICT KEY NAMING:
- Use "id" for entity identifiers.
- Use "source" and "target" for relationships.
- Do not use "entity_id", "subject_id", or "object_id".

"""

def generate_scene_graph(text):
    response = client.models.generate_content(
        model="gemini-3-flash-preview", # Or "gemini-1.5-pro"
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
        ),
        contents=text
    )
    
    return json.loads(response.text)

if __name__ == "__main__":
    report_text = """
Report : The 26/11 Leopold Cafe Attack
Type: Real-World / Tactical Terror Incident (2008)

Focus: Rapid movement, aggression vs. panic, and high-fidelity weapon/backpack attributes.

"At 9:48 PM on November 26, 2008, two young males, both in their early 20s and wearing heavy blue backpacks and casual cargo trousers, approached the entrance of Leopold Cafe in Colaba. The lead attacker, carrying an AK-47 with a taped double magazine, looked cold and focused.

At 9:50 PM, the first grenade was tossed into the crowded dining area. The sound was deafening. A silver-haired tourist, clutching a beer bottle, looked frozen with shock. The second attacker, who was smirking, began firing into the mezzanine. At 9:51 PM, a waiter named Akash, described as a lanky man in a white uniform shirt soaked in red wine and blood, lunged behind a wooden refrigerator. He felt pure adrenaline.

Thirty seconds later, the attackers exited the cafe and headed toward the Taj Mahal Palace Hotel. They appeared rushed but methodical. Behind them, the historic cafe was a scene of chaotic agony, with the smell of gunpowder and fried food hanging in the air. By 10:00 PM, Mumbai police arrived, looking confused and under-equipped as they encountered the first major casualties of the night."
    """ 
    
    print("Generating scene graph...")
    scene_graph = generate_scene_graph(report_text)
    
    # SAVE DIRECTLY TO FILE
    with open('scene_graph.json', 'w') as f:
        json.dump(scene_graph, f, indent=4)
    
    print("Success! Scene graph saved to 'scene_graph.json'.")
