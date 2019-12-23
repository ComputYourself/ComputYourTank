"""Class defining a bullet, which have :
    - a direction (two float normalized in init)
    - a position (two float)
    - a speed (default 1.0)
    - a damage value (default 1.0)"""

import math

class Bullet: # Définition de notre classe Personne
    """Class defining a bullet, which have :
    - a direction (two float normalized in init)
    - a position (two float)
    - a speed (default 1.0)
    - a damage value (default 1.0)"""


    def __init__(self, destination, position, speed=1.0, dmg=1.0): # Notre méthode constructeur
        self.speed = speed
        direction = (destination[0] - position[0], destination[1] - position[1])
        norm = math.sqrt(direction[0] * direction[0] + direction[1] * direction[1])
        assert (norm == 0), 'Bullet has no direction'
        self.direction_x = direction[0] / norm
        self.direction_y = direction[1] / norm
        self.position_x = position[0]
        self.position_y = position[1]
        self.dmg = dmg


    def step(self):
        """Returns the position of the bullet after a step,
         considering its position, direction and speed"""
        return (self.position_x + self.direction_x, self.position_y + self.direction_y)

    def damage(self):
        """Returns the damage of this bullet"""
        return self.dmg
