import random
import re

from rich import print as rprint

# Open file with words
BAG_OF_WORDS = [w for w in open("words.txt").read().split() if len(w) == 5]

# Open file with letter frequency
LETTERS_FREQ = {
    z.split(",")[0]: float(z.split(",")[1]) for z in open("letters.txt").read().split()
}

# Colors for rich print
YELLOW = "[yellow][bold]{}[/bold][/yellow]"
GREEN = "[green][bold]{}[/bold][/green]"
GRAY = "[gray][bold]{}[/bold][/gray]"

# Calculate the score of a word using the letter frequency
def score_word(word):
    return round(sum([LETTERS_FREQ[l] for l in set(word)]), 2)


class Wordle:
    """
    This class simulates the Wordle game. There are two modes, one you can 
    input the word in the start of the game and the other the word is randomly
    generated. It's not possible (yet!) to interact with the online Wordle game.
    """
    def __init__(self, word=None):
        if word:
            self.word = word
        else:
            self.word = random.choice(BAG_OF_WORDS)
        self.tries = 6

    """
    Prints the word using green to represent if the letter is in the correct spot,
    yellow if it's in the word but in the wrong spot and gray if it's a letter that's
    not part of the word.
    """
    def print_check(self, word, results):
        fw = ""
        for i, x in enumerate(results):
            if x == "v":
                fw += GREEN.format(word[i].upper())
            elif x == "a":
                fw += YELLOW.format(word[i].upper())
            else:
                fw += GRAY.format(word[i].upper())
        rprint(fw)

    """
    Checks if guess is in the word and prints results.
    """
    def check(self, word):
        r = ". . . . .".split()
        for i, l in enumerate(word):
            if self.word[i] == l:
                r[i] = "v"
            elif l in self.word and self.word[i] != l:
                r[i] = "a"
            else:
                r[i] = "p"
        self.print_check(word, r)
        return r

    def play(self):
        c = 0
        while c != self.tries:
            inp = input("Você já tentou {} vezes, manda uma palavra: ".format(c))
            if len(inp) != 5:
                rprint("5 letras, por favor!")
                continue
            if self.check(inp):
                rprint("You win!")
                exit()
            c += 1
        rprint("You lose!")


class WordleSolver:
    """
    Automatic Wordle solver.
    """
    def __init__(self):
        self.bag = self._create_bag()
        self.gray_letters = [] # List of letters that aren't in the word
        self.yellow_letters = [] # List of regex including letters that are in the word, but wrong position
        self.green_letters = [".", ".", ".", ".", "."] # Initial regex with letter that are in a certain position

    """
    Given a bag of words, it sorts them by their score and returns a list of words.
    """
    def _create_bag(self) -> list:
        bag = BAG_OF_WORDS.copy()
        scored = list(map(score_word, bag))
        new_l = sorted(
            [(x, y) for x, y in zip(bag, scored)], key=lambda x: x[1], reverse=True
        )
        return new_l

    """
    Drops words from bag and reatribuites it to the atribute bag. 
    """
    def _reroll_bag(self, p=False):
        bag = self.bag.copy()
        bag = list(filter(self.drop_word_green, bag))
        bag = list(filter(self.drop_word_gray, bag))
        bag = list(filter(self.drop_word_yellow, bag))
        self.bag = bag
        
        # Print result
        if p:
            rprint(self.bag)

    """
    Add letters that aren't in the word to the gray_letters list
    """
    def add_gray(self, l):
        self.gray_letters.append(l)

    """
    Creates regexes of letters that are in the wrong position. 
    """
    def add_yellow(self, l, p):
        r = [".", ".", ".", ".", "."]
        r[p] = l
        self.yellow_letters.append("".join(r))
        print(self.yellow_letters)

    """
    Adds letter to regex
    """
    def add_green(self, l, p):
        self.green_letters[p] = l

    """
    After guess, compares it to result and adds gray, yellow and green letter to their
    respective list
    """
    def parse_result(self, word, result):
        for i, r in enumerate(result):
            if r == "v":
                self.add_green(word[i], i)
            elif r == "a":
                self.add_yellow(word[i], i)
            else:
                self.add_gray(word[i])

        self._reroll_bag()
        # rprint(self.yellow_letters)
        if result.count("v") == 5:
            return True

    """
    Remove words if it contains any of the gray_letters
    """
    def drop_word_gray(self, w):
        return None if any([l for l in w[0] if l in self.gray_letters]) else w[0]

    """
    Remove words if they contain letter in the yellow position or if the word doesn't
    contain that letter.
    """
    def drop_word_yellow(self, word):
        all_yellow_letters = "".join(self.yellow_letters).replace(".", " ")

        for letter in all_yellow_letters:
            if letter in word:
                return None
                
        if any([re.search(r"{}".format(l), word[0]) for l in self.yellow_letters]):
            return None
        else:
            word[0]
        

    """
    Removes word if it doesn't have green letters. 
    """
    def drop_word_green(self, w):
        return w if re.search(r"{}".format("".join(self.green_letters)), w[0]) else None

    """
    Gets first letter in bag list, which is the word with the highest score. 
    """
    def get_word(self):
        return self.bag[0][0]


class WorldeInterface:
    """
    Interaction between Wordle class and WordleSolver class. Wordle game can be initialized
    given the word as parameter.
    """
    def __init__(self, word=None) -> None:
        self.game = Wordle(word)
        self.solver = WordleSolver()

    """
    Simulates each step where a word is guessed and afterwards it's shown whether those
    letters are part of the correct answer.
    """
    def step(self):
        c = 0
        while c != self.game.tries:
            word = self.solver.get_word()
            res = self.game.check(word)
            if self.solver.parse_result(word, res):
                print("Ganhou!")
                exit()
            c += 1
        
        print(f"Perdeu!\nA palavra era {word}")


if __name__ == "__main__":

    w = WorldeInterface() 
    w.step()
