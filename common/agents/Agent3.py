import random
from common.base_agent import BaseAgent
from common.move import Move

# 127.0.0.1
# 128.179.154.221
# Student scipers, will be automatically used to evaluate your code
SCIPERS = ["390899", "Ton sciper"]

class Node:
    def __init__(self, position, real_cost=0, estimate_cost=0, previous_point=None):
        self.position = position
        self.real_cost = real_cost
        self.estimate_cost = estimate_cost
        self.f = real_cost + estimate_cost
        self.previous_point = previous_point
    
    def __lt__(self, node):
        return self.f < node.f

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
    
    def neighbor_positions(self, current_point):
        moves = [Move.LEFT.value, Move.DOWN.value, Move.UP.value,  Move.RIGHT.value]
        neighbor_positions = []
        for move in moves:
            

    
    def grid_with_obstacles(self):

        self.positions()

        grid_coordinates = []

        AVAILABLE = 0
        AVOID = 1
        OCCUPIED = 2

        print("GO")
        backward_train_position_x = self.all_trains[self.nickname]["position"][0]-self.move_vector[0]*self.cell_size
        backward_train_position_y = self.all_trains[self.nickname]["position"][1]-self.move_vector[1]*self.cell_size
        backward_train_position = (backward_train_position_x, backward_train_position_y)
        print("backward_train_position", backward_train_position)

        train_wagon_coordinates = []
        around_head_coordinates = []
        for train in self.all_trains:
            train_pos = tuple(self.all_trains[train]["position"])
            print("train_position", train_pos)
            train_wagon_coordinates.append(train_pos)
            for wagon_pos in self.all_trains[train]["wagons"]: 
                train_wagon_coordinates.append(tuple(wagon_pos))

            if train == self.nickname:
               continue
            else:
                moves = [Move.LEFT.value, Move.DOWN.value, Move.UP.value,  Move.RIGHT.value]
                for move in moves:
                   precaution_position=self.new_position(train_pos, move, 1)
                   #avoids duplicates
                   if precaution_position not in around_head_coordinates:
                        around_head_coordinates.append(precaution_position)

        #fill in grid coordinates
        for y in range(0, self.game_width, self.cell_size):
            grid_coordinates.append([])
            for x in range(0, self.game_height, self.cell_size):
                if (x,y) == backward_train_position:
                        grid_coordinates[y // self.cell_size].append(OCCUPIED)
                elif (x, y) in train_wagon_coordinates:   
                        grid_coordinates[y // self.cell_size].append(OCCUPIED)
                elif (x,y) in around_head_coordinates:
                    grid_coordinates[y // self.cell_size].append(AVOID)
                else:
                    grid_coordinates[y // self.cell_size].append(AVAILABLE)
    
        return grid_coordinates
        #for i in grid_coordinates:
        #     print(i, end ="\n")


    def path_to_point(self, goal):

        self.positions()

        #initialize the start node
        start = self.train_position
        start_point = Node(start)
        goal_point = Node(goal)
        #initialize open and closed lists
        points_to_evaluate = [start_point]
        evaluated_points = []
        #initialize distances and costs to record
        while len(points_to_evaluate):
            # chooses node with lowest cost
            current_point = min(points_to_evaluate)
            points_to_evaluate.remove(current_point)
            evaluated_points.append(current_point)

            
            if current_point == goal_point:
                best_path = []
                #reconstruct shortest path
                while current_point:
                    best_path.append(current_point.position)
                    current_point = current_point.previous_point
                #reconstruct the path in the correct order
                best_path = best_path[::-1] 

                return best_path ##############
            
            for neighboring_pos in get_neighboring_pos(current_node.position, grid_coordinates):
                neighbor_point = Node(neighboring_pos, current_point)
                #avoid duplicate assessing of points
                if neighbor_point in evaluated_points:
                    continue

                neighbor_point.g = current_point + 1
                neighbor_point.h = h(neighbor_point.position, goal_point.position)
                neighbor_point.f = neighbor_point.g + neighbor_point.h
                
                for point_to_evaluate in points_to_evaluate:
                    if neighbor_point == point_to_evaluate and neighbor_point.g > point_to_evaluate.g:
                        continue
                
                points_to_evaluate.append(neighbor_point)

            return None #No path available
                




    def get_move(self):

        obstacle_grid = self.grid_with_obstacles()

