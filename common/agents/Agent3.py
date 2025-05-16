import random
from common.base_agent import BaseAgent
from common.move import Move

# 127.0.0.1
# 128.179.154.221
# Student scipers, will be automatically used to evaluate your code
SCIPERS = ["390899", "Ton sciper"]

class Node:
    def __init__(self, position, real_cost=0, estimate_cost=0, previous_point=None):
        self.position = tuple(position)
        self.real_cost = real_cost
        self.estimate_cost = estimate_cost
        self.total_cost = real_cost + estimate_cost
        self.previous_point = previous_point
    
    def __lt__(self, node):
        return self.total_cost < node.total_cost
    
    def __eq__(self, node):
        #avoid error if type is not the same
        if not isinstance(node, Node):
            return False
        return self.position == node.position
    
    def __hash__(self):
        return hash(self.position)  # Use position as the hashable attribute

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
        self.delivery_zone_pos = self.delivery_zone['position']
        self.x_delivery_position = self.delivery_zone['position'][0]
        self.y_delivery_position = self.delivery_zone['position'][1]

        #grid costs
        self.AVAILABLE = 0
        self.AVOID = 1000
        self.OCCUPIED = float('inf')

    def distance_to_point(self, current_point, point):
        """
        Calculates shortest distance between the train and a given point

        IN: train coordinates (x,y) and point coordinates (x,y)
        OUT: shortest distance (tuple of int)
        """

        return abs(current_point[0] - point[0]) + abs(current_point[1] - point[1])

    def new_position(self, position:tuple, move: tuple, num_of_moves: int):
        """
        Determines new train position after n moves
        
        IN: tuple corresponding to move, number of times train wants to move
        OUT: new position coordinates
        """
        new_x = position[0] + (move[0] * self.cell_size) * num_of_moves
        new_y = position[1] + (move[1] * self.cell_size) * num_of_moves

        return (new_x, new_y)
    
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
            distance = self.distance_to_point(self.train_position, pos)
            #update closest passenger coordinates if distance is smaller than the on of the previous closest passenger
            if distance < closest_distance:
                closest_distance = distance
                closest_passenger = pos

        return closest_passenger
    
    def neighbor_positions(self, current_point, grid_with_obstacles):
        self.positions()
        moves = [Move.LEFT.value, Move.DOWN.value, Move.UP.value,  Move.RIGHT.value]
        neighbor_positions = []
        for move in moves:
            #find neighboring pos
            x_neighbor_pos = current_point[0] + move[0]*self.cell_size
            y_neighbor_pos = current_point[1] + move[1]*self.cell_size
            if 0 <= (x_neighbor_pos // self.cell_size) < len(grid_with_obstacles[0]) and 0<= (y_neighbor_pos // self.cell_size) < len(grid_with_obstacles):
                if grid_with_obstacles[y_neighbor_pos // self.cell_size][x_neighbor_pos // self.cell_size] != self.OCCUPIED:
                    neighbor_positions.append((x_neighbor_pos, y_neighbor_pos))
        return neighbor_positions

    def grid_with_obstacles(self):

        self.positions()
        grid_coordinates = []

        

        backward_train_position_x = self.all_trains[self.nickname]["position"][0]-self.move_vector[0]*self.cell_size
        backward_train_position_y = self.all_trains[self.nickname]["position"][1]-self.move_vector[1]*self.cell_size
        backward_train_position = (backward_train_position_x, backward_train_position_y)
        

        train_wagon_coordinates = []
        around_head_coordinates = []
        for train in self.all_trains:
            train_pos = tuple(self.all_trains[train]["position"])
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
        for y in range(0, self.game_height, self.cell_size):
            grid_coordinates.append([])
            for x in range(0, self.game_width, self.cell_size):
                if (x,y) == backward_train_position:
                        grid_coordinates[y // self.cell_size].append(self.OCCUPIED)
                elif (x, y) in train_wagon_coordinates:   
                        grid_coordinates[y // self.cell_size].append(self.OCCUPIED)
                elif (x,y) in around_head_coordinates:
                    grid_coordinates[y // self.cell_size].append(self.AVOID)
                else:
                    grid_coordinates[y // self.cell_size].append(self.AVAILABLE)

        
        #for i in grid_coordinates:
        #     print(i, end ="\n")
        return grid_coordinates

    def avoid_wall(self):
        self.positions()
        grid = self.grid_with_obstacles()
        moves = [Move.LEFT.value, Move.DOWN.value, Move.UP.value,  Move.RIGHT.value]
        moves.remove((self.move_vector[0]*(-1), self.move_vector[1]*(-1)))
        possible_move = None
        choice_of_move = None
        for move in moves:
            new_pos = self.new_position(self.train_position, move, 1)
            if 0 <= new_pos[1]//self.cell_size < len(grid) and 0 <= new_pos[0]//self.cell_size < len(grid[0]):
                if grid[new_pos[1]//self.cell_size][new_pos[0]//self.cell_size] != self.OCCUPIED:
                    if grid[new_pos[1]//self.cell_size][new_pos[0]//self.cell_size] != self.AVOID:
                        choice_of_move = move
                    possible_move = move
        if possible_move is None and choice_of_move is None:
            #print("NO MOOOVE")
            return Move.UP
        return choice_of_move if choice_of_move is not None else possible_move

    def path_to_point(self, goal):

        self.positions()
        grid = self.grid_with_obstacles()

        #initialize the start node
        if self.train_position == self.delivery_zone_pos:
            goal = self.closest_passenger()

        start = self.train_position
        start_point = Node(start)
        goal_point = Node(goal)

        #initialize open and closed lists
        points_to_evaluate = [start_point]
        evaluated_points = set()

        #initialize distances and costs to record
        while points_to_evaluate:
            #if len(points_to_evaluate) < 100:
            #    print(len(points_to_evaluate))
            # chooses node with lowest cost
            points_to_evaluate.sort(key=lambda node: node.total_cost)
            current_point = points_to_evaluate.pop(0)
            #current_point = min(points_to_evaluate)##############

            #skip if already evaluated
            if current_point in evaluated_points:
                continue

            if current_point == goal_point:
                #print("goal reached")
                best_path = []
                #reconstruct shortest path
                while current_point.previous_point:
                    best_path.append(current_point.position)
                    current_point = current_point.previous_point
                #reconstruct the path in the correct order
                if best_path:
                    return best_path[-1]
                else:
                    return self.avoid_wall()
                
            
            #points_to_evaluate.remove(current_point)
            evaluated_points.add(current_point)

            for neighbor_pos in self.neighbor_positions(current_point.position, grid):
                #neighbor_point = Node(neighboring_pos, previous_point=current_point)
                #avoid duplicate assessing of points
                #if neighbor_point in evaluated_points:
                #    continue

                x,y = neighbor_pos
                cost_of_move = grid[y//self.cell_size][x//self.cell_size]

                neighbor_point = Node(neighbor_pos, previous_point=current_point)
                neighbor_point.real_cost = current_point.real_cost + cost_of_move
                neighbor_point_pos = neighbor_point.position
                neighbor_point.estimate_cost = self.distance_to_point(neighbor_point_pos, goal)
                neighbor_point.total_cost = neighbor_point.real_cost + neighbor_point.estimate_cost

                skip_neighbor = False
                for point_to_evaluate in points_to_evaluate:
                    if neighbor_point == point_to_evaluate and neighbor_point.real_cost >= point_to_evaluate.real_cost:
                        skip_neighbor = True
                        break
                        #continue
                if not skip_neighbor:
                    points_to_evaluate.append(neighbor_point)
        
        print("no path found")
        return None #No path available
                
    def close_to_delivery(self):
        """
        Determines if the train is close to the delivery zone when it is trying to go towards a passenger
        
        IN: None
        OUT: Boolean
        """

        train_pos = self.all_trains[self.nickname]["position"]

        #distance to delivery position
        delivery_pos = self.delivery_zone['position']
        distance_to_delivery = self.distance_to_point(train_pos, delivery_pos)
        if distance_to_delivery < 80 and len(self.all_trains[self.nickname]['wagons'])>=2: #80 is arbitrary, 2 just makes sense in practice
            return True
        return False
    
    def on_the_way(self):
        """
        Determine if there is a passenger near the train when he is moving towards the delivery zone
        
        IN: None
        OUT: Boolean
        """

        closest_passenger = self.closest_passenger()
        distance_to_passenger = abs(closest_passenger[0] - self.x_train_position) + abs(closest_passenger[1] - self.y_train_position)
        if distance_to_passenger < 120: #120 is arbitrary
            return True
        return False

    def get_direction(self, path):
        moves = [Move.LEFT.value, Move.DOWN.value, Move.UP.value,  Move.RIGHT.value]
        for move in moves:
            pos_of_move = self.new_position(self.train_position, move, 1)
            if list(pos_of_move) == path:
                #print("Move:", Move(move))
                return Move(move)

    def get_move(self):
        """
        Determines which coordinates to go to and how to move accordingly
        
        IN: None
        OUT: Move
        """
        self.positions()
        DELIVER = 0

        #determine if train is long enough to go deliver passengers
        if len(self.all_trains[self.nickname]['wagons'])>=1:
            DELIVER = 1

        if DELIVER == 0:
            passenger_pos = self.closest_passenger()
            path = self.path_to_point(passenger_pos)
        
        else:
            passenger_on_way = self.on_the_way()
            #check if train is to long
            if len(self.all_trains[self.nickname]['wagons'])>=7:
                print("TOO LONG")
                path = self.path_to_point(self.delivery_zone_pos)  
            elif passenger_on_way:
                print("Passenger on the way")
                passenger_pos = self.closest_passenger()
                path = self.path_to_point(passenger_pos)
            else:
                "delivery zone"
                path = self.path_to_point(self.delivery_zone_pos) 

        if path:
            print("path")
            move = self.get_direction(list(path))
        else:
            print("AAAAVOOOID OBSTACCCCLE")
            move = self.avoid_wall()
            print("Move", Move(move))

        return Move(move) 

        

