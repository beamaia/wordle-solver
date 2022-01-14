import random
import re

from rich import print as rprint

FIRST_WORD = "ORATE"
BAG_OF_WORDS = open("words.txt").read().split()
LETTERS_FREQ = {
    z.split(",")[0]: float(z.split(",")[1]) for z in open("letters.txt").read().split()
}
YELLOW = "[yellow]{}[/yellow]"
GREEN = "[green]{}[/green]"
GRAY = "[gray]{}[/gray]"


def score_word(w):
    return round(sum([LETTERS_FREQ[l] for l in set(w)]), 2)


class Wordle:
    def __init__(self):
        self.word = random.choice(BAG_OF_WORDS)
        self.tries = 6

    def print_check(self, word, results):
        fw = ""
        for i, x in enumerate(results):
            if x == "v":
                fw += GREEN.format(word[i])
            elif x == "a":
                fw += YELLOW.format(word[i])
            else:
                fw += GRAY.format(word[i])
        rprint(fw)

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
    def __init__(self):
        self.bag = self._create_bag()
        self.gray_letters = []
        self.yellow_letters = []
        self.green_letters = [".", ".", ".", ".", "."]

    def _create_bag(self) -> list:
        bag = BAG_OF_WORDS.copy()
        scored = list(map(score_word, bag))
        new_l = sorted(
            [(x, y) for x, y in zip(bag, scored)], key=lambda x: x[1], reverse=True
        )
        return new_l

    def _reroll_bag(self, p=False):
        bag = self.bag.copy()
        bag = list(filter(self.drop_word_green, bag))
        bag = list(filter(self.drop_word_gray, bag))
        bag = list(filter(self.drop_word_yellow, bag))
        self.bag = bag
        if p:
            rprint(self.bag)

    def add_gray(self, l):
        self.gray_letters.append(l)

    def add_yellow(self, l, p):
        r = [".", ".", ".", ".", "."]
        r[p] = l
        self.yellow_letters.append("".join(r))

    def add_green(self, l, p):
        self.green_letters[p] = l

    def parse_result(self, word, result):
        for i, r in enumerate(result):
            if r == "v":
                self.add_green(word[i], i)
            elif r == "a":
                self.add_yellow(word[i], i)
            else:
                self.add_gray(word[i])

        self._reroll_bag()
        if result.count("v") == 5:
            return True

    def drop_word_gray(self, w):
        return None if any([l for l in w[0] if l in self.gray_letters]) else w[0]

    def drop_word_yellow(self, w):
        return (
            None
            if any([re.search(r"{}".format(l), w[0]) for l in self.yellow_letters])
            else w[0]
        )

    def drop_word_green(self, w):
        return w if re.search(r"{}".format("".join(self.green_letters)), w[0]) else None

    def get_word(self):
        return self.bag[0][0]


class WorldeInterface:
    def __init__(self) -> None:
        self.game = Wordle()
        self.solver = WordleSolver()

    def step(self):
        c = 0
        while c != self.game.tries:
            word = self.solver.get_word()
            res = self.game.check(word)
            if self.solver.parse_result(word, res):
                print("ganhamo pora")
                exit()
            c += 1


if __name__ == "__main__":
    w = WorldeInterface()
    w.step()
