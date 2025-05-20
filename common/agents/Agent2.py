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
    
class Agent(BaseAgent):

    def get_move(self):
        if self.all_trains[self.nickname]["wagons"]:
            if self.all_trains[self.nickname]["position"][0] < self.delivery_zone['position'][0]:
                return Move.RIGHT
            elif self.all_trains[self.nickname]["position"][1] < self.delivery_zone['position'][1]:
                return Move.UP
            elif self.all_trains[self.nickname]["position"][1] > self.delivery_zone['position'][1]:
                return Move.DOWN
            elif self.all_trains[self.nickname]["position"][0] > self.delivery_zone['position'][0]:
                return Move.LEFT

        elif self.all_trains[self.nickname]["position"][0] < self.passengers[0]['position'][0]:
            return Move.RIGHT
        
        elif self.all_trains[self.nickname]["position"][1] < self.passengers[0]['position'][1]:
            return Move.UP
        
        else: 
            moves = [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]
            return random.choice(moves)
        
        
        
