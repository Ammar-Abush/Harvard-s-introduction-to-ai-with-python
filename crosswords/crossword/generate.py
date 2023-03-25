import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }
    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            d = self.domains[var].copy()
            for word in d:
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        
        """
        revised = False
        if self.crossword.overlaps[x,y] == None:
            return False
        d = self.domains[x].copy()
        for w in d:
            num = 0
            for word in self.domains[y]:
                
                if w[self.crossword.overlaps[x,y][0]] != word[self.crossword.overlaps[x,y][1]]:
                    num+=1
            if num == len(self.domains[y]):
                self.domains[x].remove(w)
                revised = True
        return revised
    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        l = arcs
        if l == None:
            l = list()
            for var in self.crossword.variables:
                for v in self.crossword.variables:
                    if var != v:
                        l.append((var,v))
        while len(l) != 0:
            (x,y) = l.pop(0)
            if self.revise(x,y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x):
                    if z not in self.crossword.neighbors(y):
                        l.append((z,x))
        return True
    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if(assignment == dict()):
            return False
        for x in self.domains:
            if(len(self.domains) != len(assignment)):
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for x in assignment:
        
            if(len(assignment[x]) != x.length):
                return False
            
            for v in assignment:
                
                if v != x:
                    if self.crossword.overlaps[x,v] != None:
                        if assignment[x][self.crossword.overlaps[x,v][0]] != assignment[v][self.crossword.overlaps[x,v][1]]:
                            return False
                    
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        mp = dict()
        for word in self.domains[var]:
            n = 0
            for v in self.crossword.neighbors(var):
                if v not in assignment:
                    if self.crossword.overlaps[var,v] != None:
                        for w in self.domains[v]:
                            if word[self.crossword.overlaps[var,v][0]] != w[self.crossword.overlaps[var,v][1]]:
                                n+=1
            mp[word] = n
        l = dict(sorted(mp.items(), key = lambda x:x[1]))
        result = list(l)
        return result
        

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        mp = dict()
        mb = dict()
        for var in self.crossword.variables:
            if var not in assignment:
                mp[var] = len(self.domains[var])
                mb[var] = len(self.crossword.neighbors(var))
        l = dict(sorted(mp.items(), key = lambda x:x[1]))
        m = dict(sorted(mp.items(),key = lambda x:x[1], reverse=True))
        least_remaining = l[list(l.keys())[0]]
        for v in m:
            if l[v] == least_remaining:
                return v
        
       
    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        
        if self.assignment_complete(assignment):
            return assignment
        x = self.select_unassigned_variable(assignment)
        for val in self.order_domain_values(x,assignment):
            new = assignment.copy()
            new[x] = val
            
            if self.consistent(new):
                result = self.backtrack(new)
                if result != None:
                    return result
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
