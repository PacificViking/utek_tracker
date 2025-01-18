import json
import argparse
import subprocess

def load_locations(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_locations(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def load_resources(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_resources(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def check_name(name, entity_type, action):
    result = subprocess.run(['python3', 'CheckName.py', '--name', name, '--type', entity_type, '--action', action], capture_output=True, text=True)
    return result.stdout.strip()

def update_locations(added_senders, removed_senders, added_receivers, removed_receivers, added_obstacles, removed_obstacles, updated_senders, updated_receivers):
    locations_file = 'locations.json'
    resources_file = 'resources.json'
    data = load_locations(locations_file)
    resources_data = load_resources(resources_file)

    # Update senders
    for sender in added_senders:
        check_result = check_name(sender['name'], 'senders', 'add')
        if "has already been taken" in check_result:
            print(check_result)
            return
        data['senders'].append(sender)
    for sender in removed_senders:
        check_name(sender['name'], 'senders', 'remove')
        data['senders'] = [s for s in data['senders'] if s['name'] != sender['name']]
        resources_data['senders'] = [s for s in resources_data['senders'] if s['name'] != sender['name']]

    # Update receivers
    for receiver in added_receivers:
        check_result = check_name(receiver['name'], 'receivers', 'add')
        if "has already been taken" in check_result:
            print(check_result)
            return
        data['receivers'].append(receiver)
    for receiver in removed_receivers:
        check_name(receiver['name'], 'receivers', 'remove')
        data['receivers'] = [r for r in data['receivers'] if r['name'] != receiver['name']]
        resources_data['receivers'] = [r for r in resources_data['receivers'] if r['name'] != receiver['name']]

    # Update obstacles
    for obstacle in added_obstacles:
        data['obstacles'].append(obstacle)
    for obstacle in removed_obstacles:
        data['obstacles'].remove(obstacle)

    # Update sender locations
    for updated_sender in updated_senders:
        for s in data['senders']:
            if s['name'] == updated_sender['name']:
                s['x'] = updated_sender['x']
                s['y'] = updated_sender['y']

    # Update receiver locations
    for updated_receiver in updated_receivers:
        for r in data['receivers']:
            if r['name'] == updated_receiver['name']:
                r['x'] = updated_receiver['x']
                r['y'] = updated_receiver['y']

    save_locations(locations_file, data)
    save_resources(resources_file, resources_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Update locations database.')
    parser.add_argument('--add_senders', type=json.loads, default='[]', help='Senders to add.')
    parser.add_argument('--remove_senders', type=json.loads, default='[]', help='Senders to remove.')
    parser.add_argument('--add_receivers', type=json.loads, default='[]', help='Receivers to add.')
    parser.add_argument('--remove_receivers', type=json.loads, default='[]', help='Receivers to remove.')
    parser.add_argument('--add_obstacles', type=json.loads, default='[]', help='Obstacles to add.')
    parser.add_argument('--remove_obstacles', type=json.loads, default='[]', help='Obstacles to remove.')
    parser.add_argument('--update_senders', type=json.loads, default='[]', help='Senders to update locations.')
    parser.add_argument('--update_receivers', type=json.loads, default='[]', help='Receivers to update locations.')

    args = parser.parse_args()
    update_locations(args.add_senders, args.remove_senders, args.add_receivers, args.remove_receivers, args.add_obstacles, args.remove_obstacles, args.update_senders, args.update_receivers)