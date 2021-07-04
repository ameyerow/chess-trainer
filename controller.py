import pygame
pygame.init()

import os
import sys
from view import *

SCREEN_SIZE = (800, 800)

def display_board():
    sprites_directory = os.path.join(os.getcwd(), "sprites")

    game_display = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("Repertoire Trainer")

    icon = pygame.image.load(os.path.join(sprites_directory, "BLACK_Q.png"))
    pygame.display.set_icon(icon)

    state_view = StateView(sprites_directory, size=(760, 760), pos=(20, 20))
    past_states = []

    moving_piece = None
    last_move = ((-1, -1), (-1, -1))
    legal_moves = []
    legal_captures = []
    while True:
        pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for piece in state_view.pieces:
                    if piece.rect.collidepoint(pos):
                        for other_piece in state_view.pieces:
                            if other_piece != piece:
                                other_piece.selected = False
                        piece.selected = True
                        legal_moves, legal_captures = state_view.state.legal_moves(piece.idx)
                        if pygame.mouse.get_pressed()[0]:
                            piece.resting = False
                            moving_piece = piece

            if event.type == pygame.MOUSEBUTTONUP:
                if not (moving_piece is None):
                    for tile in state_view.tiles:
                        if tile.rect.collidepoint(pos):
                            legal, _ = state_view.state.is_legal_move(moving_piece.idx, tile.idx)
                            if legal:
                                move = state_view.state.move_to_pgn_notation(moving_piece.idx, tile.idx)
                                new_state = state_view.state.update(move)
                                past_states.append(state_view.state)
                                state_view.update(new_state)

                                last_move = (moving_piece.idx, tile.idx)
                                legal_moves = []
                                legal_captures = []
                            break
                for piece in state_view.pieces:
                    piece.resting = True
                    moving_piece = None

        if not (moving_piece is None) and pygame.mouse.get_pressed()[0]:
            state_view.tiles.update(pos, legal_moves, legal_captures, last_move)
        else:
            state_view.tiles.update((-1,-1), legal_moves, legal_captures, last_move)   

        state_view.pieces.update(pos)

        game_display.fill(Colors.WHITE.value)
        state_view.draw(game_display)
        pygame.display.update()