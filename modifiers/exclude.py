﻿# -*- coding: utf-8 -*-

import re
import random

from constants import ALPHABET
from formatting import embolden, listtostr


STR_ANNOUNCE_MOD = "Your word must " + embolden("exclude") + " {}!"


class ModifierGenerator(object):

    def __init__(self):
        pass

    def generate(self, word, round_name, involved_letters, difficulty):
        num_letters = random.randint(1, 4)
        if round_name in ["blockbeginend", "blockend", "blockmiddle", "blockstart", "ordered"]:
            possible_letters = ALPHABET - set(word)
        elif round_name in ["boggle"]:
            possible_letters = involved_letters - set("@")
        else:
            possible_letters = None
        if not possible_letters:
            regex = None
            s = ""
        else:
            # This picking ought to be done probabilistically according to letter frequency, but until
            # tools.discrete_sample is rewritten this will have to do.
            letters = random.sample(possible_letters, num_letters)
            regex = re.compile("^[^" + "".join(letters) + "]*$")
            s = STR_ANNOUNCE_MOD.format(listtostr(map(embolden, sorted(letters)), conj="and"))
        return regex, s
