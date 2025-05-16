from common.base_agent import BaseAgent
from common.move import Move

SCIPERS = ["390899", "Ton sciper"]

class Node:
    """
    Determines node caracteristics used in path_to_point
    """
    def __init__(self, position, real_cost=0, estimate_cost=0, previous_point=None):
        self.position = tuple(position)
        self.real_cost = real_cost
        self.estimate_cost = estimate_cost
        self.total_cost = real_cost + estimate_cost
        self.previous_point = previous_point

    def __lt__(self, node):
        """
        Determines how to compare nodes
        
        IN: node
        OUT: Boolean (True if Node cost is lower)
        """
        return self.total_cost < node.total_cost
    
    def __eq__(self, node):
        """
        Determines how to define if nodes are equal
        
        IN: node
        OUT: Boolean (True if nodes have the same position)
        """
        #avoid error if type is not the same
        if not isinstance(node, Node):
            return False
        
        return self.position == node.position
    
    def __hash__(self):
        return hash(self.position)

class Agent(BaseAgent):
    def positions(self):
        """
        Coordinates and values reused several times throughout the code
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
        self.AVOID = 100
        self.OCCUPIED = float('inf')

    def distance_to_point(self, current_point: tuple, point: tuple):
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

    def neighbor_positions(self, current_point, grid_with_obstacles):
        """
        Determines coordinates of positions surrounding current point

        IN: current point (tuple), grid with obstacles (list of int)
        OUT: list of neighbor positions
        """
        self.positions()
        moves = [Move.LEFT.value, Move.DOWN.value, Move.UP.value,  Move.RIGHT.value]
        neighbor_positions = []
        for move in moves:
            #find neighboring positions
            x_neighbor_pos = current_point[0] + move[0]*self.cell_size
            y_neighbor_pos = current_point[1] + move[1]*self.cell_size
            #check if coordinates within range
            if 0 <= (x_neighbor_pos // self.cell_size) < len(grid_with_obstacles[0]) and 0<= (y_neighbor_pos // self.cell_size) < len(grid_with_obstacles):
                #check if position is not occupied
                if grid_with_obstacles[y_neighbor_pos // self.cell_size][x_neighbor_pos // self.cell_size] != self.OCCUPIED:
                    neighbor_positions.append((x_neighbor_pos, y_neighbor_pos))

            return neighbor_positions

    def grid_with_obstacles(self):
        """
        Determines cost of cells within playing zone
        
        IN: none
        OUT: grid with costs (list of lists)
        """

        self.positions()

        #reset grid and obstacle positions
        grid_coordinates = []
        train_wagon_coordinates = []
        around_head_coordinates = []

        #determines position if train goes backwards
        backward_train_position_x = self.all_trains[self.nickname]["position"][0]-self.move_vector[0]*self.cell_size
        backward_train_position_y = self.all_trains[self.nickname]["position"][1]-self.move_vector[1]*self.cell_size
        backward_train_position = (backward_train_position_x, backward_train_position_y)

        #determine obstacle positions
        for train in self.all_trains:
            train_pos = tuple(self.all_trains[train]["position"])
            train_wagon_coordinates.append(train_pos)
            for wagon_pos in self.all_trains[train]["wagons"]: 
                train_wagon_coordinates.append(tuple(wagon_pos))   
        
            #determine positions to avoid around train heads
            if train == self.nickname:
               continue
            else:
                moves = [Move.LEFT.value, Move.DOWN.value, Move.UP.value,  Move.RIGHT.value]
                for move in moves:
                   precaution_position=self.new_position(train_pos, move, 1)
                   #avoids duplicates
                   if precaution_position not in around_head_coordinates:
                        around_head_coordinates.append(precaution_position)

        #fill in grid coordinates with costs
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

        return grid_coordinates

    def avoid_obstacles(self):
        """
        determines movement to choose to avoid wall
        
        IN:
        OUT:
        """
        self.positions()
        grid = self.grid_with_obstacles()
        moves = [Move.LEFT.value, Move.DOWN.value, Move.UP.value,  Move.RIGHT.value]
        moves.remove(tuple(-i for i in self.move_vector))
        safe_move = None
        possible_move = None

        for move in moves:
            new_pos = self.new_position(self.train_position, move, 1)
            if 0 <= new_pos[1]//self.cell_size < len(grid) and 0 <= new_pos[0]//self.cell_size < len(grid[0]):
                if grid[new_pos[1]//self.cell_size][new_pos[0]//self.cell_size] != self.OCCUPIED:
                    if grid[new_pos[1]//self.cell_size][new_pos[0]//self.cell_size] != self.AVOID:
                        safe_move = move
                    possible_move = move

        if possible_move is None and safe_move is None:
            print("NO MOOOVE")
            return Move.UP
        return safe_move if safe_move is not None else possible_move            
              
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

    def closest_delivery_zone_point(self):
        """
        Determines best delivery zone point to aim for
        
        IN: None
        OUT: (x,y) coordinates (tuple of int)
        """
        pass

    def on_the_way(self):
        """
        Determines if there is a passenger near the train when he is moving towards the delivery zone
        
        IN: None
        OUT: Boolean (True if there is a passenger near the train)
        """
        closest_passenger = self.closest_passenger()
        distance_to_passenger = self.distance_to_point(self.train_position, closest_passenger)
        if distance_to_passenger < 120: #120 is arbitrary
            return True
        return False
    
    def close_to_delivery(self):
        """
        Determines if the train is close to the delivery zone when it is trying to go towards a passenger
        
        IN: None
        OUT: Boolean (True if delivery zone is close to train)
        """

        self.positions()

        distance_to_delivery = self.distance_to_point(self.train_position, self.delivery_zone_pos)
        if distance_to_delivery < 80 and len(self.all_trains[self.nickname]['wagons'])>=2: #80 is arbitrary, 2 just makes sense in practice
            return True
        return False

    def path_to_point(self, goal:tuple):
        """
        A* algorithm to determine optimal path to get to wanted point
        
        IN: goal coordinates (x,y) tuple of int
        OUT: path (list of coordinates)
        """
        self.positions()
        grid = self.grid_with_obstacles()

        #initializes start and goal nodes
        #change goal if already on goal
        #if self.train_position == goal:
        #    print("already on goal")
        #    if len(self.all_trains[self.nickname]['wagons'])>=1:
        #        goal = self.delivery_zone_pos
        #    else:
        #        goal = self.closest_passenger()
        
        start_point = Node(self.train_position)
        print("GOAL", goal, "TRAIN", self.train_position)
        goal_point = Node(goal)

        #initialize open and closed lists
        points_to_evaluate = [start_point]
        evaluated_points = set()

        #determine best path
        while points_to_evaluate:
            #choose point with lowest cost
            points_to_evaluate.sort(key=lambda node: node.total_cost) #sorting conditions determine by __lt__
            current_point = points_to_evaluate.pop(0)

            #skip point if already evaluated
            if current_point in evaluated_points:
                continue

            #reconstruct shortest path if goal has been reached
            if current_point == goal_point:
                print("goal_reached", goal)
                best_path = []
                while current_point.previous_point:
                    best_path.append(current_point.position)
                    current_point = current_point.previous_point
                print("PATH", best_path)
                return best_path[-1]
            
            evaluated_points.add(current_point)

            #evaluate neighbor positions
            for neighbor_pos in self.neighbor_positions(current_point.position, grid):
                x , y = neighbor_pos
                cost_of_move = grid[y//self.cell_size][x//self.cell_size]

                #update costs
                neighbor_point = Node(neighbor_pos, previous_point=current_point)
                neighbor_point.real_cost = current_point.real_cost + cost_of_move
                neighbor_point_pos = neighbor_point.position
                neighbor_point.estimate_cost = self.distance_to_point(neighbor_point_pos, goal)
                neighbor_point.total_cost = neighbor_point.real_cost + neighbor_point.estimate_cost

                #check if neighbor has already been evaluated
                skip_neighbor = False
                for point in points_to_evaluate:
                    if neighbor_point == point and neighbor_point.real_cost >= point.real_cost:
                        skip_neighbor = True
                        break
                if not skip_neighbor:
                    points_to_evaluate.append(neighbor_point)

        print("no path found")
        return None
        
    def get_direction(self, wanted_pos):
        moves = [Move.LEFT.value, Move.DOWN.value, Move.UP.value,  Move.RIGHT.value]
        for move in moves:
            pos_after_move = self.new_position(self.train_position, move, 1)
            if list(pos_after_move) == wanted_pos:
                return move

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
            print("DELIVER == 0", len(self.all_trains[self.nickname]['wagons']))
            passenger_pos = self.closest_passenger()
            path = self.path_to_point(passenger_pos)
        
        else:
            passenger_on_way = self.on_the_way()
            #check if train is to long
            if len(self.all_trains[self.nickname]['wagons'])>=10:
                path = self.path_to_point(self.delivery_zone_pos)  
            elif passenger_on_way:
                passenger_pos = self.closest_passenger()
                path = self.path_to_point(passenger_pos)
            else:
                path = self.path_to_point(self.delivery_zone_pos) 

        if path:
            move = self.get_direction(list(path))
        else:
            move = self.avoid_obstacles()
            print("Move", Move(move))

        return Move(move)      



    


