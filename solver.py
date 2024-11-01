import copy
from collections import deque
from typing import List, Tuple, Set
from game import Game
from deadlock import DeadlockDetector
import time
import heapq


class Solver:
    def __init__(self, initial_game):
        self.initial_game = initial_game
        self.visited = set()
        self.start_time = time.time()


    from collections import deque

    def find_solution_bfs(self, callback=None):
        queue = deque([(self.initial_game.get_matrix(), self.initial_game.worker(), [])])
        self.visited = set()
        worker_x, worker_y, _ = self.initial_game.worker()  # Unpack only what's needed
        self.visited.add(self._serialize_state(self.initial_game.get_matrix(), worker_x, worker_y))

        while queue:
            current_matrix, (worker_x, worker_y, _), moves = queue.popleft()

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
                    new_state = (new_game.get_matrix(), new_game.worker(), moves + [(dx, dy, direction)])
                    
                    # Serialize and check visited and deadlock before adding to the queue
                    new_worker_x, new_worker_y, _ = new_game.worker()
                    new_state_key = self._serialize_state(new_state[0], new_worker_x, new_worker_y)
                    
                    if new_state_key not in self.visited and not DeadlockDetector.is_deadlock(new_state[0]):
                        self.visited.add(new_state_key)
                        queue.append(new_state)

        print("No solution found")
        return []



    def find_solution_dfs(self, callback=None):
        stack = [(self.initial_game.get_matrix(), self.initial_game.worker(), [])]
        self.visited = set()

        while stack:
            current_matrix, (worker_x, worker_y, _), moves = stack.pop()
            state_key = self._serialize_state(current_matrix, worker_x, worker_y)

            # If already visited, skip this state
            if state_key in self.visited:
                continue

            # Check if the current state is a deadlock
            if DeadlockDetector.is_deadlock(current_matrix):
                # If a deadlock is detected, skip without adding to visited
                print("Deadlock detected, backtracking")
                continue

            # Mark the current state as visited
            self.visited.add(state_key)

            # Check if the current state is a solution
            if self._is_solution(current_matrix):
                print("Solution found:", moves)
                return moves

            # Call the callback function if provided (useful for visualizations or progress monitoring)
            if callback:
                elapsed_time = time.time() - self.start_time
                callback(current_matrix, moves, elapsed_time)

            # Generate possible moves
            possible_moves = [(-1, 0, 'L'), (1, 0, 'R'), (0, -1, 'U'), (0, 1, 'D')]

            for dx, dy, direction in possible_moves:
                # Create a new game instance based on the current state
                new_game = Game(copy.deepcopy(current_matrix))

                # Check if the worker can move or push in the given direction
                if new_game.can_move(dx, dy) or new_game.can_push(dx, dy):
                    new_game.move(dx, dy, save=False)
                    new_state = (new_game.get_matrix(), new_game.worker(), moves + [(dx, dy, direction)])
                    new_worker_x, new_worker_y, _ = new_game.worker()
                    new_state_key = self._serialize_state(new_state[0], new_worker_x, new_worker_y)

                    if new_state_key not in self.visited:
                        stack.append(new_state)

        print("No solution found")
        return []






    def find_solution_a_star(self, callback=None):
    # Heuristic function to estimate distance from current state to goal
        def heuristic(matrix):
            if not hasattr(self, '_goal_positions'):
                self._goal_positions = [(y, x) for y, row in enumerate(matrix) for x, cell in enumerate(row) if cell == '.']
            box_positions = [(y, x) for y, row in enumerate(matrix) for x, cell in enumerate(row) if cell == '$']

            # Sum of minimum distances from each box to a goal
            distance_sum = 0
            for box in box_positions:
                distances = [abs(box[0] - goal[0]) + abs(box[1] - goal[1]) for goal in self._goal_positions]
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

        # Priority queue for the open list, using heapq
        open_list = []
        initial_heuristic = heuristic(self.initial_game.get_matrix())
        heapq.heappush(open_list, (initial_heuristic, 0, self.initial_game.get_matrix(), self.initial_game.worker(), []))
        self.visited = set()

        while open_list:
            # Pop the state with the lowest estimated cost
            _, g, current_matrix, (worker_x, worker_y, _), moves = heapq.heappop(open_list)
            state_key = self._serialize_state(current_matrix, worker_x, worker_y)

            if state_key in self.visited:
                continue

            # Use DeadlockDetector to check for deadlocks
            if DeadlockDetector.is_deadlock(current_matrix):
                print("Deadlock detected, skipping state")
                continue

            # Mark the current state as visited
            self.visited.add(state_key)

            # Check if the current state is a solution
            if self._is_solution(current_matrix):
                print("Solution found:", moves)
                return moves

            # Call the callback function if provided
            if callback:
                elapsed_time = time.time() - self.start_time
                callback(current_matrix, moves, elapsed_time)

            # Generate possible moves and add them to the priority queue
            possible_moves = [(-1, 0, 'L'), (1, 0, 'R'), (0, -1, 'U'), (0, 1, 'D')]
            for dx, dy, direction in possible_moves:
                new_game = Game(copy.deepcopy(current_matrix))
                if new_game.can_move(dx, dy) or new_game.can_push(dx, dy):
                    new_game.move(dx, dy, save=False)
                    new_matrix = new_game.get_matrix()

                    # Skip deadlocked states
                    if DeadlockDetector.is_deadlock(new_matrix):
                        print("Move led to deadlock, skipping")
                        continue

                    h = heuristic(new_matrix)
                    heapq.heappush(open_list, (g + 1 + h, g + 1, new_matrix, new_game.worker(), moves + [(dx, dy, direction)]))

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
