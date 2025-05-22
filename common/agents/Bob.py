import random
from common.base_agent import BaseAgent
from common.move import Move

# Coded with love by Marylou and Alexan <3
# 127.0.0.1
# 128.179.154.221
# Student scipers, will be automatically used to evaluate your code
SCIPERS = ["390899", "398584"]

class Agent(BaseAgent):
    def get_move(self):
        """
        Called regularly called to get the next move for your train. Implement
        an algorithm to control your train here. You will be handing in this file.

        For now, the code simply picks a random direction between UP, DOWN, LEFT, RIGHT

        This method must return one of moves.MOVE
        """

        moves = [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]
        return random.choice(moves)
#class Agent(BaseAgent):
#
#    def positions(self):
#        """
#        Cordinates which are reused several times throughout the movement choice
#        """
#        #train coordinates
#        self.train_position = self.all_trains[self.nickname]["position"]
#        self.x_train_position = self.all_trains[self.nickname]["position"][0]
#        self.y_train_position = self.all_trains[self.nickname]["position"][1]
#        
#        #previous train movement
#        self.move_vector = self.all_trains[self.nickname]["direction"]
#        self.previous_move = Move(tuple(self.move_vector))
#
#        #delivery zone coordinates
#        self.x_delivery_position = self.delivery_zone['position'][0]
#        self.y_delivery_position = self.delivery_zone['position'][1]
#    
#    def distance_to_point(self, current_x: int, current_y: int, point_x: int, point_y: int):
#        """
#        Calculates shortest distance between the train and a given point
#
#        IN: train coordinates (x,y) and point coordinates (x,y)
#        OUT: shortest distance (tuple of int)
#        """
#
#        return abs(current_x - point_x) + abs(current_y - point_y)
#    
#    def new_position(self, position:tuple, move: tuple, num_of_moves: int):
#        """
#        Determines new train position after n moves
#        
#        IN: tuple corresponding to move, number of times train wants to move
#        OUT: new position coordinates
#        """
#        new_x = position[0] + (move[0] * self.cell_size) * num_of_moves
#        new_y = position[1] + (move[1] * self.cell_size) * num_of_moves
#
#        return (new_x, new_y)
#    
#    def available_grid_coordinates(self):
#        """
#        Determines all grid coordinates which have no obstacle
#
#        IN: None
#        OUT: available coordinates' grid (list of tuples)
#        """
#
#        #reset grid
#        grid_coordinates = []
#
#        #fill in grid coordinates depending on game parameters
#        for x in range(0, self.game_width, self.cell_size):
#            for y in range(0, self.game_height, self.cell_size):
#                grid_coordinates.append((x,y))
#        
#        #remove train positions from available coordinates
#        for train in self.all_trains:
#            train_pos = tuple(self.all_trains[train]["position"])
#            #avoid errors in case of duplicate removal of positions
#            if train_pos in grid_coordinates: 
#                grid_coordinates.remove(train_pos)
#
#            #remove wagon positions from available coordinates
#            for wagon_pos in self.all_trains[train]["wagons"]: 
#                #avoid errors in case of duplicate removal of positions
#                if tuple(wagon_pos) in grid_coordinates:
#                    grid_coordinates.remove(tuple(wagon_pos))
#        
#        return grid_coordinates
#    
#    def around_head(self):
#        """
#        Determines coordinates which could possibly be filled by train heads after next move
#       
#        IN: None
#        OUT: list of tuples containing coordinates
#        """
#
#        # Reset head positions
#        head_positions=[]
#
#
#        for train in self.all_trains:
#            #avoid making perimeter around own head unavailable
#            if train == self.nickname:
#               continue
#
#            else:
#                head_position = tuple(self.all_trains[train]["position"])
#                #avoids duplicates
#                if head_position not in head_positions:
#                    head_positions.append(head_position)
#                moves = [Move.LEFT.value, Move.DOWN.value, Move.UP.value,  Move.RIGHT.value]
#                for move in moves:
#                   precaution_position=self.new_position(head_position, move, 1)
#                   #avoids duplicates
#                   if precaution_position not in head_positions:
#                        head_positions.append(precaution_position)
#        return head_positions
#         
#    def closest_passenger(self):
#        """
#        Determines distance to closest passenger
#
#        IN: None
#        OUT: coordinates of closest passenger (int)
#        """
#
#        self.positions()
#
#        #reset passenger positions
#        passenger_positions = []
#
#        #create list with current available passengers
#        for i in range(len(self.passengers)):
#            passenger_positions.append(self.passengers[i]['position'])
#        closest_distance = float('inf')
#
#        for pos in passenger_positions:
#            distance = self.distance_to_point(self.x_train_position, self.y_train_position, pos[0], pos[1])
#            #update closest passenger coordinates if distance is smaller than the on of the previous closest passenger
#            if distance < closest_distance:
#                closest_distance = distance
#                closest_passenger = pos
#
#        return closest_passenger
#    
#    def delivery_zone_spots(self):
#        delivery_zone_list=[]
#        #this function converts the given data to all positions contained in the delivery zone
#
#        for i in range(0,int(self.delivery_zone['height']/(self.cell_size))):
#            for j in range(0,int(self.delivery_zone['width']/(self.cell_size))):
#
#                x_position= self.x_delivery_position+i*self.cell_size
#                y_position = self.y_delivery_position+j*self.cell_size
#
#                pos1=(x_position,y_position)
#                delivery_zone_list.append(pos1)
#
#        return delivery_zone_list
#
#    def closest_delivery_zone_point(self):
#        """
#        Determines closest point within delivery zone train can go to
#        
#        IN:
#        OUT:
#        """
#        closest_point=(0,0)
#        min_distance=10000
#        all_possible_points=self.delivery_zone_spots()
#        actual_x=self.all_trains[self.nickname]["position"][0]
#        actual_y=self.all_trains[self.nickname]["position"][1]
#        for point in all_possible_points:
#            point=list(point)
#            point_x=point[0]
#            point_y=point[1]
#            distance=self.distance_to_point(actual_x,actual_y,point_x,point_y)
#            if distance<min_distance:
#                min_distance=distance
#                closest_point=tuple(point)
#        return closest_point
#
#    def path_to_point(self, point: tuple):
#        """
#        Determines direction to take to get to closest passenger
#
#        IN: coordinates of the point the train is trying to reach (int, int)
#        OUT: best move the train can take (eg: Move.UP, Move.LEFT, ...)
#        """
#
#        self.positions()
#
#        #reset movement variables
#        moves = [Move.LEFT.value, Move.DOWN.value, Move.UP.value,  Move.RIGHT.value]
#        shortest_distance = float('inf')
#        best_move = None
#        best_safe_move = None
#        possible_moves = []
#        possible_safe_moves = []
#        other_possibility = []
#        other_safe_possibility = []
#
#        #remove move opposite to the previous one
#        opposite_m = tuple(-i for i in self.move_vector)
#        moves.remove(opposite_m)
#
#        for move in moves:
#            #calculate distance between possible new position and point train is trying to reach
#            new_pos = self.new_position(self.train_position, move, 1) 
#            new_x = new_pos[0]
#            new_y = new_pos[1]
#            distance = self.distance_to_point(new_x, new_y, point[0], point[1])
#
#            #determine available coordinates
#            available_positions = self.available_grid_coordinates()
#            head_positions = self.around_head()
#
#            #check if wanted move does not move onto unavailable position
#            if tuple(new_pos) in available_positions:
#                    #differentiates possible positions form safe positions
#                    possible_moves.append(move)
#                    if tuple(new_pos) not in head_positions:
#                        possible_safe_moves.append(move)
#                    #check if move brings closer to the wanted point than previous move
#                    if distance < shortest_distance:
#                        shortest_distance = distance
#                        best_move = move 
#                        if tuple(new_pos) not in head_positions:
#                            best_safe_move = move
#                    if distance == shortest_distance:
#                        other_possibility.append(move)
#                        if tuple(new_pos) not in head_positions:
#                            other_safe_possibility.append(move)
#        
#        #determine distance if turning around
#        if point == self.delivery_zone['position']:
#            turn_x = self.x_train_position + opposite_m[0] * self.cell_size
#            turn_y = self.y_train_position + opposite_m[1] * self.cell_size
#            turn_around = self.distance_to_point(turn_x, turn_y, point[0], point[1])
#
#            #check if turning around would be the best choice
#            if distance > turn_around:
#                if len(other_safe_possibility) > 0:
#                    if len(other_safe_possibility) == 1:
#                        best_safe_move = other_safe_possibility[0]
#                    else:
#                        direction = random.randint(0, len(other_safe_possibility)-1)
#                        best_safe_move = other_safe_possibility[direction]
#                elif len(other_possibility) > 0:
#                    if len(other_possibility) == 1:
#                        best_move = other_possibility[0]
#                    else:
#                        direction = random.randint(0, len(other_possibility)-1)
#                        best_move = other_possibility[direction]
#        
#        if best_move == best_safe_move:
#            final_move = best_move
#        elif best_safe_move is not None:
#            final_move = best_safe_move 
#        elif len(other_safe_possibility) > 0:
#            if len(other_safe_possibility) == 1:
#                final_move = other_safe_possibility[0]
#            else:
#                direction = random.randint(0, len(other_safe_possibility)-1)
#                final_move = other_safe_possibility[direction]
#        elif len(other_possibility) > 0:
#            if len(other_possibility) == 1:
#                final_move = other_possibility[0]
#            else:
#                direction = random.randint(0, len(other_possibility)-1)
#                final_move = other_possibility[direction]
#        
#        if final_move is None:
#            return Move.turn_right(move)
#        else:
#            return final_move
#        
#    def on_the_way(self):
#        """
#        Determine if there is a passenger near the train when he is moving towards the delivery zone
#        
#        IN: None
#        OUT: Boolean
#        """
#
#        closest_passenger = self.closest_passenger()
#        distance_to_passenger = abs(closest_passenger[0] - self.x_train_position) + abs(closest_passenger[1] - self.y_train_position)
#        radius=100#default value just in case
#        if len(self.all_trains)==1 or len(self.all_trains)==2:
#            radius=120
#        if len(self.all_trains)==3 or len(self.all_trains)==4:
#            radius=50
#        if distance_to_passenger < radius: 
#            return True
#        return False
#
#    def close_to_delivery(self):
#        """
#        Determines if the train is close to the delivery zone when it is trying to go towards a passenger
#        
#        IN: None
#        OUT: Boolean
#        """
#
#        train_pos = self.all_trains[self.nickname]["position"]
#
#        #distance to delivery position
#        delivery_pos = self.delivery_zone['position']
#        distance_to_delivery = self.distance_to_point(train_pos[0], train_pos[1], delivery_pos[0], delivery_pos[1])
#        if distance_to_delivery < 80 and len(self.all_trains[self.nickname]['wagons'])>=2: #80 is arbitrary, 2 just makes sense in practice
#            return True
#        return False
#      
#    def around_delivery_zone_spots(self):
#        delivery_zone_list=[]
#        # this function is useful for the "ultimate strategy". It finds the positions of all spots/cells around the delivery zone
#        #the corners are taken care of in the first for loop
#
#        for i in range(-1,int(self.delivery_zone['width']/(self.cell_size))+1):
#                x1_position= self.x_delivery_position+i*self.cell_size
#                y1_position = self.y_delivery_position-self.cell_size
#
#                x2_position=self.x_delivery_position+i*self.cell_size
#                y2_position=self.y_delivery_position+self.delivery_zone['height']+self.cell_size
#                pos1=(x1_position,y1_position)
#                pos2=(x2_position,y2_position)
#                delivery_zone_list.append(pos1)
#                delivery_zone_list.append(pos2)
#
#        for j in range(0,int(self.delivery_zone['height']/(self.cell_size))):
#                x1_position= self.x_delivery_position-self.cell_size
#                y1_position = self.y_delivery_position+j*self.cell_size
#
#                x2_position=self.x_delivery_position+self.delivery_zone['width']
#                y2_position=self.y_delivery_position+j*self.cell_size
#                pos1=(x1_position,y1_position)
#                pos2=(x2_position,y2_position)
#                delivery_zone_list.append(pos1)
#                delivery_zone_list.append(pos2)
#
#        # ci-dessous : les coins
#
#
#        return delivery_zone_list
#
#    def delivery_donut(self):
#        """
#        This is the function for the ULTIMATE strategy. It is responsible for guiding the train to the delivery
#        zone when the strategy is activated, and then to make the train infinitely around the delivery zone. It is a 
#        bit of hardcode as we needed to check that the train was still around the delivery zone. 
#        """
#        delivery_zone_pos = self.delivery_zone['position']
#        target_position=(delivery_zone_pos[0]-self.cell_size,delivery_zone_pos[1])
#        move = self.path_to_point(target_position)
#        launch_circling=False
#        near_delivery_zone_positions=self.around_delivery_zone_spots()
#
#        if tuple(self.all_trains[self.nickname]["position"]) in near_delivery_zone_positions:
#            launch_circling=True
#
#        if target_position==tuple(self.all_trains[self.nickname]["position"]):
#            move=(0,-1)
#            return move
#        
#        if launch_circling:#circling around the delivery zone, and turning when necessary with conditions
#            if self.all_trains[self.nickname]["position"][1]==self.y_delivery_position-self.cell_size:
#                move=(1,0)
#                if self.all_trains[self.nickname]["position"][0]==self.delivery_zone['width']+self.x_delivery_position:
#                    move=(0,1)
#
#            if self.all_trains[self.nickname]["position"][1]==self.y_delivery_position+self.delivery_zone['height']:
#                move=(-1,0)
#                if self.all_trains[self.nickname]["position"][0]==self.x_delivery_position:
#                    move=(0,-1)
#
#            if self.all_trains[self.nickname]["position"][0]==self.x_delivery_position+self.delivery_zone['width']:
#                move=(0,1)
#                if self.all_trains[self.nickname]["position"][1]==self.y_delivery_position+self.delivery_zone['height']:
#                    move=(-1,0)
#
#            if self.all_trains[self.nickname]["position"][0]==self.x_delivery_position:
#                move=(0,-1)
#                if self.all_trains[self.nickname]["position"][1]==self.y_delivery_position-self.cell_size:
#                    move=(1,0)
#
#                    
#        return move
#
#    def get_move(self):
#        """
#        Determines which coordinates to go to and how to move accordingly
#        
#        IN: None
#        OUT: Move
#        """
#        #determines the perimeter of the delivery zone for the preparation of the "ultimate strategy"
#
#        """Memo : what is called ultimate strategy are all the methods, code and functions needed to circle 
#        the delivery zone automatically when our agent leads by at least 10 points. This ensures victory as
#        the ennemy cannot reach the delivery zone anymore."""
#        perimeter=(2*self.delivery_zone['width']/self.cell_size  +   2*self.delivery_zone['height']/self.cell_size)+4
#        maxscore=0
#        #the code below finds the maximum score of all players, without considering our own
#        if self.best_scores :
#            for train in self.all_trains:
#                if train in self.best_scores:
#                 if train==self.nickname:
#                    continue
#                 if self.best_scores[train]>maxscore:
#                    maxscore=self.best_scores[train]
#        delivery_position_not_on_edge=True
#        self.positions()
#        if self.x_delivery_position==0 or self.y_delivery_position==0 or self.x_delivery_position==self.game_width or self.y_delivery_position==self.game_height:
#            delivery_position_not_on_edge=False
#
#
#
#        
#        DELIVER = 0
#        delivery_zone_pos =self.delivery_zone['position'] #self.closest_delivery_zone_point() 
#        if len(self.all_trains[self.nickname]['wagons'])>=1:
#            DELIVER = 1
#
#        if self.best_scores and self.nickname in self.best_scores:
#            if self.best_scores[self.nickname]>maxscore+10 and  len(self.all_trains[self.nickname]['wagons'])<perimeter and delivery_position_not_on_edge :
#                DELIVER=0
#                
#        #There is a variable to check that the delivery position is not on the edge, otherwise the strategy fails..
#
#        if DELIVER == 0:
#            close_to_delivery=False
#            if not self.best_scores:
#                close_to_delivery = self.close_to_delivery()
#            
#            if close_to_delivery is True:
#                move = self.path_to_point(delivery_zone_pos)
#            else:
#                passenger_pos = self.closest_passenger()
#                move = self.path_to_point(passenger_pos)
#
#        else:
#            if len(self.all_trains[self.nickname]['wagons'])>=5:
#                move = self.path_to_point(delivery_zone_pos)
#            passenger_on_the_way = self.on_the_way()
#            if passenger_on_the_way is True:
#                passenger_pos = self.closest_passenger()
#                move = self.path_to_point(passenger_pos)
#            else:
#                move = self.path_to_point(delivery_zone_pos)
#
#        ultimate_strategy=False
#        #the code belows enables the "ultimate strategy" when the lead is more than 10 points.
#        #we drop one wagon if possible to reach the perfect score, otherwise we do without it
#        if self.best_scores and self.nickname in self.best_scores and delivery_position_not_on_edge:
#            if self.best_scores[self.nickname]>maxscore+10:
#                ultimate_strategy=True
#                if len(self.all_trains[self.nickname]['wagons'])==perimeter-1:
#                        self.network.send_drop_wagon_request()
#                if len(self.all_trains[self.nickname]['wagons'])==perimeter-2:
#                    move=self.delivery_donut()  
#                else:
#                    pass #because if too long, the ultimate strategy will kill the bot. Better next time!
#        if ultimate_strategy:
#            if self.best_scores[self.nickname]>maxscore+2:
#                if len(self.all_trains[self.nickname]['wagons'])==perimeter-1:
#                        self.network.send_drop_wagon_request()
#                if len(self.all_trains[self.nickname]['wagons'])==perimeter-2:
#                    move=self.delivery_donut()  
#            else:
#                ultimate_strategy=False
#        if len(self.all_trains[self.nickname]['wagons'])>=15:
#                move = self.path_to_point(delivery_zone_pos)
#
#        return Move(move)
#
#    