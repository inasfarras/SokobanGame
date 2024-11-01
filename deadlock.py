from collections import deque

class DeadlockDetector:
    @staticmethod
    def is_deadlock(matrix) -> bool:
        """
        Relaxed deadlock detection to allow exploration.
        Detect if the current state is a deadlock due to a box in a corner.
        """
        for y, row in enumerate(matrix):
            for x, cell in enumerate(row):
                # Check if there's a box ($) in a deadlock position (corner without a goal)
                if cell == '$' and not DeadlockDetector.is_goal(matrix, x, y):
                    if DeadlockDetector.is_corner(matrix, x, y):
                        return True
        return False

    @staticmethod
    def is_goal(matrix, x, y) -> bool:
        """
        Checks if a given position (x, y) is a goal.
        """
        return matrix[y][x] == '.'

    @staticmethod
    def is_box_cluster_deadlock(matrix) -> bool:
        """
        Detect if there is a deadlock involving multiple boxes.
        Specifically, if two or more boxes are grouped such that they cannot be moved to their goals.
        """
        box_positions = [(y, x) for y, row in enumerate(matrix) for x, cell in enumerate(row) if cell == '$']
        for box in box_positions:
            if not DeadlockDetector.can_reach_goal(matrix, box):
                return True
        return False

    @staticmethod
    def can_reach_goal(matrix, box) -> bool:
        """
        Determine if a box can reach a goal.
        This method uses BFS to see if there is a viable path from the box to a goal.
        """
        y, x = box
        queue = deque([(y, x)])
        visited = set([(y, x)])

        while queue:
            current_y, current_x = queue.popleft()
            if matrix[current_y][current_x] == '.':
                return True

            # Generate possible moves
            possible_moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dy, dx in possible_moves:
                new_y, new_x = current_y + dy, current_x + dx
                if (0 <= new_y < len(matrix) and 0 <= new_x < len(matrix[0]) and
                        (new_y, new_x) not in visited and matrix[new_y][new_x] in [' ', '.']):
                    queue.append((new_y, new_x))
                    visited.add((new_y, new_x))

        return False

    @staticmethod
    def is_corner(matrix, x, y) -> bool:
        """
        Checks if a given position (x, y) is in a corner.
        """
        if matrix[y][x] != '$':
            return False
        
        # Define corner conditions (two adjacent walls)
        if (y > 0 and matrix[y - 1][x] == '#') and (x > 0 and matrix[y][x - 1] == '#'):
            return True
        if (y > 0 and matrix[y - 1][x] == '#') and (x < len(matrix[0]) - 1 and matrix[y][x + 1] == '#'):
            return True
        if (y < len(matrix) - 1 and matrix[y + 1][x] == '#') and (x > 0 and matrix[y][x - 1] == '#'):
            return True
        if (y < len(matrix) - 1 and matrix[y + 1][x] == '#') and (x < len(matrix[0]) - 1 and matrix[y][x + 1] == '#'):
            return True

        return False

    @staticmethod
    def is_trapped_along_wall(matrix, x, y) -> bool:
        """
        Checks if a box is along a wall and trapped (cannot reach a goal).
        """
        # if matrix[y][x] != '$':
        #     return False
        
        # # Check for trapped boxes along vertical walls
        # if (x == 0 or x == len(matrix[0]) - 1) and matrix[y][x] != '.':
        #     # If a box is along the left or right wall and not on a goal
        #     if (y > 0 and matrix[y - 1][x] == '#') or (y < len(matrix) - 1 and matrix[y + 1][x] == '#'):
        #         return True

        # # Check for trapped boxes along horizontal walls
        # if (y == 0 or y == len(matrix) - 1) and matrix[y][x] != '.':
        #     # If a box is along the top or bottom wall and not on a goal
        #     if (x > 0 and matrix[y][x - 1] == '#') or (x < len(matrix[0]) - 1 and matrix[y][x + 1] == '#'):
        #         return True

        return False
