import copy
from collections import deque
from typing import List, Tuple, Set
from game import Game
from deadlock import DeadlockDetector
import time

class Solver:
    def __init__(self, initial_game):
        self.initial_game = initial_game
        self.visited = set()
        self.start_time = time.time()

    def find_solution_bfs(self, callback=None):
        queue = deque([(self.initial_game.get_matrix(), self.initial_game.worker(), [])])
        self.visited = set()

        while queue:
            current_matrix, (worker_x, worker_y, _), moves = queue.popleft()
            state_key = self._serialize_state(current_matrix, worker_x, worker_y)

            if state_key in self.visited:
                continue

            # Use DeadlockDetector to check for deadlocks
            if DeadlockDetector.is_deadlock(current_matrix):
                print("Deadlock detected, skipping state")
                continue

            self.visited.add(state_key)

            # Check if the current state is a solution
            if self._is_solution(current_matrix):
                print("Solution found:", moves)
                return moves

            # Call the callback function if provided
            if callback:
                elapsed_time = time.time() - self.start_time
                callback(current_matrix, moves, elapsed_time)

            # Generate possible moves, with a more thorough exploration strategy
            possible_moves = [(-1, 0, 'L'), (1, 0, 'R'), (0, -1, 'U'), (0, 1, 'D')]
            for dx, dy, direction in possible_moves:
                new_game = Game(copy.deepcopy(current_matrix))
                if new_game.can_move(dx, dy) or new_game.can_push(dx, dy):
                    new_game.move(dx, dy, save=False)
                    queue.append((new_game.get_matrix(), new_game.worker(), moves + [(dx, dy, direction)]))

        print("No solution found")
        return []

    def find_solution_dfs(self, callback=None):
        stack = [(self.initial_game.get_matrix(), self.initial_game.worker(), [])]
        self.visited = set()

        while stack:
            current_matrix, (worker_x, worker_y, _), moves = stack.pop()
            state_key = self._serialize_state(current_matrix, worker_x, worker_y)

            if state_key in self.visited:
                continue

            # Use DeadlockDetector to check for deadlocks
            if DeadlockDetector.is_deadlock(current_matrix):
                print("Deadlock detected, skipping state")
                continue

            self.visited.add(state_key)

            # Check if the current state is a solution
            if self._is_solution(current_matrix):
                print("Solution found:", moves)
                return moves

            # Call the callback function if provided
            if callback:
                elapsed_time = time.time() - self.start_time
                callback(current_matrix, moves, elapsed_time)

            # Generate possible moves
            possible_moves = [(-1, 0, 'L'), (1, 0, 'R'), (0, -1, 'U'), (0, 1, 'D')]
            for dx, dy, direction in possible_moves:
                new_game = Game(copy.deepcopy(current_matrix))
                if new_game.can_move(dx, dy) or new_game.can_push(dx, dy):
                    new_game.move(dx, dy, save=False)
                    stack.append((new_game.get_matrix(), new_game.worker(), moves + [(dx, dy, direction)]))

        print("No solution found")
        return []

    def find_solution_a_star(self, callback=None):
        def heuristic(matrix):
            goal_positions = [(y, x) for y, row in enumerate(matrix) for x, cell in enumerate(row) if cell == '.']
            box_positions = [(y, x) for y, row in enumerate(matrix) for x, cell in enumerate(row) if cell == '$']
            
            # Sum of minimum distances from each box to a goal
            distance_sum = 0
            for box in box_positions:
                distances = [abs(box[0] - goal[0]) + abs(box[1] - goal[1]) for goal in goal_positions]
                if distances:
                    distance_sum += min(distances)

            # Penalty for each box not on a goal
            goal_penalty = len([box for box in box_positions if matrix[box[0]][box[1]] != '*'])
            
            # Penalty for boxes near walls but not on goals
            wall_penalty = 0
            for box in box_positions:
                y, x = box
                if ((y == 0 or y == len(matrix) - 1) or (x == 0 or x == len(matrix[0]) - 1)) and matrix[y][x] != '*':
                    wall_penalty += 10

            return distance_sum + (2 * goal_penalty) + wall_penalty

        open_list = [(heuristic(self.initial_game.get_matrix()), 0, self.initial_game.get_matrix(), self.initial_game.worker(), [])]
        self.visited = set()

        while open_list:
            open_list.sort(key=lambda x: x[0])  # Sort by heuristic value
            _, g, current_matrix, (worker_x, worker_y, _), moves = open_list.pop(0)
            state_key = self._serialize_state(current_matrix, worker_x, worker_y)

            if state_key in self.visited:
                continue

            # Use DeadlockDetector to check for deadlocks
            if DeadlockDetector.is_deadlock(current_matrix):
                print("Deadlock detected, skipping state")
                continue

            self.visited.add(state_key)

            # Check if the current state is a solution
            if self._is_solution(current_matrix):
                print("Solution found:", moves)
                return moves

            # Call the callback function if provided
            if callback:
                elapsed_time = time.time() - self.start_time
                callback(current_matrix, moves, elapsed_time)

            # Generate possible moves
            possible_moves = [(-1, 0, 'L'), (1, 0, 'R'), (0, -1, 'U'), (0, 1, 'D')]
            for dx, dy, direction in possible_moves:
                new_game = Game(copy.deepcopy(current_matrix))
                if new_game.can_move(dx, dy) or new_game.can_push(dx, dy):
                    new_game.move(dx, dy, save=False)
                    new_matrix = new_game.get_matrix()

                    print(f"Trying move {direction} from position {(worker_x, worker_y)}")
                    
                    if DeadlockDetector.is_deadlock(new_matrix):
                        print("Move led to deadlock, skipping")
                        continue

                    h = heuristic(new_matrix)
                    open_list.append((g + 1 + h, g + 1, new_matrix, new_game.worker(), moves + [(dx, dy, direction)]))

        print("No solution found")
        return []

    def _serialize_state(self, matrix, worker_x, worker_y):
        # Serialize the matrix and worker position to a string representation
        return f"{worker_x},{worker_y}:" + ''.join(''.join(row) for row in matrix)

    def _is_solution(self, matrix):
        # Check if all boxes are on goal positions
        for row in matrix:
            for cell in row:
                if cell == '$' or cell == '.':
                    return False
        return True
