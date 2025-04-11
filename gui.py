from time import sleep

import pygame
import sys
import math
from enum import Enum

from action import Build, NoneAction, Action
from agent import Agent, MinimaxAgent
from structure import Structure
from tile import Tile
from game import Game
from board import Board
from player import Player
from card import Card
from constants import *
from util import hex_to_pixel

pygame.init()

TILE_COLORS = {
    Tile.Type.FOREST: (34, 139, 34),     # Forest Green
    Tile.Type.PASTURE: (144, 238, 144),  # Light Green
    Tile.Type.GRAIN: (255, 215, 0),      # Gold
    Tile.Type.BRICK: (178, 34, 34),      # Firebrick
    Tile.Type.ORE: (119, 136, 153),      # SlateGray
    Tile.Type.DESERT: (245, 245, 220),   # Beige
}

# Button states
class ButtonState(Enum):
    NORMAL = 0
    HOVER = 1
    ACTIVE = 2

class Button:
    def __init__(self, x, y, width, height, text, callback, color=(100, 100, 100)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.base_color = color
        self.hover_color = tuple(min(c + 30, 255) for c in color)
        self.active_color = tuple(max(c - 30, 0) for c in color)
        self.state = ButtonState.NORMAL
        self.font = pygame.font.SysFont(None, 24)
    
    def draw(self, screen):
        if self.state == ButtonState.NORMAL:
            color = self.base_color
        elif self.state == ButtonState.HOVER:
            color = self.hover_color
        else:  # ACTIVE
            color = self.active_color
            
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # Border
        
        # Render text
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.state = ButtonState.HOVER
            else:
                self.state = ButtonState.NORMAL
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.state = ButtonState.ACTIVE
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            was_active = self.state == ButtonState.ACTIVE
            if self.rect.collidepoint(event.pos):
                self.state = ButtonState.HOVER
                if was_active:
                    self.callback()
            else:
                self.state = ButtonState.NORMAL
        return False

class GameGUI:
    def __init__(self, game: Game):
        self.game = game
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Catan")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 36)

        self.center_x = CENTER_X
        self.center_y = CENTER_Y

        self.selected_action = None
        self.highlighted_element = None
        self.roll_result = None
        self.message = None
        self.buttons = []
        self.game_over = False
        self.winner = None

        self.setup_ui()

        self.intersection_coords = {}
        self.edge_coords = {}

        self.awaiting_settlement = True
        self.awaiting_road = False
    
    def setup_ui(self):
        """
        Sets up the main UI components and frames.
        """
        button_width = 160
        button_height = 40
        button_margin = 10
        button_x = SCREEN_WIDTH - button_width - 20
        button_y = 20

        self.buttons = [
            Button(button_x, button_y, button_width, button_height, 
                   "Build Road", lambda: self.select_action("build_road"), (139, 69, 19)),
            Button(button_x, button_y + button_height + button_margin, button_width, button_height, 
                   "Build Settlement", lambda: self.select_action("build_settlement"), (205, 133, 63)),
            Button(button_x, button_y + 2 * (button_height + button_margin), button_width, button_height, 
                   "Build City", lambda: self.select_action("build_city"), (255, 215, 0)),
            Button(button_x, button_y + 3 * (button_height + button_margin), button_width, button_height, 
                   "End Turn", lambda: self.select_action("end_turn"), (100, 100, 100))
        ]
    
    def select_action(self, action):
        """
        Handles whenever the user selects an action.
        :param action: The action taken by user.
        """
        if self.game.phase is not Game.Phase.NORMAL or self.game_over:
            return
        
        self.selected_action = action
        self.highlighted_element = None
        
        if action == "end_turn":
            self.end_turn()
        
    def end_turn(self):
        """
        Called whenever the user ends their turn.
        """
        self.game.end_turn()
        self.selected_action = None

        self.message = f"{self.game.current_player.id}'s turn"

        if self.game.phase is Game.Phase.NORMAL:
            self.roll_dice()

        self.game.turn_counter += 1
    
    def roll_dice(self):
        """
        Handles rolling the die, and distributing cards.
        """
        roll_value = Game.roll()
        self.roll_result = roll_value
        self.message = f"Rolled: {roll_value}"
        self.game.handle_roll(roll_value)
    
    def pixel_to_hex(self, x, y):
        """
        Converts x,y coords to q,r axial coords.
        :param x: X value.
        :param y: Y value.
        """
        x = (x - self.center_x) / HEX_SIZE
        y = (y - self.center_y) / HEX_SIZE

        q = (math.sqrt(3)/3 * x - 1/3 * y)
        r = (2/3 * y)
        
        return q, r
    
    def draw_hex(self, screen, q, r, color):
        """
        Draws a tile as a hexagon.
        :param screen: The screen to draw on.
        :param q: The q value.
        :param r: The r value.
        :param color: Color of the hexagon.
        """
        x, y = hex_to_pixel(q, r)

        vertices = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            vx = x + HEX_SIZE * math.cos(angle_rad)
            vy = y + HEX_SIZE * math.sin(angle_rad)
            vertices.append((vx, vy))
        
        pygame.draw.polygon(screen, color, vertices)
        pygame.draw.polygon(screen, BLACK, vertices, 2)
        
        return vertices
    
    def draw_board(self):
        """
        Draws the game board and all the items.
        """
        self.screen.fill(WHITE)
        self.intersection_coords.clear()
        self.edge_coords.clear()

        for coord, tile in self.game.board.grid.items():
            q, r = coord
            color = TILE_COLORS[tile.type]
            self.draw_hex(self.screen, q, r, color)

            if tile.type != Tile.Type.DESERT:
                x, y = hex_to_pixel(q, r)
                num_text = self.font.render(str(tile.roll), True, BLACK)
                num_rect = num_text.get_rect(center=(x, y))
                pygame.draw.circle(self.screen, WHITE, (x, y), 15)
                self.screen.blit(num_text, num_rect)

        self.draw_intersections_and_edges()
        self.draw_player_panel()

        if self.game.phase is Game.Phase.NORMAL and not self.game_over:
            for button in self.buttons:
                button.draw(self.screen)

        self.draw_messages()
    
    def draw_intersections_and_edges(self):
        """
        Draws all the intersections and edges.
        """
        for edge_loc, edge in self.game.board.edges.items():
            if edge.location.is_edge():
                (px1, py1), (px2, py2) = edge.location.coords

                edge_center = ((px1 + px2) / 2, (py1 + py2) / 2)
                self.edge_coords[edge_center] = edge.location
                
                # Determine color and width based on whether there's a road.
                color = GRAY
                width = 2
                if edge.road is not None:
                    color = edge.road.owner.color
                    width = EDGE_WIDTH

                if self.highlighted_element == edge.location:
                    color = (255, 255, 255)
                    width += 2
                
                pygame.draw.line(self.screen, color, (px1, py1), (px2, py2), width)

        for loc, intersection in self.game.board.intersections.items():
            x, y = loc.coords
            px, py = x, y

            self.intersection_coords[(px, py)] = loc

            color = GRAY
            size = INTERSECTION_SIZE
            
            if intersection.structure is not None:
                color = intersection.structure.owner.color

                if intersection.structure.type == Structure.Type.CITY:
                    size = INTERSECTION_SIZE * 1.5

            if self.highlighted_element == loc:
                color = (255, 255, 255)
                size += 2
            
            pygame.draw.circle(self.screen, color, (px, py), size)
    
    def draw_player_panel(self):
        """
        Draws the player information panel which includes current player and resources.
        """
        panel_x = 20
        panel_y = 20
        panel_width = 250
        panel_height = 120 * len(self.game.players)
        
        pygame.draw.rect(self.screen, (240, 240, 240), 
                         (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, BLACK, 
                         (panel_x, panel_y, panel_width, panel_height), 2)
        
        for i, player in enumerate(self.game.players):
            player_y = panel_y + i * 120

            if player == self.game.current_player:
                pygame.draw.rect(self.screen, (220, 220, 255), 
                                 (panel_x + 2, player_y + 2, panel_width - 4, 116))

            player_color = player.color
            name_text = self.font.render(f"{player.id}", True, player_color)
            points_text = self.font.render(f"Points: {player.points}", True, BLACK)
            
            self.screen.blit(name_text, (panel_x + 10, player_y + 10))
            self.screen.blit(points_text, (panel_x + 10, player_y + 35))

            card_counts = {}
            for card in player.cards:
                if card.type in card_counts:
                    card_counts[card.type] += 1
                else:
                    card_counts[card.type] = 1
            
            resource_y = player_y + 60
            for j, (card_type, count) in enumerate(card_counts.items()):
                color = TILE_COLORS[card_type]
                resource_text = self.font.render(f"{count}", True, BLACK)
                pygame.draw.rect(self.screen, color, 
                                 (panel_x + 15 + j * 30, resource_y, 15, 15))
                self.screen.blit(resource_text, (panel_x + 15 + j * 30, resource_y + 20))
    
    def draw_messages(self):
        """
        Draws messages, states, roll results, etc.
        """
        message_area = pygame.Rect(300, 20, 500, 80)
        pygame.draw.rect(self.screen, (240, 240, 240), message_area)
        pygame.draw.rect(self.screen, BLACK, message_area, 2)

        if self.message:
            message_text = self.font.render(self.message, True, BLACK)
            self.screen.blit(message_text, (message_area.x + 10, message_area.y + 10))

        if self.selected_action:
            action_text = self.font.render(f"Selected: {self.selected_action.replace('_', ' ').title()}", True, BLACK)
            self.screen.blit(action_text, (message_area.x + 250, message_area.y + 10))

        if self.game_over and self.winner:
            victory_text = self.big_font.render(f"{self.winner.id} wins!", True, self.winner.color)
            text_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            pygame.draw.rect(self.screen, (255, 255, 255), text_rect.inflate(20, 20))
            pygame.draw.rect(self.screen, self.winner.color, text_rect.inflate(20, 20), 3)
            self.screen.blit(victory_text, text_rect)
    
    def find_closest_element(self, mouse_pos, max_distance=20):
        """
        To make it easier to click, find the closest element in a certain range of the mouse click.
        :param mouse_pos: The current mouse position.
        :param max_distance: The limit to how far an item away can be from mouse.
        :return: The closest element.
        """
        x, y = mouse_pos
        closest_element = None
        min_distance = max_distance

        for (ix, iy), location in self.intersection_coords.items():
            distance = math.sqrt((x - ix) ** 2 + (y - iy) ** 2)
            if distance < min_distance:
                min_distance = distance
                closest_element = location

        for (ex, ey), location in self.edge_coords.items():
            distance = math.sqrt((x - ex) ** 2 + (y - ey) ** 2)
            if distance < min_distance:
                min_distance = distance
                closest_element = location
        
        return closest_element
    
    def handle_board_click(self):
        """
        Handles a click on the board that is not a button or a intersection/edge.
        """
        element = self.highlighted_element
        
        if not element:
            return

        if self.game.phase is not Game.Phase.NORMAL:
            if self.awaiting_settlement and element.is_intersection():
                self.place_initial_settlement(element)
            elif self.awaiting_road and element.is_edge():
                self.place_initial_road(element)
            return

        if self.selected_action == "build_road" and element.is_edge():
            self.build(Structure.Type.ROAD, element)
        elif self.selected_action == "build_settlement" and element.is_intersection():
            self.build(Structure.Type.SETTLEMENT, element)
        elif self.selected_action == "build_city" and element.is_intersection():
            self.build(Structure.Type.CITY, element)
    
    def place_initial_settlement(self, location):
        """
        Helps the user place a settlement before the main game starts.
        :param location: The coord to build at.
        """
        intersection = self.game.board.get_at_location(location)
        
        if not intersection or intersection.structure is not None:
            self.message = "Invalid location: Already occupied"
            return

        for adj_intersection in intersection.adjacent_intersections:
            if adj_intersection.structure is not None:
                self.message = "Too close to another settlement"
                return

        self.game.build(Structure.Type.SETTLEMENT, location)

        if self.game.turn_counter < 3:
            self.game.first_round_settlements[self.game.current_player.id].append(intersection)

        self.game.last_settlement_placed = intersection
        self.awaiting_settlement = False
        self.awaiting_road = True
        self.game.phase = Game.Phase.ROAD
        self.message = "Place a road connected to your settlement"
    
    def place_initial_road(self, location):
        """
        Helps a user place a road before the main game starts and after a settlement.
        :param location: The location to build on.
        """
        edge = self.game.board.get_at_location(location)

        if not edge or edge.road is not None:
            self.message = "Invalid location: Already occupied"
            return

        is_connected = False
        if self.game.last_settlement_placed:
            if edge.start == self.game.last_settlement_placed or edge.end == self.game.last_settlement_placed:
                is_connected = True
        
        if not is_connected:
            self.message = "Road must connect to your settlement"
            return

        self.game.build(Structure.Type.ROAD, location)

        if self.game.turn_counter > 2:
            self.distribute_initial_resources()

        self.awaiting_road = False
        self.awaiting_settlement = True
        
        if self.game.turn_counter <= len(self.game.players):
            # If we've gone through all players, switch to second round.
            if self.game.turn_counter == len(self.game.players):
                self.message = "Second round: Place your second settlement"
            else:
                self.game.current_player_index = (self.game.current_player_index + 1) % len(self.game.players)
                self.game.current_player = self.game.players[self.game.current_player_index]
                self.message = f"{self.game.current_player.id}'s turn to place a settlement"

            self.game.phase = Game.Phase.SETTLEMENT
        else:
            # Move to previous player in reverse order.
            self.game.current_player_index = (self.game.current_player_index - 1) % len(self.game.players)
            self.game.current_player = self.game.players[self.game.current_player_index]
            
            # If we've gone through all players, switch to main game.
            if self.game.turn_counter == 4:
                self.game.phase = Game.Phase.NORMAL
                self.game.current_player_index = 0
                self.game.current_player = self.game.players[0]
                self.message = "Main game begins! Roll the dice"
                self.roll_dice()
            else:
                self.game.phase = Game.Phase.SETTLEMENT
                self.message = f"{self.game.current_player.id}'s turn to place a settlement"

        self.game.turn_counter += 1

    def distribute_initial_resources(self):
        """
        After the user places their second settlement, give them the resources.
        :return:
        """
        if self.game.last_settlement_placed:
            for tile in self.game.last_settlement_placed.adjacent_tiles:
                if tile.type != Tile.Type.DESERT:
                    self.game.current_player.add_card(Card(tile.type))
    
    def build(self, structure_type, location):
        """
        Handles building a structure during the main game.
        :param structure_type: The type of structure to build
        :param location: The location to build at.
        """
        success = self.game.build(structure_type, location)
        
        if success:
            self.message = f"{structure_type.value} built successfully!"
        else:
            self.message = f"Cannot build {structure_type.value} here"

        self.selected_action = None

        winner = self.game.game_winner()
        if winner and not self.game_over:
            self.game_over = True
            self.winner = winner
            self.message = f"{winner.id} wins with {winner.points} victory points!"

    def handle_agent(self, action: Action):
        """
        Handles actions taken by the agent.
        :param action: The action the agent wants to take.
        """
        match action:
            case Build(type=t, location=loc):
                match self.game.phase:
                    case Game.Phase.NORMAL:
                        self.build(t, loc)
                        self.end_turn()
                    case Game.Phase.SETTLEMENT:
                        self.place_initial_settlement(loc)
                    case Game.Phase.ROAD:
                        self.place_initial_road(loc)
            case NoneAction():
                self.end_turn()

    def run(self):
        """
        The main game loop. Updates the view and handles events.
        """
        self.message = "Initial placement: Place your first settlement"
        self.draw_board()
        pygame.display.flip()
        
        next_ai_turn_time = 0
        ai_turn_delay = 500
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
            
            if not running:
                break
                
            current_time = pygame.time.get_ticks()

            # AI player.
            if not self.winner and hasattr(self.game.current_player, 'get_action') and current_time >= next_ai_turn_time:
                self.message = f"{self.game.current_player.id} is thinking..."
                self.draw_board()
                pygame.display.flip()

                agent: Agent = self.game.current_player
                action = agent.get_action(self.game)

                self.draw_board()
                pygame.display.flip()
                pygame.time.delay(500)

                self.handle_agent(action)
                next_ai_turn_time = pygame.time.get_ticks() + ai_turn_delay
                
            # Handle human player.
            elif not hasattr(self.game.current_player, 'get_action'):
                mouse_pos = pygame.mouse.get_pos()
                self.highlighted_element = self.find_closest_element(mouse_pos)
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break

                    button_clicked = False
                    for button in self.buttons:
                        if button.handle_event(event):
                            button_clicked = True

                    if not button_clicked and event.type == pygame.MOUSEBUTTONDOWN:
                        self.handle_board_click()
            
            self.draw_board()
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

def start_gui_game():
    """
    Creates players, board, and starts game.
    """
    player1 = MinimaxAgent("Player 1", (51, 93, 184))
    player2 = MinimaxAgent("Player 2", (184, 51, 71))
    board = Board.create_default_board()
    game = Game(board, [player1, player2])
    
    gui = GameGUI(game)
    gui.run()

if __name__ == "__main__":
    start_gui_game()