import json
import argparse

def load_resources(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_resources(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def load_names(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def update_resources(sender_resources, receiver_needs):
    resources_file = 'resources.json'
    names_file = 'names.json'
    resources_data = load_resources(resources_file)
    names_data = load_names(names_file)

    # Update sender resources
    for sender in sender_resources:
        found = False
        for s in resources_data['senders']:
            if s['name'] == sender['name']:
                s['resources'] = sender['resources']
                found = True
                break
        if not found:
            if sender['name'] in names_data['senders']:
                resources_data['senders'].append(sender)
            else:
                print(f"Sender {sender['name']} does not exist in names database.")

    # Update receiver needs
    for receiver in receiver_needs:
        found = False
        for r in resources_data['receivers']:
            if r['name'] == receiver['name']:
                r['needs'] = receiver['needs']
                found = True
                break
        if not found:
            if receiver['name'] in names_data['receivers']:
                resources_data['receivers'].append(receiver)
            else:
                print(f"Receiver {receiver['name']} does not exist in names database.")

    save_resources(resources_file, resources_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Update resources database.')
    parser.add_argument('--sender_resources', type=json.loads, default='[]', help='Sender resources to update.')
    parser.add_argument('--receiver_needs', type=json.loads, default='[]', help='Receiver needs to update.')

    args = parser.parse_args()
    update_resources(args.sender_resources, args.receiver_needs)