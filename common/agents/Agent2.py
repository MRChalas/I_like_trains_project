import random
import numpy as np
from common.base_agent import BaseAgent
from common.move import Move
import common.agents.global_nav as gnav
import heapq

# FINAL THING TO ADD: Detect sides of delivery_zone to jnot have a unique pixel
"""
Size of delivery_zone?
Character not spawning?
Difference of level between agent and bot

Control edge cases, eg between train and wall, ...
"""
# 127.0.0.1
# 128.179.154.221
# Student scipers, will be automatically used to evaluate your code
SCIPERS = ["390899", "Ton sciper"]

#QUESTIONS:
#Est-ce qu'on a acces au temps restant? si oui on peut accelerer le train a la fin
#Comment ca fonctionne pour avoir des boosts de vitesse?
class Node:
    def __init__(self, position, g=0, h=0, parent=None):
        self.position = position  # (x, y)
        self.g = g  # Cost from start to this node
        self.h = h  # Heuristic cost to goal
        self.f = g + h  # Total cost
        self.parent = parent  # Parent node for path reconstruction
    def __lt__(self, other):
        return self.f < other.f  # For priority queue comparison
    
class Agent(BaseAgent):

    def positions(self):
        """
        Cordinates which are reused several times throughout the movement choice
        """
        #train coordinates
        self.train_position = self.all_trains[self.nickname]["position"]
        self.x_train_position = self.all_trains[self.nickname]["position"][0]
        self.y_train_position = self.all_trains[self.nickname]["position"][1]
        
        #previous train movement
        self.move_vector = self.all_trains[self.nickname]["direction"]
        self.previous_move = Move(tuple(self.move_vector))

        #delivery zone coordinates
        self.x_delivery_position = self.delivery_zone['position'][0]
        self.y_delivery_position = self.delivery_zone['position'][1]
    
    def closest_passenger(self):
        """
        Determines distance to closest passenger

        IN: None
        OUT: coordinates of closest passenger (int)
        """

        self.positions()

        #reset passenger positions
        passenger_positions = []

        #create list with current available passengers
        for i in range(len(self.passengers)):
            passenger_positions.append(self.passengers[i]['position'])
        closest_distance = float('inf')

        for pos in passenger_positions:
            distance = self.distance_to_point(self.x_train_position, self.y_train_position, pos[0], pos[1])
            #update closest passenger coordinates if distance is smaller than the on of the previous closest passenger
            if distance < closest_distance:
                closest_distance = distance
                closest_passenger = pos

        return closest_passenger

    def distance_to_point(self, current_x: int, current_y: int, point_x: int, point_y: int):
        """
        Calculates shortest distance between the train and a given point

        IN: train coordinates (x,y) and point coordinates (x,y)
        OUT: shortest distance (tuple of int)
        """

        return abs(current_x - point_x) + abs(current_y - point_y)
    
    
    def new_position(self, position:tuple, move: tuple, num_of_moves: int):
        """
        Determines new train position after n moves
        
        IN: tuple corresponding to move, number of times train wants to move
        OUT: new position coordinates
        """
        new_x = position[0] + (move[0] * self.cell_size) * num_of_moves
        new_y = position[1] + (move[1] * self.cell_size) * num_of_moves

        return (new_x, new_y)

    def available_grid_coordinates(self):
        """
        Determines all grid coordinates which have no obstacle

        IN: None
        OUT: available coordinates' grid (list of tuples)
        """

        #reset grid
        grid_coordinates = []

        #fill in grid coordinates depending on game parameters
        for x in range(0, self.game_width, self.cell_size):
            for y in range(0, self.game_height, self.cell_size):
                grid_coordinates.append((x,y))
        
        #remove train positions from available coordinates
        for train in self.all_trains:
            train_pos = tuple(self.all_trains[train]["position"])
            #avoid errors in case of duplicate removal of positions
            if train_pos in grid_coordinates: 
                grid_coordinates.remove(train_pos)

            #remove wagon positions from available coordinates
            for wagon_pos in self.all_trains[train]["wagons"]: 
                #avoid errors in case of duplicate removal of positions
                if tuple(wagon_pos) in grid_coordinates:
                    grid_coordinates.remove(tuple(wagon_pos))
        
        return grid_coordinates
    
    import heapq



    def path_to_point(self, start, goal):
        """
        A* algorithm to find the shortest path from start to goal.

        IN: start (tuple), goal (tuple)
        OUT: List of moves to reach the goal
        """
        self.positions()

        # Initialize open and closed lists
        open_list = []
        closed_list = set()

        # Create the start node
        start_node = Node(start, g=0, h=self.distance_to_point(start[0], start[1], goal[0], goal[1]))
        heapq.heappush(open_list, start_node)

        while open_list:
            # Get the node with the lowest f cost
            current_node = heapq.heappop(open_list)

            # If the goal is reached, reconstruct the path
            if current_node.position == goal:
                path = []
                while current_node.parent:
                    path.append(current_node.position)
                    current_node = current_node.parent
                path.reverse()
                return path

            # Add the current node to the closed list
            closed_list.add(tuple(current_node.position))

            # Generate neighbors
            moves = [Move.LEFT.value, Move.DOWN.value, Move.UP.value, Move.RIGHT.value]
            for move in moves:
                neighbor_pos = self.new_position(current_node.position, move, 1)

                # Skip if the neighbor is in the closed list or not in available positions
                if tuple(neighbor_pos) in closed_list or neighbor_pos not in self.available_grid_coordinates():
                    continue

                # Calculate g, h, and f costs
                g = current_node.g + self.cell_size
                h = self.distance_to_point(neighbor_pos[0], neighbor_pos[1], goal[0], goal[1])
                f = g + h

                # Check if the neighbor is already in the open list with a lower f cost
                neighbor_node = Node(neighbor_pos, g, h, current_node)
                if any(open_node.position == neighbor_pos and open_node.f <= f for open_node in open_list):
                    continue

                # Add the neighbor to the open list
                heapq.heappush(open_list, neighbor_node)

        # If no path is found, return None
        print("No path found. Open list is empty.")
        return None

    def get_move(self):
        moves = [Move.LEFT.value, Move.DOWN.value, Move.UP.value,  Move.RIGHT.value]
        self.positions()
        start = self.train_position
        goal = self.closest_passenger()
        path = self.path_to_point(start, goal)
        print(self.train_position, goal)
        print("Path:", path)
        for move in moves:
            pos_of_move = self.new_position(self.train_position, move, 1)
            print("POS of move", pos_of_move)
            if list(pos_of_move) == path:
                print("Move:", Move(move))
                return Move(move)