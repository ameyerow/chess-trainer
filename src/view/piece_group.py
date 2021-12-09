import pygame

class PieceGroup(pygame.sprite.Group):
    def by_resting(self, sprite):
        return not sprite.resting
    
    def draw(self, surface):
        sprites = self.sprites()
        surface_blit = surface.blit

        for sprite in sorted(sprites, key=self.by_resting):
            surface_blit(sprite.background, sprite.background_rect)
            self.spritedict[sprite] = surface_blit(sprite.image, sprite.rect)
        self.lostsprites = []
