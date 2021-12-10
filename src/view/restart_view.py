import pygame

from .utils.screen_pos import ScreenPos
from .utils.colors import Colors


class RestartView(pygame.sprite.Sprite):
    def __init__(self, 
                sprite_size: int,
                board_offset: ScreenPos):
        pygame.sprite.Sprite.__init__(self)

        self.sprite_size = sprite_size
        self.board_offset = board_offset

        self.background = pygame.Surface((3*sprite_size//2, 2*sprite_size//3))
        self.background.fill(Colors.WHITE.value)
        pygame.draw.rect(self.background, Colors.BLACK.value, [0, 0, 3*sprite_size//2, 2*sprite_size//3], 1)
        self.background.set_alpha(0)

        self.background_rect = self.background.get_rect()
        self.background_rect.center = (self.board_offset.x + 4 * self.sprite_size,\
                                       self.board_offset.y + 4 * self.sprite_size)

    
    def update(self, prompt_for_restart: bool):
        if prompt_for_restart:
            self.background.set_alpha(255)
        else:
            self.background.set_alpha(0)

    def draw(self, surface):
        surface_blit = surface.blit

        surface_blit(self.background, self.background_rect)
        if self.background.get_alpha() > 0:
            font_size = self.sprite_size // 4
            font = pygame.font.SysFont('Arial', font_size)
            width, height = font.size("Restart")

            x = self.background_rect.x + (self.background_rect.width - width) // 2
            y = self.background_rect.y + (self.background_rect.height - height) // 2

            text_surface = font.render("Restart", True, Colors.BLACK.value)
            surface_blit(text_surface, (x, y))

    def click(self, mouse_screen_pos: ScreenPos) -> bool:
        if self.background_rect.collidepoint((mouse_screen_pos[0], mouse_screen_pos[1])):
            return True
        else:
            return False

    