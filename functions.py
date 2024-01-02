import random
# Function called when the "dice" command is issued
def roll_dice():
    sides = 6
    return random.randint(1, sides)
