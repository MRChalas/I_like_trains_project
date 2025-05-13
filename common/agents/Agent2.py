import random
import numpy as np
from common.base_agent import BaseAgent
from common.move import Move
import common.agents.global_nav as gnav

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
    
    def gen_obstacle_grid(self):
        cells_horz = self.game_width // self.cell_size
        cells_vert = self.game_height // self.cell_size
        full_grid = np.zeros((cells_vert, cells_horz))

        self.positions()

        FREE = 0
        AVOID = cells_horz*2
        OCCUPIED = cells_horz*cells_vert*10

        #remove train positions from available coordinates
        for train in self.all_trains:
            train_pos = tuple(self.all_trains[train]["position"])
            #avoid errors in case of duplicate removal of positions
            full_grid[train_pos[0] // self.cell_size, train_pos[1] // self.cell_size]=OCCUPIED

            #remove wagon positions from available coordinates
            for wagon_pos in self.all_trains[train]["wagons"]: 
                full_grid[wagon_pos[0] // self.cell_size, wagon_pos[1] // self.cell_size]=OCCUPIED

        for train in self.all_trains:
            #avoid making perimeter around own head unavailable
            if train == self.nickname:
                behind = ((self.train_position[0]//self.cell_size) - self.move_vector[0], (self.train_position[1]// self.cell_size - self.move_vector[1]))
                full_grid[behind[0], behind[1]] = OCCUPIED

            else:
                head_position = tuple(self.all_trains[train]["position"])
                moves = [Move.LEFT.value, Move.DOWN.value, Move.UP.value,  Move.RIGHT.value]
                for move in moves:
                   precaution_position=self.new_position(head_position, move, 1)
                   full_grid[precaution_position[0] // self.cell_size, precaution_position[1] // self.cell_size] = AVOID

        

        return full_grid


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

    def path_to_point(self, point: tuple):
        
        self.positions()

        print("Gen obstacle grid")
        obst_grid = self.gen_obstacle_grid()
        print("Obstacle grid generated")
        dist_mat = gnav.distance_grid(obst_grid, self.x_train_position//self.cell_size, self.y_train_position//self.cell_size, point[0]//self.cell_size, point[1]//self.cell_size)
        print("Distance grid generated")
        path = gnav.path_find(dist_mat, point[0]//self.cell_size, point[1]//self.cell_size, self.x_train_position//self.cell_size, self.y_train_position//self.cell_size, obst_grid)    
        print("Path found")
        #Find first point in path from train position
        for direction in gnav.DIRECTIONS:
            new_x = self.x_train_position//self.cell_size + direction[0]
            new_y = self.y_train_position//self.cell_size + direction[1]

            if 0 <= new_x < obst_grid.shape[1] and 0 <= new_y < obst_grid.shape[0]:
                if path[new_y][new_x] == 1:
                    return direction
        
        #Convert to move
        if direction == Move.UP.value:
            return Move.UP
        elif direction == Move.DOWN.value:
            return Move.DOWN
        elif direction == Move.LEFT.value:
            return Move.LEFT
        elif direction == Move.RIGHT.value:
            return Move.RIGHT


    
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