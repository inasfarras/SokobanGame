# sokoban.py
import sys
import pygame
from game import Game
from button import Button
from level_manager import LevelManager
import constants
import time
from solver import Solver

class SokobanGame:
    def __init__(self):
        pygame.init()

        # Set up screen dimensions
        self.screen_width = 1000  # Increased width to accommodate sidebar
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Sokoban Game')

        # Load images
        self.wall = pygame.image.load('images/wall.png')
        self.floor = pygame.image.load('images/floor.png')
        self.box = pygame.image.load('images/box.png')
        self.box_docked = pygame.image.load('images/box_docked.png')
        self.worker = pygame.image.load('images/worker.png')
        self.worker_docked = pygame.image.load('images/worker_dock.png')
        self.docker = pygame.image.load('images/dock.png')

        # Initialize game components
        self.level_manager = LevelManager('levels', 3)  # Level file and number of levels
        self.level = 1
        level_matrix = self.level_manager.load_level(self.level)
        self.game = Game(level_matrix)
        self.buttons = self.setup_buttons()
        self.selected_algorithm = "BFS"  # Default algorithm

    def setup_buttons(self):
        # Set up buttons with new layout for sidebar
        buttons = {
            "next_level": Button("Next Level", (820, 50), constants.BUTTON_COLORS["next_level"]),
            "previous_level": Button("Previous Level", (820, 120), constants.BUTTON_COLORS["previous_level"]),
            "reset": Button("Reset", (820, 190), constants.BUTTON_COLORS["reset"]),
            "solve_bfs": Button("Solve BFS", (820, 260), constants.BUTTON_COLORS["auto_solve"]),
            "solve_dfs": Button("Solve DFS", (820, 330), constants.BUTTON_COLORS["auto_solve"]),
            "solve_astar": Button("Solve A*", (820, 400), constants.BUTTON_COLORS["auto_solve"]),
        }
        return buttons

    def run(self):
        running = True
        level_completed = False
        completion_time = 0

        while running:
            self.screen.fill(constants.BACKGROUND_COLOR)

            # Draw game elements and buttons
            self.draw_game()
            self.draw_buttons()
            self.draw_status_panel()

            # Check for level completion
            if self.game.is_completed() and not level_completed:
                level_completed = True
                completion_time = time.time()  # Record the completion time
                self.draw_level_completed_message()

            # Automatically advance to the next level after a delay
            if level_completed and time.time() - completion_time > 2:  # Wait for 2 seconds
                if self.level < self.level_manager.max_level:
                    self.next_level()
                    level_completed = False
                else:
                    self.display_win_banner()
                    self.level = 1
                    self.reset_level()

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and not level_completed:
                    if event.key == pygame.K_UP:
                        self.game.move(0, -1)  # Move up
                    elif event.key == pygame.K_DOWN:
                        self.game.move(0, 1)   # Move down
                    elif event.key == pygame.K_LEFT:
                        self.game.move(-1, 0)  # Move left
                    elif event.key == pygame.K_RIGHT:
                        self.game.move(1, 0)   # Move right
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    for key, button in self.buttons.items():
                        if button.rect.collidepoint(mouse_pos):
                            if key == "next_level":
                                self.next_level()
                                level_completed = False
                            elif key == "previous_level":
                                self.previous_level()
                                level_completed = False
                            elif key == "reset":
                                self.reset_level()
                                level_completed = False
                            elif key == "solve_bfs":
                                self.auto_solve("BFS")
                            elif key == "solve_dfs":
                                self.auto_solve("DFS")
                            elif key == "solve_astar":
                                self.auto_solve("A*")

            # Update display
            pygame.display.update()

    def solver_callback(self, current_matrix, moves, elapsed_time):
        """Callback method for real-time updates while the solver is running."""
        self.game.set_matrix(current_matrix)  # Update the game matrix
        self.draw_game()  # Redraw the game board

        # Display current moves and elapsed time
        font = pygame.font.Font(None, 24)
        # Draw background rectangles for text
        pygame.draw.rect(self.screen, (0, 0, 0), (10, 10, 200, 25))  # Background for timer
        pygame.draw.rect(self.screen, (0, 0, 0), (10, 40, 300, 25))  # Background for moves

        timer_text = f"Elapsed Time: {elapsed_time:.2f}s"
        timer_surface = font.render(timer_text, True, (255, 255, 255))
        timer_rect = timer_surface.get_rect(topleft=(10, 10))
        self.screen.blit(timer_surface, timer_rect)

        # Extract only the direction part for displaying
        directions = ''.join([move[2] for move in moves])  # Get the direction part from each tuple
        moves_surface = font.render(f"Moves: {directions}", True, (255, 255, 255))
        moves_rect = moves_surface.get_rect(topleft=(10, 40))
        self.screen.blit(moves_surface, moves_rect)

        pygame.display.update()
        # pygame.time.delay(1)  # Increased delay for more stable movement visualization
    # Add delay to make changes visible

    def auto_solve(self, algorithm):
        # Reset the game to the initial state before solving
        self.reset_level()
        
        solver = Solver(self.game)
        start_time = time.time()

        # Find solution based on the selected algorithm
        if algorithm == "BFS":
            solution = solver.find_solution_bfs(callback=self.solver_callback)
        elif algorithm == "DFS":
            solution = solver.find_solution_dfs(callback=self.solver_callback)
        elif algorithm == "A*":
            solution = solver.find_solution_a_star(callback=self.solver_callback)

        elapsed_time = time.time() - start_time
        self.display_solution_banner(algorithm, solution, elapsed_time)

        if solution:
            # Save the solution
            print(f"Solution saved: {solution}")

            # Reset the game again to initial state before executing the solution
            self.reset_level()

            # Execute the solution moves after resetting
            for move in solution:
                dx, dy, direction = move
                self.game.move(dx, dy)
                self.draw_game()
                pygame.display.update()
                pygame.time.delay(100)  # Delay to show each move

        else:
            print("No solution found")


    def draw_game(self):
        # Calculate offsets to center the game board
        board_width = len(self.game.get_matrix()[0]) * 32
        board_height = len(self.game.get_matrix()) * 32
        offset_x = (self.screen_width - 200 - board_width) // 2  # Adjusted to leave space for sidebar
        offset_y = (self.screen_height - board_height) // 2

        # Draw game elements
        for y, row in enumerate(self.game.get_matrix()):
            for x, cell in enumerate(row):
                pos = (offset_x + x * 32, offset_y + y * 32)
                self.screen.blit(self.floor, pos)
                if cell == '#':
                    self.screen.blit(self.wall, pos)
                elif cell == '.':
                    self.screen.blit(self.docker, pos)
                elif cell == '$':
                    self.screen.blit(self.box, pos)
                elif cell == '*':
                    self.screen.blit(self.box_docked, pos)
                elif cell == '@':
                    self.screen.blit(self.worker, pos)
                elif cell == '+':
                    self.screen.blit(self.worker_docked, pos)

    def draw_buttons(self):
        # Draw buttons on the sidebar
        for button in self.buttons.values():
            button.draw(self.screen)

    def draw_status_panel(self):
        # Draw the status panel on the right side of the screen
        font = pygame.font.Font(None, 36)

        # Display current level
        level_text = font.render(f"Level: {self.level}", True, (255, 255, 255))
        self.screen.blit(level_text, (820, 10))

    def draw_level_completed_message(self):
        # Draw message when level is completed
        font = pygame.font.Font(None, 36)
        text = font.render("Level Completed!", True, (0, 255, 0))
        text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.screen.blit(text, text_rect)

    def display_solution_banner(self, algorithm, solution, elapsed_time):
        # Display a banner showing the solution found and the time taken
        font = pygame.font.Font(None, 36)
        solution_text = f"[{algorithm}] Solution Found in {elapsed_time:.2f}s!"
        
        # Extract only the direction from each move tuple
        moves_text = ''.join([direction for _, _, direction in solution])
        
        # Create surfaces to display the text
        text = font.render(solution_text, True, (0, 0, 0), (0, 255, 0))
        text_rect = text.get_rect(center=(self.screen_width // 2, 30))
        self.screen.blit(text, text_rect)
        
        moves_render = font.render(moves_text, True, (0, 0, 0), (0, 255, 0))
        moves_rect = moves_render.get_rect(center=(self.screen_width // 2, 70))
        self.screen.blit(moves_render, moves_rect)

        pygame.display.update()


    def get_direction_from_coords(self, dx, dy):
        if dx == 0 and dy == -1:
            return 'U'
        elif dx == 0 and dy == 1:
            return 'D'
        elif dx == -1 and dy == 0:
            return 'L'
        elif dx == 1 and dy == 0:
            return 'R'
        return ''

    def next_level(self):
        # Load the next level if available
        if self.level < self.level_manager.max_level:
            self.level += 1
            self.reset_level()
        else:
            self.display_win_banner()
            self.level = 1
            self.reset_level()

    def previous_level(self):
        # Load the previous level if available
        self.level = max(1, self.level - 1)
        self.reset_level()

    def reset_level(self):
        # Reset the current level to its initial state
        try:
            level_matrix = self.level_manager.load_level(self.level)
            self.game = Game(level_matrix)
        except ValueError as e:
            print(f"ERROR: {e}")

    def display_win_banner(self):
        # Display a banner when the player wins all levels
        font = pygame.font.Font(None, 48)
        win_text = "You Win!!! Returning to Level 1."
        text = font.render(win_text, True, (255, 255, 255), (0, 128, 0))
        text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.screen.blit(text, text_rect)
        pygame.display.update()
        pygame.time.delay(100)  # Delay to show the banner

if __name__ == "__main__":
    SokobanGame().run()
    pygame.quit()
    sys.exit()
