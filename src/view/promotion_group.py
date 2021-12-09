import pygame

from .promotion_view import PromotionView


class PromotionGroup(pygame.sprite.Group):
    def draw(self, surface):
        promotion_views = self.sprites()
        surface_blit = surface.blit

        for promotion_view in promotion_views:
            promotion_view: PromotionView = promotion_view
            surface_blit(promotion_view.background, promotion_view.background_rect)
            
            if promotion_view.background.get_alpha() > 0:
                size = promotion_view.sprite_size
                for i in range(len(promotion_view.images)):
                    image = promotion_view.images[i]
                    rect = promotion_view.rects[i]
                    surface_blit(image, rect)
        self.lostsprites = []
