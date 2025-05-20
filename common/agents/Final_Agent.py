import random
from common.base_agent import BaseAgent
from common.move import Move

# Local: 127.0.0.1
# Server: 128.179.154.221
# Student scipers, will be automatically used to evaluate your code
SCIPERS = ["390899", "398584"]

class Node:
    """
    Determines node comparison caracteristics and values to track 
    """
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
        return isinstance(node, Node) and self.position == node.position
    
    def __hash__(self):
        return hash(self.position)  

class Agent(BaseAgent):
    def positions(self):
        """
        Values which are reused several times throughout the code
        """
        #possible moves
        self.moves = [Move.LEFT.value, Move.DOWN.value, Move.UP.value, Move.RIGHT.value]

        #train coordinates
        self.train_position = self.all_trains[self.nickname]["position"]
        self.x_train_position = self.all_trains[self.nickname]["position"][0]
        self.y_train_position = self.all_trains[self.nickname]["position"][1]
        
        #previous train movement
        self.move_vector = self.all_trains[self.nickname]["direction"]
        self.previous_move = Move(tuple(self.move_vector))

        #delivery zone information
        self.delivery_zone_pos = self.delivery_zone['position']
        self.x_delivery_position = self.delivery_zone['position'][0]
        self.y_delivery_position = self.delivery_zone['position'][1]
        self.delivery_zone_perimeter = (2*self.delivery_zone['width']/self.cell_size  \
                                        +   2*self.delivery_zone['height']/self.cell_size) + 4
        self.ultimate_strategy=False

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

    def new_position(self, position:tuple, move:tuple, steps = 1):
        """
        Determines new train position after n moves
        
        IN: tuple corresponding to move, number of times train wants to move
        OUT: new position coordinates
        """
        new_x = position[0] + (move[0] * self.cell_size) * steps
        new_y = position[1] + (move[1] * self.cell_size) * steps

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
        passenger_positions = [passenger['position'] for passenger in self.passengers]

        closest_distance = float('inf')
        for pos in passenger_positions:
            distance = self.distance_to_point(self.train_position, pos)
            #update closest passenger coordinates if distance is smaller
            if distance < closest_distance:
                closest_distance = distance
                closest_passenger = pos

        return closest_passenger

    def closest_delivery_zone_point(self):
        """
        Determines closest point within delivery zone train can go to
        
        IN: None
        OUT: (x,y) coordinates of closest delivery zone point
        """
        closest_delivery_point = (0,0)
        min_distance = float('inf')

        #loop through all delivery zone points
        for i in range(self.delivery_zone['height']//self.cell_size):
            for j in range(self.delivery_zone['width']//self.cell_size):
                x_position = self.x_delivery_position + i*self.cell_size
                y_position = self.y_delivery_position + j*self.cell_size
                point = (x_position, y_position)
                distance = self.distance_to_point(self.train_position, point)

                if distance < min_distance:
                    min_distance = distance
                    closest_delivery_point = point
        print(closest_delivery_point)
        return tuple(closest_delivery_point)
     
    def get_neighbors(self, current_point, grid_with_obstacles):
        """
        Determine coordinates neighboring current point
        
        IN: coordinates of point, grid with costs
        OUT: available neighbor positions
        """

        self.positions()
        neighbor_positions = []
        for move in self.moves:
            x_neighbor_pos = current_point[0] + move[0]*self.cell_size
            y_neighbor_pos = current_point[1] + move[1]*self.cell_size
            #check if neighboring position is within bounds
            if 0 <= (x_neighbor_pos // self.cell_size) < len(grid_with_obstacles[0]) and 0<= (y_neighbor_pos // self.cell_size) < len(grid_with_obstacles):
                if grid_with_obstacles[y_neighbor_pos // self.cell_size][x_neighbor_pos // self.cell_size] != self.OCCUPIED:
                    neighbor_positions.append((x_neighbor_pos, y_neighbor_pos))

        return neighbor_positions

    def grid_with_obstacles(self):
        """
        Generate grid with costs of cells
        
        IN: None
        OUT: list of list containing cost of going on each cell
        """
        self.positions()

        #reset grid
        grid_coordinates = []

        #determine pos train would be on if it moved backwards
        backward_train_position_x = self.all_trains[self.nickname]["position"][0]-self.move_vector[0]*self.cell_size
        backward_train_position_y = self.all_trains[self.nickname]["position"][1]-self.move_vector[1]*self.cell_size
        backward_train_position = (backward_train_position_x, backward_train_position_y)
        
        #determine positions to avoid 
        train_wagon_coordinates = []
        around_head_coordinates = []
        for train in self.all_trains:
            train_pos = tuple(self.all_trains[train]["position"])
            train_wagon_coordinates.append(train_pos)
            for wagon_pos in self.all_trains[train]["wagons"]: 
                train_wagon_coordinates.append(tuple(wagon_pos))

            #avoid making perimeter around own train unavailable
            if train == self.nickname:
               continue
            else:
                for move in self.moves:
                   precaution_position=self.new_position(train_pos, move)
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

        return grid_coordinates

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
    
    def around_head(self):
        """
        Determines coordinates which could possibly be filled by train heads after next move
       
        IN: None
        OUT: list of tuples containing coordinates
        """

        # Reset head positions
        head_positions=[]

        for train in self.all_trains:
            #avoid making perimeter around own head unavailable
            if train == self.nickname:
               continue
            else:
                head_position = tuple(self.all_trains[train]["position"])
                #avoids duplicates
                if head_position not in head_positions:
                    head_positions.append(head_position)
                for move in self.moves:
                   precaution_position=self.new_position(head_position, move, 1)
                   #avoids duplicates
                   if precaution_position not in head_positions:
                        head_positions.append(precaution_position)

        return head_positions

    def delivery_zone(self):
        """
        Determines positions covered by delivery zone
        
        IN: None
        OUT: list of (x,y) delivery zone coordinates 
        """

        self.positions()

        #reset delivery points
        delivery_points=[]

        for i in range(self.delivery_zone['height']//self.cell_size):
            for j in range(self.delivery_zone['width']//self.cell_size):
                x_position = self.x_delivery_position + (i*self.cell_size)
                y_position = self.y_delivery_position + (j*self.cell_size)
                delivery_points.append((x_position, y_position))

        return delivery_points

    def zone_around_delivery(self):
        """
        Determines coordinates of cells around delivery zone
        
        IN: None
        OUT: list of tuple
        """
        
        #reset delivery positions
        delivery_zone_list=[]

        for i in range(-1,int(self.delivery_zone['width']/(self.cell_size))+1):
                #positions above delivery zone
                x1_position = self.x_delivery_position + i*self.cell_size
                y1_position = self.y_delivery_position - self.cell_size

                #positions below delivery zone
                x2_position = self.x_delivery_position + i*self.cell_size
                y2_position = self.y_delivery_position + self.delivery_zone['height'] + self.cell_size

                delivery_zone_list.append((x1_position,y1_position))
                delivery_zone_list.append((x2_position,y2_position))

        for j in range(0,int(self.delivery_zone['height']/(self.cell_size))):
                #positions to the left of the delivery zone
                x1_position = self.x_delivery_position - self.cell_size
                y1_position = self.y_delivery_position + j*self.cell_size

                #positions to the right of the delivery zone
                x2_position = self.x_delivery_position + self.delivery_zone['width']
                y2_position = self.y_delivery_position + j*self.cell_size

                delivery_zone_list.append((x1_position,y1_position))
                delivery_zone_list.append((x2_position,y2_position))

        return delivery_zone_list

    def path_to_point(self, goal:tuple):
        """
        A* path finding algorithm to determine best move to choose
        
        IN: coordinates of goal point 
        OUT: next coordinates to go onto if a path is found, otherwise None
        """

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
            # chooses node with lowest cost
            points_to_evaluate.sort(key=lambda node: node.total_cost)
            current_point = points_to_evaluate.pop(0)

            #skip if already evaluated
            if current_point in evaluated_points:
                continue

            if current_point == goal_point:
                best_path = []
                #reconstruct shortest path
                while current_point.previous_point:
                    best_path.append(current_point.position)
                    current_point = current_point.previous_point
                #reconstruct the path in the correct order
                if best_path:
                    return best_path[-1]
                
            
            #points_to_evaluate.remove(current_point)
            evaluated_points.add(current_point)

            for neighbor_pos in self.get_neighbors(current_point.position, grid):

                x,y = neighbor_pos
                cost_of_move = grid[y//self.cell_size][x//self.cell_size]

                #update costs
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
                if not skip_neighbor:
                    points_to_evaluate.append(neighbor_point)
    
        return None #No path available

    def other_move(self, point:tuple):
        """
        Determines direction to take to get to closest passenger

        IN: coordinates of the point the train is trying to reach (int, int)
        OUT: best move the train can take (eg: Move.UP, Move.LEFT, ...)
        """

        self.positions()

        #reset movement variables
        moves = self.moves
        shortest_distance = float('inf')
        best_move = None
        best_safe_move = None
        possible_moves = []
        possible_safe_moves = []
        other_possibility = []
        other_safe_possibility = []

        #remove move opposite to the previous one
        opposite_m = tuple(-i for i in self.move_vector)
        moves.remove(opposite_m)

        for move in moves:
            #calculate distance between possible new position and point train is trying to reach
            new_pos = self.new_position(self.train_position, move) 
            distance = self.distance_to_point(new_pos, point)

            #determine available coordinates
            available_positions = self.available_grid_coordinates()
            head_positions = self.around_head()

            #check if wanted move does not move onto unavailable position
            if tuple(new_pos) in available_positions:
                    #differentiates possible positions form safe positions
                    possible_moves.append(move)
                    if tuple(new_pos) not in head_positions:
                        possible_safe_moves.append(move)
                    #check if move brings closer to the wanted point than previous move
                    if distance < shortest_distance:
                        shortest_distance = distance
                        best_move = move 
                        if tuple(new_pos) not in head_positions:
                            best_safe_move = move
                    if distance == shortest_distance:
                        other_possibility.append(move)
                        if tuple(new_pos) not in head_positions:
                            other_safe_possibility.append(move)
        
        #determine distance if turning around
        if point == self.delivery_zone['position']:
            turn_x = self.x_train_position + opposite_m[0] * self.cell_size
            turn_y = self.y_train_position + opposite_m[1] * self.cell_size
            turn_around = self.distance_to_point((turn_x, turn_y), point)

            #check if turning around would be the best choice
            if distance > turn_around:
                if len(other_safe_possibility) > 0:
                    if len(other_safe_possibility) == 1:
                        best_safe_move = other_safe_possibility[0]
                    else:
                        direction = random.randint(0, len(other_safe_possibility)-1)
                        best_safe_move = other_safe_possibility[direction]
                elif len(other_possibility) > 0:
                    if len(other_possibility) == 1:
                        best_move = other_possibility[0]
                    else:
                        direction = random.randint(0, len(other_possibility)-1)
                        best_move = other_possibility[direction]
        
        #choose best move
        if best_move == best_safe_move:
            final_move = best_move
        elif best_safe_move is not None:
            final_move = best_safe_move 
        elif len(other_safe_possibility) > 0:
            if len(other_safe_possibility) == 1:
                final_move = other_safe_possibility[0]
            else:
                direction = random.randint(0, len(other_safe_possibility)-1)
                final_move = other_safe_possibility[direction]
        elif len(other_possibility) > 0:
            if len(other_possibility) == 1:
                final_move = other_possibility[0]
            else:
                direction = random.randint(0, len(other_possibility)-1)
                final_move = other_possibility[direction]
        
        if final_move is None:
            return Move.turn_right(move)
        else:
            return final_move
                      
    def close_to_delivery(self):
        """
        Determines if the train is close to the delivery zone when it is trying to go towards a passenger
        This allows to determine if the train should drop what it already has on the way, done in get_move
        
        IN: None
        OUT: Boolean
        """
        self.positions()

        #distance to delivery position
        distance_to_delivery = self.distance_to_point(self.train_position, self.delivery_zone_pos)
        if distance_to_delivery < 80 and len(self.all_trains[self.nickname]['wagons']) >= 1: #80 is arbitrary, 1 just makes sense in practice
            return True
        return False
    
    def passenger_on_way(self):
        """
        Determine if there is a passenger near the train when he is moving towards the delivery zone
        If so, the train will grab it on the way in get_move
        
        IN: None
        OUT: Boolean
        """

        closest_passenger = self.closest_passenger()
        distance_to_passenger = self.distance_to_point(closest_passenger, self.train_position) 
        radius = 100 #default value just in case
        #adapt depending on number of players
        if len(self.all_trains) == 1 or len(self.all_trains) == 2:
            radius = 100
        if len(self.all_trains) == 3 or len(self.all_trains) == 4:
            radius = 50
        if distance_to_passenger < radius: 
            return True
        return False

    def get_direction(self, next_pos):
        """
        Determines move to choose depending on next coordinate to go onto
        
        IN: tuple of coordinates (int, int)
        OUT: move (eg. Move.UP, ...)
        """
        for move in self.moves:
            pos_of_move = self.new_position(self.train_position, move)
            if pos_of_move == next_pos:
                return Move(move)

    def delivery_donut(self):
        """
        The ULTIMATE strategy :). Blocks other players from delivering passenger by surrounding the delivery zone
        and circling around it.
        
        IN: None
        OUT: Move
        """
        self.positions()

        target_pos = ((self.x_delivery_position - self.cell_size), self.y_delivery_position)

        #guide train to delivery zone
        move = Move(self.other_move(target_pos)) 

        #variable to enable/disable the circling around the delivery zone
        launch_circling = False 
        delivery_spots = self.zone_around_delivery()

        #checks if train position is on circling path 
        if tuple(self.train_position) in delivery_spots:
            launch_circling = True
        
        #the target is just below the top left corner, we need to move up to start
        if target_pos == tuple(self.train_position): 
            return Move.UP
        
        #this contains all the conditions to force the train to go around the delivery zone
        if launch_circling:
            #the conditions are here to turn at the right moment.
            if self.y_train_position == (self.y_delivery_position - self.cell_size):
                move = Move.RIGHT
                if self.x_train_position == (self.delivery_zone["width"] + self.x_delivery_position):
                    move = Move.DOWN
            
            if self.y_train_position == (self.y_delivery_position + self.delivery_zone["height"]):
                move = Move.LEFT
                if self.x_train_position == self.x_delivery_position:
                    move = Move.UP
            
            if self.x_train_position == (self.x_delivery_position + self.delivery_zone['width']):
                move = Move.DOWN
                if self.y_train_position == (self.y_delivery_position + self.delivery_zone['height']):
                    move = Move.LEFT
            
            if self.x_train_position == self.y_delivery_position:
                move = Move.UP
                if self.y_train_position == (self.y_delivery_position - self.cell_size):
                    move = Move.RIGHT

        return move

    def get_move(self):
        """
        Determines which coordinates to go to and how to move accordingly.
        Contains the decision making : grabbing passengers, delivering them, or activating the ultimate strategy
        
        IN: None
        OUT: Move(eg. Move.UP,...)
        """
        self.positions()

        #determine current opponent maximum score for the ultimate strategy 
        max_score = 0
        if self.best_scores:
            for train in self.all_trains:
                if train in self.best_scores:
                    if train == self.nickname:
                        continue
                    if self.best_scores[train] > max_score:
                        max_score = self.best_scores[train]
        delivery_pos_on_edge = False

        #disable ultimate strategy if the delivery zone is on the edge
        if (self.x_delivery_position == 0) or (self.y_delivery_position == 0) \
        or (self.x_delivery_position == self.game_width) or (self.y_delivery_position == self.game_height):
            delivery_pos_on_edge = True

        DELIVER = 0
        if len(self.all_trains[self.nickname]['wagons']) > 0:
            DELIVER = 1

        #disable delivery if the ultimate strategy is activated
        if self.best_scores and self.nickname in self.best_scores:
            if (self.best_scores[self.nickname]> (max_score + 9)) and  (len(self.all_trains[self.nickname]['wagons']) < self.delivery_zone_perimeter) and not delivery_pos_on_edge :
                DELIVER = 0
        
        if DELIVER == 0:
            close_to_delivery = False
            #condition to dodge this part if at the start of the game (otherwise errors pop up)
            if not self.best_scores:
                close_to_delivery = self.close_to_delivery()

            #go to the delivery zone if close enough to it
            if close_to_delivery:
                goal = self.closest_delivery_zone_point()
                path = self.path_to_point(goal)
            else:
                goal = self.closest_passenger()
                path = self.path_to_point(goal) #deliver passengers
        
        else:
            if len(self.all_trains[self.nickname]['wagons']) > 4:
                goal = self.closest_delivery_zone_point()
                path = self.path_to_point(goal) #goes back if too long
            passenger_on_way = self.passenger_on_way()
            #takes the passengers that are close to the path
            if passenger_on_way:
                goal = self.closest_passenger()
                path = self.path_to_point(goal)
            else:
                goal = self.closest_delivery_zone_point()
                path = self.path_to_point(goal)

        #activating the strategy if we are alone or with 2 players only
        if self.best_scores and (self.nickname in self.best_scores) \
        and not delivery_pos_on_edge and len(self.all_trains)!=4 and len(self.all_trains)!= 3:
            #activate with a lead of 10 points minimum
            if self.best_scores[self.nickname] > (max_score + 9):
                if len(self.all_trains[self.nickname]['wagons']) == (self.delivery_zone_perimeter - 1) and not self.ultimate_strategy:
                    self.network.send_drop_wagon_request()#drops a wagon to get the exact wagons compared to the perimeter
                if len(self.all_trains[self.nickname]['wagons']) == (self.delivery_zone_perimeter - 2):#(-2) because head is considered (ensure one cell margin to avoid death)
                    move = self.delivery_donut()   #circle delivery zone if the amount of wagons is perfect
                    return move
                else:
                    pass
            self.ultimate_strategy = True #ensure strategy continues even if some of the lead is lost.

        #ensure we are never too long
        if len(self.all_trains[self.nickname]['wagons']) >= 6 and not self.ultimate_strategy:
            goal = self.closest_delivery_zone_point()
            path = self.path_to_point(goal)
        if path:
            move = self.get_direction(path)
        else:
            move = self.other_move(goal)


        """        if self.best_scores:
            if self.all_trains[self.nickname]["score"] == 0:
                max_actual_score = 0
                #find the max current score of any train.
                for train in self.all_trains:
                    if train == self.nickname:
                        continue
                    if self.all_trains[train]["score"]:
                        if self.all_trains[train]["score"] > max_actual_score:
                            target_score = self.all_trains[train]["score"]
                            target_train = train
                #if self.all_trains[train]["score"]:
                #    #target train with high score if our train just died and score difference with opponent is high
                #    if target_score > 1 and not self.ultimate_strategy:
                #        move = self.path_to_point(self.all_trains[target_train]["position"]) """
                        
        if self.ultimate_strategy:
            if self.best_scores[self.nickname]>max_score+2:#continues the strategy even if some of the lead is lost, up to +2
                if len(self.all_trains[self.nickname]['wagons']) == (self.delivery_zone_perimeter - 1):
                    self.network.send_drop_wagon_request()
                if len(self.all_trains[self.nickname]['wagons']) == (self.delivery_zone_perimeter - 2):
                    move = self.delivery_donut() #activates the strategy
            else:
                self.ultimate_strategy = False #go back to normal mode if lead is lost
      
        print(self.closest_delivery_zone_point(), self.delivery_zone_pos)
        return Move(move)


        

