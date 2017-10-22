# -*- coding: utf-8 -*-

import re
import random
from formatting import embolden


STR_ANNOUNCE = "Find a word that starts with {}!"


class RoundGenerator():

    def __init__(self):
        pass

    def generate(self, word, words, difficulty):
        block_length = min(len(word), random.randint(3, 5))
        pos = 0
        block = word[pos:pos + block_length]
        regex = re.compile("^" + block + ".*$")
        s = STR_ANNOUNCE.format(embolden(block))
        involved_letters = block
        return regex.match, s, involved_letters
