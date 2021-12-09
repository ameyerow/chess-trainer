import pygame

from .tile_effect_view import TileEffectView


class TileGroup(pygame.sprite.Group):
    def draw(self, surface):
        tiles = self.sprites()
        surface_blit = surface.blit

        for tile in tiles:
            tile: TileEffectView = tile
            surface_blit(tile.background, tile.background_rect)
            surface_blit(tile.hint_background, tile.hint_background_rect)
            self.spritedict[tile] = surface_blit(tile.image, tile.rect)
        self.lostsprites = []
