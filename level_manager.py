class LevelManager:
    def __init__(self, filename, max_level):
        self.filename = filename
        self.max_level = max_level

    def load_level(self, level):
        if level < 1 or level > self.max_level:
            raise ValueError(f"Level {level} is out of range (1 - {self.max_level})")

        matrix = []
        with open(self.filename, 'r') as file:
            level_found = False
            for line in file:
                if not level_found:
                    if line.strip() == f"Level {level}":
                        level_found = True
                elif line.strip() == "" and level_found:
                    # End of the level description
                    break
                elif level_found:
                    matrix.append(line.strip())

        if not matrix:
            # Display a banner pop-up saying "You Win!" and reset to level 1
            print("You Win!")
            level = 1
            return self.load_level(level)
        
        return matrix
