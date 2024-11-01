from typing import List, Tuple
import queue

class Game:
    def __init__(self, level_matrix: List[str]):
        self.queue = queue.LifoQueue()
        self.matrix = [list(row) for row in level_matrix]

    def is_valid_value(self, char: str) -> bool:
        return char in [' ', '#', '@', '.', '*', '$', '+']

    def get_matrix(self) -> List[List[str]]:
        return self.matrix

    def set_matrix(self, new_matrix):
        self.matrix = new_matrix

    def is_completed(self) -> bool:
        for row in self.matrix:
            if '.' in row:  # Goal without a box
                return False
            if '$' in row:  # Loose box
                return False
        return True

    def worker(self) -> Tuple[int, int, str]:
        for y, row in enumerate(self.matrix):
            for x, cell in enumerate(row):
                if cell in ['@', '+']:
                    return x, y, cell
        raise ValueError("ERROR: Worker not found in the matrix")

    def can_move(self, dx: int, dy: int) -> bool:
        worker_x, worker_y, _ = self.worker()
        target_x, target_y = worker_x + dx, worker_y + dy
        # Check if target position is within the matrix bounds
        if 0 <= target_y < len(self.matrix) and 0 <= target_x < len(self.matrix[0]):
            target = self.get_content(target_x, target_y)
            return target in [' ', '.']  # Worker can only move to an empty space or goal
        return False

    def can_push(self, dx: int, dy: int) -> bool:
        worker_x, worker_y, _ = self.worker()
        target_x, target_y = worker_x + dx, worker_y + dy
        next_target_x, next_target_y = worker_x + 2 * dx, worker_y + 2 * dy

        # Boundary check for both target and next target
        if not (0 <= target_y < len(self.matrix) and 0 <= target_x < len(self.matrix[0])):
            return False
        if not (0 <= next_target_y < len(self.matrix) and 0 <= next_target_x < len(self.matrix[0])):
            return False

        target = self.get_content(target_x, target_y)
        next_target = self.get_content(next_target_x, next_target_y)
        return target in ['*', '$'] and next_target in [' ', '.']

    def get_content(self, x: int, y: int) -> str:
        # Boundary check
        if 0 <= y < len(self.matrix) and 0 <= x < len(self.matrix[y]):
            return self.matrix[y][x]
        # If out of bounds, treat it as a wall
        return '#'

    def move_worker(self, dx: int, dy: int, save: bool):
        worker_x, worker_y, worker_char = self.worker()
        target_x, target_y = worker_x + dx, worker_y + dy
        target_char = self.get_content(target_x, target_y)

        # Move the worker based on current and target cell types
        if worker_char == '@' and target_char == ' ':
            self.set_content(target_x, target_y, '@')
            self.set_content(worker_x, worker_y, ' ')
        elif worker_char == '@' and target_char == '.':
            self.set_content(target_x, target_y, '+')
            self.set_content(worker_x, worker_y, ' ')
        elif worker_char == '+' and target_char == ' ':
            self.set_content(target_x, target_y, '@')
            self.set_content(worker_x, worker_y, '.')
        elif worker_char == '+' and target_char == '.':
            self.set_content(target_x, target_y, '+')
            self.set_content(worker_x, worker_y, '.')

        if save:
            self.queue.put((dx, dy, False))

    def move_box(self, x: int, y: int, dx: int, dy: int):
        current_box = self.get_content(x, y)
        future_box = self.get_content(x + dx, y + dy)

        if current_box == '$' and future_box == ' ':
            self.set_content(x + dx, y + dy, '$')
            self.set_content(x, y, ' ')
        elif current_box == '$' and future_box == '.':
            self.set_content(x + dx, y + dy, '*')
            self.set_content(x, y, ' ')
        elif current_box == '*' and future_box == ' ':
            self.set_content(x + dx, y + dy, '$')
            self.set_content(x, y, '.')
        elif current_box == '*' and future_box == '.':
            self.set_content(x + dx, y + dy, '*')
            self.set_content(x, y, '.')

    def move(self, dx: int, dy: int, save: bool = True):
        if self.can_move(dx, dy):
            self.move_worker(dx, dy, save)
        elif self.can_push(dx, dy):
            worker_x, worker_y, _ = self.worker()
            self.move_box(worker_x + dx, worker_y + dy, dx, dy)
            self.move_worker(dx, dy, save)
            if save:
                self.queue.put((dx, dy, True))

    def set_content(self, x: int, y: int, content: str):
        if 0 <= y < len(self.matrix) and 0 <= x < len(self.matrix[y]):
            if self.is_valid_value(content):
                self.matrix[y][x] = content

    def unmove(self):
        if not self.queue.empty():
            movement = self.queue.get()
            dx, dy, pushed = movement

            if pushed:
                worker_x, worker_y, _ = self.worker()
                self.move_worker(-dx, -dy, False)
                self.move_box(worker_x + dx, worker_y + dy, -dx, -dy)
            else:
                self.move_worker(-dx, -dy, False)
