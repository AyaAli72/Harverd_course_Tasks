import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return set(self.cells)
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if len(self.cells) == self.count:
            return set()
        elif( self.count == 0 ):
            return set(self.cells)
        else:
            return set()
        

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        self.mines.add(cell)

        # Go through all sentences in knowledge
        for sentence in self.knowledge:
            if cell in sentence.cells:
                sentence.cells.remove(cell)
                sentence.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        self.safe.add(cell)
        for sentence in self.knowledge:
            if cell in sentence.cells:
                sentence.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        def add_knowledge(self, cell, count):
            # 1. Mark the cell as a move made
            self.moves_made.add(cell)

            # 2. Mark the cell as safe
            self.mark_safe(cell)

            # 3. Find all neighbors that are not known to be safe or mines
            neighbors = set()
            i, j = cell
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if (di == 0 and dj == 0):
                        continue
                    ni, nj = i + di, j + dj
                    if 0 <= ni < self.height and 0 <= nj < self.width:
                        neighbor = (ni, nj)
                        if neighbor not in self.safes and neighbor not in self.mines:
                            neighbors.add(neighbor)

            # 4. Add new sentence
            if neighbors:
                new_sentence = Sentence(neighbors, count)
                self.knowledge.append(new_sentence)

            # 5. Mark any new cells as safe or mines
            changed = True
            while changed:
                changed = False
                safes = set()
                mines = set()
                for sentence in self.knowledge:
                    safes |= sentence.known_safes()
                    mines |= sentence.known_mines()

                for safe in safes:
                    if safe not in self.safes:
                        self.mark_safe(safe)
                        changed = True
                for mine in mines:
                    if mine not in self.mines:
                        self.mark_mine(mine)
                        changed = True

                # 6. Infer new sentences from subsets
                new_inferences = []
                for s1 in self.knowledge:
                    for s2 in self.knowledge:
                        if s1 == s2:
                            continue
                        if s1.cells.issubset(s2.cells):
                            diff_cells = s2.cells - s1.cells
                            diff_count = s2.count - s1.count
                            if diff_cells:
                                inferred = Sentence(diff_cells, diff_count)
                                if inferred not in self.knowledge and inferred not in new_inferences:
                                    new_inferences.append(inferred)
                if new_inferences:
                    self.knowledge.extend(new_inferences)
                    changed = True

    def make_safe_move(self):
        for safe in self.safes:
            if safe not in self.moves_made:
                return safe
        return None


    def make_random_move(self):
        all_moves = set((i, j) for i in range(self.height) for j in range(self.width))
        possible_moves = all_moves - self.moves_made - self.mines
        if possible_moves:
            return random.choice(list(possible_moves))
        return None