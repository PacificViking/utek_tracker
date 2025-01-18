import json

# Load resources.json
with open('resources.json', 'r') as f:
    resources_data = json.load(f)

# Load locations.json
with open('locations.json', 'r') as f:
    locations_data = json.load(f)

# Create a dictionary to store merged data
people_data = {
    "senders": [],
    "receivers": []
}

# Merge senders
for sender in resources_data['senders']:
    for loc_sender in locations_data['senders']:
        if sender['name'] == loc_sender['name']:
            merged_sender = {**sender, **loc_sender, "role": "distributor"}
            people_data['senders'].append(merged_sender)

# Merge receivers
for receiver in resources_data['receivers']:
    for loc_receiver in locations_data['receivers']:
        if receiver['name'] == loc_receiver['name']:
            merged_receiver = {**receiver, **loc_receiver, "role": "camp"}
            people_data['receivers'].append(merged_receiver)

# Save the merged data to people_data.json
with open('people_data.json', 'w') as f:
    json.dump(people_data, f, indent=4)

print("Merged data has been saved to people_data.json")