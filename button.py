import pygame

class Button:
    def __init__(self, text, position, color):
        self.text = text
        self.position = position
        self.color = color
        self.font = pygame.font.Font(None, 36)
        self.rect = pygame.Rect(position[0], position[1], 180, 50)  # Set the size of the button

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surf = self.font.render(self.text, True, (0, 0, 0))  # Text color is black
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

