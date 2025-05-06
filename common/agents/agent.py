import random
from common.base_agent import BaseAgent
from common.move import Move

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

######################### meurt dans le coin ce qui pose probleme
# popo...  H            # Resolution : si au bord + positions derriere bloquees, capter si c un coin et si oui blocker le mvmt vers le haut(ou autre)
#sopo                   #
#                       #
#                       #
#                       #
#########################                       

#INFO:
# Nouvelle version qui marche mieux parce qu'elle évite les autres trains mais je pense qu'elle sera moins efficace que l'autre une fois que l'autre evitera les trains
#En revanche le code de mise en place est plus simple

#GESTION DES MURS:
#La liste avec les positions ne contient pas les positions des murs donc, par defaut, le train les evitera



class Agent(BaseAgent):

    def positions(self):
        """
        Cordinates which are reused several times throughout the movement choice
        """

        #train coordinates
        self.x_train_position = self.all_trains[self.nickname]["position"][0]
        self.y_train_position = self.all_trains[self.nickname]["position"][1]
        
        #latest train movement
        self.move_vector = self.all_trains[self.nickname]["direction"]
        self.previous_move = Move(tuple(self.move_vector))

        #delivery zone coordinates
        self.x_delivery_position = self.delivery_zone['position'][0]
        self.y_delivery_position = self.delivery_zone['position'][1]
    
    def distance_to_point(self, train_x: int, train_y: int, point_x: int, point_y: int):
        """
        Calculates shortest distance between the train and a given point

        IN: train coordinates (x,y) and point coordinates (x,y)
        OUT: shortest distance (tuple of int)
        """

        return abs(train_x - point_x) + abs(train_y - point_y)
    
    def new_position(self, move, num_of_moves):
        new_x = self.x_train_position + (move[0] * self.cell_size)*num_of_moves
        new_y = self.y_train_position + (move[1] * self.cell_size)*num_of_moves

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
    
    def check_if_corner(self, moves):

        self.positions()
        self.available_grid_coordinates()

        return moves 

    
    def path_to_point(self, point: tuple):
        """
        Determines direction to take to get to closest passenger

        IN: coordinates of the point the train is trying to reach (int, int)
        OUT: best move the train can take (eg: Move.UP, Move.LEFT, ...)
        """

        self.positions()

        #other = 0

        #reset possible moves train can choose from
        moves = [Move.LEFT.value, Move.DOWN.value, Move.UP.value,  Move.RIGHT.value]
        other_possibility = []
        #remove move opposite to the previous one
        opposite_m = tuple(-i for i in self.move_vector)
        moves.remove(opposite_m)
        shortest_distance = float('inf')
        best_move = None

        moves = self.check_if_corner(moves)

        for move in moves:
            #calculate distance between possible new position and point train is trying to reach
            new_pos = self.new_position(move, 1) 
            new_x = new_pos[0]
            new_y = new_pos[1]
            distance = self.distance_to_point(new_x, new_y, point[0], point[1])

            #determine available coordinates
            available_positions = self.available_grid_coordinates()

            #check if wanted move does not move onto unavailable position
            if tuple(new_pos) in available_positions:
                possible_move = move
                #check if move brings closer to the wanted point than previous move
                if distance < shortest_distance:
                    shortest_distance = distance
                    best_move = move 
                if distance == shortest_distance:
                    other_possibility.append(move)
        other = random.randint(0,len(other_possibility)-1)
        other_possibility = other_possibility[other]

                    #print(other)
                    #if other == 0:
                    #    third_possibility = move
                    #    other =1
                    #    print(other)
        #precaution to avoid running head first into trains
        if best_move is not None:
            
            safety_check_pos = self.new_position(best_move, 2)
            print("SAFETY", safety_check_pos)
            for train in self.all_trains:
                print("TRAIN_POS", tuple(self.all_trains[train]["position"]))
                if safety_check_pos in tuple(self.all_trains[train]["position"]):
                    print("SAAAAAAFE")
                    return other_possibility
        else:
            safety_check_pos = self.new_position(other_possibility, 2)
            print("SAFETY_OTHER", safety_check_pos)
            for train in self.all_trains:
                print("TRAIN_POS", tuple(self.all_trains[train]["position"]))
                if safety_check_pos in tuple(self.all_trains[train]["position"]):
                    print("SAAAAAAFE")
                    return other_possibility
        
        #determine distance if turning around
        if point == self.delivery_zone['position']:
            turn_x = self.x_train_position + opposite_m[0] * self.cell_size
            turn_y = self.y_train_position + opposite_m[1] * self.cell_size
            turn_around = self.distance_to_point(turn_x, turn_y, point[0], point[1])
            #check if turning around would be the best choice
            if distance > turn_around:
                return other_possibility
            
            
        return best_move if best_move is not None else possible_move
        
    def on_the_way(self):

        closest_passenger = self.closest_passenger()
        distance_to_passenger = abs(closest_passenger[0] - self.x_train_position) + abs(closest_passenger[1] - self.y_train_position)
        if distance_to_passenger < 120:#120 is purely arbitrary, to test and determine which is best (from what I've seen the range of the value should be 50-150)
            return 1
        return 0


    def close_to_delivery(self):
        train_pos = self.all_trains[self.nickname]["position"]
        delivery_pos = self.delivery_zone['position']
        """ after many different tests, I realized you could gain time by dropping some passengers off if very close
        to the delivery zone on the way. This function takes care of those special cases, making some gains in efficiency :-)"""
        distance_to_delivery = self.distance_to_point(train_pos[0], train_pos[1], delivery_pos[0], delivery_pos[1])
        #closest_passenger = self.closest_passenger()
        #distance_to_passenger = self.distance_to_point(train_pos[0], train_pos[1], closest_passenger[0], closest_passenger[1])
        if distance_to_delivery < 90 and len(self.all_trains[self.nickname]['wagons'])>=2: #80 is arbitrary, 2 just makes sense in practice
            return 1
        #elif distance_to_delivery > 2*distance_to_passenger:
        #    return 1
        return 0
      
    def get_move(self):
        
        
        DELIVER = 0
        delivery_zone_pos = self.delivery_zone['position']

        if len(self.all_trains[self.nickname]['wagons'])>=1:
            DELIVER = 1

        if DELIVER == 0:
            close_to_delivery = self.close_to_delivery()
            if close_to_delivery == 1:
                move = self.path_to_point(delivery_zone_pos)
            else:
                passenger_pos = self.closest_passenger()
                move = self.path_to_point(passenger_pos)
#
        else:
            passenger_on_the_way = self.on_the_way()
            if passenger_on_the_way == 1:
                passenger_pos = self.closest_passenger()
                move = self.path_to_point(passenger_pos)
            else:
                move = self.path_to_point(delivery_zone_pos)
            
        return Move(move)
    #

#            {
#                "nickname": "Luky Luke",
#                "agent_file_name": "agentM_0.py"
#            },
#            {
#                "nickname": "Billy the kid",
#                "agent_file_name": "agentA_0.py"
#            },
#            {
#                "nickname": "Buffalo Bill",
#                "agent_file_name": "agent.py"

    
    
