Alice then initiates a purchase of 3 of the red potions and 1 of the blue potions. To do so she:

starts by calling POST /carts to get a new cart with ID 9001.
then Alice calls POST /carts/9001/items/RED_POTION and passes in a quantity of 3.
she makes another call to POST /carts/9001/items/BLUE_POTION and passes in a quantity of 1.
finally, she calls POST /carts/9001/checkout to finish her checkout. The checkout charges her 205 gold and gives her 3 red potions and 1 blue potion.
Alice drinks her potions and is ready to go off on a new adventure.
