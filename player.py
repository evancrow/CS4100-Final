from uuid import uuid4

from card import Card
from structure import Structure


class Player:
    def __init__(self):
        self.id = uuid4()
        self.cards: [Card] = []
        self.points = 0

    def add_card(self, card: Card):
        """
        Adds a card to the users deck.
        :param card: The card to add.
        """
        self.cards.append(card)

    def use_card_of_type(self, card_type):
        """
        Removes a card from a users deck.
        :param card_type: The card type to use.
        :return: True if the card exists and was removed, false otherwise.
        """
        for card in self.cards:
            if card.type == card_type:
                self.cards.remove(card)
                return True

        return False

    def can_make_structure(self, structure: Structure):
        """
        Checks if the user has the cards to make a structure.
        :param structure: The structure to make.
        :return: True if the user has the cards to make a structure, false otherwise.
        """
        required = structure.type.required_cards()
        card_count = {}

        for card in self.cards:
            if card.type in required:
                if card.type in card_count:
                    card_count[card.type] += 1
                else:
                    card_count[card.type] = 1

        for resource_type, count in required.items():
            if resource_type not in card_count or card_count[resource_type] < count:
                return False
                
        return True

    def made_structure(self, structure_type: Structure.Type):
        """
        Removes the cards from a users deck after making a structure and adds the correct points.
        :param structure_type: The structure the suer made.
        """
        for card_type, count in structure_type.required_cards().items():
            for _ in range(count):
                self.use_card_of_type(card_type)

        if structure_type == Structure.Type.CITY or Structure.Type.SETTLEMENT:
            # If a player built a settlement it adds a point.
            # If they built a city, it takes the settlement and adds a point.
            # Either way they get one additional point whenever they build.
            self.add_point()

    def add_point(self):
        """
        Adds a point to the user.
        """
        self.points += 1