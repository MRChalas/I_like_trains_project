import random
from common.base_agent import BaseAgent
from common.move import Move

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
    
    def closest_delivery_zone_point(self):
        """
        Determines closest point within delivery zone train can go to
        
        IN:
        OUT:
        """

        pass
    
    def path_to_point(self, point: tuple):
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
            new_x = new_pos[0]
            new_y = new_pos[1]
            distance = self.distance_to_point(new_x, new_y, point[0], point[1])

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
            turn_around = self.distance_to_point(turn_x, turn_y, point[0], point[1])

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

    def close_to_delivery(self):
        """
        Determines if the train is close to the delivery zone when it is trying to go towards a passenger
        
        IN: None
        OUT: Boolean
        """

        train_pos = self.all_trains[self.nickname]["position"]

        #distance to delivery position
        delivery_pos = self.delivery_zone['position']
        distance_to_delivery = self.distance_to_point(train_pos[0], train_pos[1], delivery_pos[0], delivery_pos[1])
        if distance_to_delivery < 80 and len(self.all_trains[self.nickname]['wagons'])>=2: #80 is arbitrary, 2 just makes sense in practice
            return True
        return False
      
    def get_move(self):
        """
        Determines which coordinates to go to and how to move accordingly
        
        IN: None
        OUT: Move
        """
        #self.logger.debug(self.all_trains)
        DELIVER = 0
        delivery_zone_pos = self.delivery_zone['position'] #closest_delivery_point(...)

        if len(self.all_trains[self.nickname]['wagons'])>=1:
            DELIVER = 1

        if DELIVER == 0:
            close_to_delivery = self.close_to_delivery()
            if close_to_delivery is True:
                move = self.path_to_point(delivery_zone_pos)
            else:
                passenger_pos = self.closest_passenger()
                move = self.path_to_point(passenger_pos)
#
        else:
            if len(self.all_trains[self.nickname]['wagons'])>=15:
                move = self.path_to_point(delivery_zone_pos)
            passenger_on_the_way = self.on_the_way()
            if passenger_on_the_way is True:
                passenger_pos = self.closest_passenger()
                move = self.path_to_point(passenger_pos)
            else:
                move = self.path_to_point(delivery_zone_pos)
            
        return Move(move)




    
    
