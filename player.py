from card import Card
from structure import Structure
from tile import Tile
from util import estimate_roll_probability


class Player:
    def __init__(self, name: str, color: (int, int, int)):
        self.id = name
        self.cards: [Card] = []
        self.points = 0
        self.color = color

        self.resource_connections = { resource: 0 for resource in Tile.Type }
        self.resource_connections_probability = {resource: 0 for resource in Tile.Type}

        self.locations = set()
        self.cities = 0
        self.settlements = 0
        self.roads = []

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
        return self.can_make_structure_of_type(structure.type)

    def can_make_structure_of_type(self, structure_type: Structure.Type):
        """
        Checks if the user has the cards to make a structure.
        :param structure_type: The type of the structure to make.
        :return: True if the user has the cards to make a structure, false otherwise.
        """
        required = structure_type.required_cards()
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

    def made_structure(self, structure_type: Structure.Type, deduct_resources: bool = True, intersection = None, edge = None):
        """
        Removes the cards from a users deck after making a structure and adds the correct points.
        :param structure_type: The structure the user made.
        :param deduct_resources: Whether to deduct the resources to build a structure from a users account.
        :param intersection: The location built on.
        :param edge: The edge built on.
        """
        if deduct_resources:
            for card_type, count in structure_type.required_cards().items():
                for _ in range(count):
                    self.use_card_of_type(card_type)

        if structure_type == Structure.Type.CITY or structure_type == Structure.Type.SETTLEMENT:
            # If a player built a settlement it adds a point.
            # If they built a city, it takes the settlement and adds a point.
            # Either way they get one additional point whenever they build.
            self.add_point()

        # Use probability of getting resource.
        match structure_type:
            case Structure.Type.SETTLEMENT:
                self.settlements += 1
            case Structure.Type.CITY:
                self.settlements -= 1
                self.cities += 1
            case Structure.Type.ROAD:
                self.roads.append(edge)

        if intersection:
            for tile in intersection.adjacent_tiles:
                self.resource_connections[tile.type] += 1
                self.resource_connections_probability[tile.type] += 1 * estimate_roll_probability(tile.roll)

        if edge:
            self.locations.add(edge.start.location)
            self.locations.add(edge.end.location)

    def add_point(self):
        """
        Adds a point to the user.
        """
        self.points += 1