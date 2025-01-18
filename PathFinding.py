import heapq
import math
import time
import json
from collections import defaultdict

class PathFinding:
    def __init__(self, n, obstacles):
        self.n = n
        self.obstacles = obstacles
        self.graph = self.build_graph()

    def build_graph(self):
        graph = {}
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for i in range(self.n):
            for j in range(self.n):
                if (i, j) in self.obstacles:
                    continue
                graph[(i, j)] = []
                for di, dj in directions:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < self.n and 0 <= nj < self.n and (ni, nj) not in self.obstacles:
                        graph[(i, j)].append(((ni, nj), math.sqrt(di**2 + dj**2)))
        return graph

    def dijkstra(self, start, goal):
        queue = [(0, start)]
        distances = {node: float('inf') for node in self.graph}
        distances[start] = 0
        previous_nodes = {node: None for node in self.graph}

        while queue:
            current_distance, current_node = heapq.heappop(queue)

            if current_node == goal:
                path = []
                while previous_nodes[current_node]:
                    path.append(current_node)
                    current_node = previous_nodes[current_node]
                path.append(start)
                return path[::-1]

            if current_distance > distances[current_node]:
                continue

            for neighbor, weight in self.graph[current_node]:
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(queue, (distance, neighbor))

        return []

    def a_star(self, start, goal):
        def heuristic(a, b):
            return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

        open_set = [(0, start)]
        g_score = {node: float('inf') for node in self.graph}
        g_score[start] = 0
        f_score = {node: float('inf') for node in self.graph}
        f_score[start] = heuristic(start, goal)
        previous_nodes = {node: None for node in self.graph}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                path = []
                while previous_nodes[current]:
                    path.append(current)
                    current = previous_nodes[current]
                path.append(start)
                return path[::-1]

            for neighbor, weight in self.graph[current]:
                tentative_g_score = g_score[current] + weight
                if tentative_g_score < g_score[neighbor]:
                    previous_nodes[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return []

class Sender:
    def __init__(self, name, x, y, resources):
        self.name = name
        self.x = x
        self.y = y
        self.resources = resources  # Dictionary of resource names to quantities

class Receiver:
    def __init__(self, name, x, y, needs):
        self.name = name
        self.x = x
        self.y = y
        self.needs = needs  # Dictionary of resource names to quantities

def load_data(locations_file, resources_file):
    with open(locations_file, 'r') as file:
        locations = json.load(file)
    with open(resources_file, 'r') as file:
        resources = json.load(file)
    return locations, resources

def save_resources(resources_file, resources):
    with open(resources_file, 'w') as file:
        json.dump(resources, file, indent=4)

def save_deliveries(deliveries_file, deliveries):
    with open(deliveries_file, 'w') as file:
        json.dump(deliveries, file, indent=4)

def match_senders_receivers(senders, receivers):
    resource_senders = defaultdict(list)
    resource_receivers = defaultdict(list)

    # Create priority queues for each resource type
    for sender in senders:
        for resource, quantity in sender.resources.items():
            heapq.heappush(resource_senders[resource], (-quantity, sender))

    for receiver in receivers:
        for resource, quantity in receiver.needs.items():
            heapq.heappush(resource_receivers[resource], (-quantity, receiver))

    matches = []
    for resource in resource_receivers:
        while resource_receivers[resource]:
            needed_quantity, receiver = heapq.heappop(resource_receivers[resource])
            needed_quantity = -needed_quantity

            if resource not in resource_senders or not resource_senders[resource]:
                print(f"Receiver {receiver.name} cannot get {resource}")
                continue

            available_quantity, sender = heapq.heappop(resource_senders[resource])
            available_quantity = -available_quantity

            if available_quantity >= needed_quantity:
                matches.append((sender, receiver, {resource: needed_quantity}))
                sender.resources[resource] -= needed_quantity
                receiver.needs[resource] -= needed_quantity

                if receiver.needs[resource] == 0:
                    del receiver.needs[resource]

                if sender.resources[resource] > 0:
                    heapq.heappush(resource_senders[resource], (-sender.resources[resource], sender))
            else:
                print(f"Receiver {receiver.name} cannot get enough {resource}")
                receiver.needs[resource] -= available_quantity
                matches.append((sender, receiver, {resource: available_quantity}))
                sender.resources[resource] = 0

    return matches

if __name__ == "__main__":
    locations_file = 'locations.json'
    resources_file = 'resources.json'
    deliveries_file = 'deliveries.json'

    locations, resources = load_data(locations_file, resources_file)

    n = locations['n']
    obstacles = locations['obstacles']
    senders_data = locations['senders']
    receivers_data = locations['receivers']

    senders = [Sender(s['name'], s['x'], s['y'], next(item['resources'] for item in resources['senders'] if item['name'] == s['name'])) for s in senders_data]
    receivers = [Receiver(r['name'], r['x'], r['y'], next(item['needs'] for item in resources['receivers'] if item['name'] == r['name'])) for r in receivers_data]

    path_finding = PathFinding(n, obstacles)

    # Ensure senders and receivers are not on obstacle locations
    for sender in senders:
        assert (sender.x, sender.y) not in obstacles, f"Sender at {(sender.x, sender.y)} is in obstacles"
    for receiver in receivers:
        assert (receiver.x, receiver.y) not in obstacles, f"Receiver at {(receiver.x, receiver.y)} is in obstacles"

    # Timing the matching algorithm
    start_time = time.time()
    matches = match_senders_receivers(senders, receivers)
    end_time = time.time()
    print(f"Matching algorithm time: {end_time - start_time} seconds")

    deliveries = []

    for sender, receiver, matched_resources in matches:
        print(f"Matched resources from {sender.name} to {receiver.name}: {matched_resources}")
        start = (sender.x, sender.y)
        goal = (receiver.x, receiver.y)
        
        # Timing A* algorithm
        start_time = time.time()
        a_star_path = path_finding.a_star(start, goal)
        end_time = time.time()
        delivery_time = len(a_star_path)
        print(f"A* path from {sender.name} to {receiver.name}: {a_star_path}")
        print(f"A* algorithm time: {end_time - start_time} seconds")

        for resource, quantity in matched_resources.items():
            deliveries.append({
                'sender': sender.name,
                'receiver': receiver.name,
                'time': delivery_time,
                'resource': resource,
                'quantity': quantity
            })

    # Save deliveries to the database
    save_deliveries(deliveries_file, deliveries)

    # Update resources in the database
    updated_senders = [{'name': s.name, 'resources': s.resources} for s in senders]
    updated_receivers = [{'name': r.name, 'needs': r.needs} for r in receivers]
    resources['senders'] = updated_senders
    resources['receivers'] = updated_receivers
    save_resources(resources_file, resources)