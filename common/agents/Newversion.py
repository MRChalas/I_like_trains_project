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

    def closest_delivery_zone_point(self):
        """
        Determines closest point within delivery zone train can go to
        
        IN:
        OUT:
        """
        closest_delivery_point = (0,0)
        min_distance = float('inf')
        delivery_zone = self.delivery_zone()
        for point in delivery_zone:
            distance = self.distance_to_point(self.train_position,point)
            if distance < min_distance:
                min_distance = distance
                closest_delivery_point = point

        return closest_delivery_point
     
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
                moves = [Move.LEFT.value, Move.DOWN.value, Move.UP.value,  Move.RIGHT.value]
                for move in moves:
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
        delivery_points=[]
        #this function converts the given data to all positions contained in the delivery zone

        for i in range(self.delivery_zone['height']//self.cell_size):
            for j in range(self.delivery_zone['width']//self.cell_size):

                x_position= self.x_delivery_position+i*self.cell_size
                y_position = self.y_delivery_position+j*self.cell_size

                delivery_points.append((x_position, y_position))

        return delivery_points

    def zone_around_delivery(self):
        delivery_zone_list=[]
        # this function is useful for the "ultimate strategy". It finds the positions of all spots/cells around the delivery zone
        #the corners are taken care of in the first for loop

        for i in range(-1,int(self.delivery_zone['width']/(self.cell_size))+1):
                x1_position= self.x_delivery_position+i*self.cell_size
                y1_position = self.y_delivery_position-self.cell_size

                x2_position=self.x_delivery_position+i*self.cell_size
                y2_position=self.y_delivery_position+self.delivery_zone['height']+self.cell_size
                pos1=(x1_position,y1_position)
                pos2=(x2_position,y2_position)
                delivery_zone_list.append(pos1)
                delivery_zone_list.append(pos2)

        for j in range(0,int(self.delivery_zone['height']/(self.cell_size))):
                x1_position= self.x_delivery_position-self.cell_size
                y1_position = self.y_delivery_position+j*self.cell_size

                x2_position=self.x_delivery_position+self.delivery_zone['width']
                y2_position=self.y_delivery_position+j*self.cell_size
                pos1=(x1_position,y1_position)
                pos2=(x2_position,y2_position)
                delivery_zone_list.append(pos1)
                delivery_zone_list.append(pos2)

        return delivery_zone_list

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
            # chooses node with lowest cost
            points_to_evaluate.sort(key=lambda node: node.total_cost)
            current_point = points_to_evaluate.pop(0)
            #current_point = min(points_to_evaluate)##############

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
    
        return None #No path available

    def other_move(self, point: tuple):
        """
        Determines direction to take to get to closest passenger

        IN: coordinates of the point the train is trying to reach (int, int)
        OUT: best move the train can take (eg: Move.UP, Move.LEFT, ...)
        """

        self.positions()

        #reset movement variables
        moves = [Move.LEFT.value, Move.DOWN.value, Move.UP.value,  Move.RIGHT.value]
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
            new_pos = self.new_position(self.train_position, move, 1) 
            distance = self.distance_to_point(new_pos , point)

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
        
        IN: None
        OUT: Boolean
        """
        self.positions()

        #distance to delivery position
        distance_to_delivery = self.distance_to_point(self.train_position, self.delivery_zone_pos)
        if distance_to_delivery < 80 and len(self.all_trains[self.nickname]['wagons'])>=1: #80 is arbitrary, 1 just makes sense in practice
            return True
        return False
    
    def passenger_on_way(self):
        """
        Determine if there is a passenger near the train when he is moving towards the delivery zone
        
        IN: None
        OUT: Boolean
        """

        closest_passenger = self.closest_passenger()
        distance_to_passenger = abs(closest_passenger[0] - self.x_train_position) + abs(closest_passenger[1] - self.y_train_position)
        radius=100#default value just in case
        if len(self.all_trains)==1 or len(self.all_trains)==2:
            radius=100
        if len(self.all_trains)==3 or len(self.all_trains)==4:
            radius=50
        if distance_to_passenger < radius: 
            return True
        return False

    def get_direction(self, path):
        moves = [Move.LEFT.value, Move.DOWN.value, Move.UP.value,  Move.RIGHT.value]
        for move in moves:
            pos_of_move = self.new_position(self.train_position, move, 1)
            if pos_of_move == path:
                return Move(move)

    def delivery_donut(self):
        """
        The ULTIMATE strategy :). Blocks other players from delivering passenger by surrounding the delivery zone
        
        IN: None
        OUT: Move
        """
        self.positions()

        target_pos = (self.x_delivery_position-self.cell_size, self.y_delivery_position)
        move = Move(self.other_move(target_pos))
        launch_circling = False
        delivery_spots = self.zone_around_delivery()

        if tuple(self.train_position) in delivery_spots:
            launch_circling = True
        
        if target_pos == tuple(self.train_position):
            return Move.UP
        
        if launch_circling:
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
        Determines which coordinates to go to and how to move accordingly
        
        IN: None
        OUT: Move
        """
        self.positions()

        #determine current maximum score
        max_score = 0
        if self.best_scores:
            for train in self.all_trains:
                if train in self.best_scores:
                    if train == self.nickname:
                        continue
                    if self.best_scores[train] > max_score:
                        max_score = self.best_scores[train]
        delivery_pos_on_edge = False
        if (self.x_delivery_position == 0) or (self.y_delivery_position == 0) \
        or (self.x_delivery_position == self.game_width) or (self.y_delivery_position == self.game_height):
            delivery_pos_on_edge = True

        DELIVER = 0
        if len(self.all_trains[self.nickname]['wagons']) > 0:
            DELIVER = 1

        if self.best_scores and self.nickname in self.best_scores:
            if (self.best_scores[self.nickname]> (max_score + 10)) and  (len(self.all_trains[self.nickname]['wagons']) < self.delivery_zone_perimeter) and not delivery_pos_on_edge :
                DELIVER=0
        
        if DELIVER == 0:
            close_to_delivery = False
            if not self.best_scores:
                close_to_delivery = self.close_to_delivery()

            if close_to_delivery:
                goal = self.delivery_zone_pos
                path = self.path_to_point(goal)
            else:
                goal = self.closest_passenger()
                path = self.path_to_point(goal)
        
        else:
            if len(self.all_trains[self.nickname]['wagons']) > 4:
                goal = self.delivery_zone_pos
                path = self.path_to_point(goal)
            passenger_on_way = self.passenger_on_way()
            if passenger_on_way:
                goal = self.closest_passenger()
                path = self.path_to_point(goal)
            else:
                goal = self.delivery_zone_pos
                path = self.path_to_point(goal)

        
        if self.best_scores and (self.nickname in self.best_scores) \
        and not delivery_pos_on_edge and len(self.all_trains)!=4 and len(self.all_trains)!=3:
            if self.best_scores[self.nickname] > (max_score + 9):
                if len(self.all_trains[self.nickname]['wagons']) == (self.delivery_zone_perimeter - 1) and not self.ultimate_strategy:
                    self.network.send_drop_wagon_request()
                if len(self.all_trains[self.nickname]['wagons']) == (self.delivery_zone_perimeter - 2):
                    move = self.delivery_donut()
                    return move
                else:
                    pass
            self.ultimate_strategy=True

        """
        if ultimate_strat:
            if self.best_scores[self.nickname]> (max_score + 2):
                if len(self.all_trains[self.nickname]['wagons']) == (self.delivery_zone_perimeter - 1):
                        self.network.send_drop_wagon_request()
                if len(self.all_trains[self.nickname]['wagons']) == (self.delivery_zone_perimeter - 2):
                    move = self.delivery_donut() 
                    return move 
            else:
                ultimate_strat = False
    """
        if len(self.all_trains[self.nickname]['wagons'])>=6 and not self.ultimate_strategy:
            goal = self.delivery_zone_pos
            path = self.path_to_point(goal)
        if path:
            move = self.get_direction(path)
        else:
            move = self.other_move(goal)


        if self.best_scores:
            if self.all_trains[self.nickname]["score"]==0:
                max_actual_score=0
                for train in self.all_trains:
                    if self.all_trains[train]["score"]:
                        if self.all_trains[train]["score"]>max_actual_score:
                            target_score=self.all_trains[train]["score"]
                            target_train=train
                if self.all_trains[train]["score"]:
                    if target_score>30:
                        move=self.path_to_point(self.all_trains[target_train]["position"]) #targets the train with a high score if 
                    # our train just died and the score is high. Does not activate if the ultimate strategy is on
        if self.ultimate_strategy:
            if self.best_scores[self.nickname]>max_score+2:
                if len(self.all_trains[self.nickname]['wagons'])==self.delivery_zone_perimeter-1:
                        self.network.send_drop_wagon_request()
                if len(self.all_trains[self.nickname]['wagons'])==self.delivery_zone_perimeter-2:
                    move=self.delivery_donut()  
            else:
                self.ultimate_strategy=False
      
          
        
        return Move(move)


        

