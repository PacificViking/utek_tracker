import json
import argparse

def load_names(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_names(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def check_and_update_name(file_path, name, entity_type, action):
    data = load_names(file_path)

    if action == "add":
        if name in data[entity_type]:
            return f"The name '{name}' has already been taken."
        data[entity_type].append(name)
    elif action == "remove":
        if name in data[entity_type]:
            data[entity_type].remove(name)
        else:
            return f"The name '{name}' does not exist."

    save_names(file_path, data)
    return f"The name '{name}' has been {action}ed successfully."

if __name__ == "__main__":
    names_file = 'names.json'
    parser = argparse.ArgumentParser(description='Check and update names database.')
    parser.add_argument('--name', required=True, help='Name to check or update.')
    parser.add_argument('--type', required=True, choices=['senders', 'receivers'], help='Type of entity (senders or receivers).')
    parser.add_argument('--action', required=True, choices=['add', 'remove'], help='Action to perform (add or remove).')

    args = parser.parse_args()
    result = check_and_update_name(names_file, args.name, args.type, args.action)
    print(result)