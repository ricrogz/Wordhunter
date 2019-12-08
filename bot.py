#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import importlib.util
import glob
import logging

import cfg
import chatter
from game import WHGame
from jaraco.stream import buffer
from irc.bot import SingleServerIRCBot


class WHBot(SingleServerIRCBot, WHGame):

    valid_params = {"n": "num_rounds", "t": "round_time"}
    default_params = {"n": cfg.NUM_ROUNDS, "t": cfg.ROUND_TIME}
    min_values = {"n": 0, "t": 5}

    def __init__(self, channel, key, nickname, server, port=6667):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)

        # allow for latin-1 encoding
        self.connection.buffer_class = buffer.LenientDecodingLineBuffer

        WHGame.__init__(self)
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG)
        self.logger.info("Initializing")
        self.rounds = 0
        self.channel = channel
        self.key = key

        # Assets
        self.words = None
        self.scores = None
        self.definitions = None
        self.scored_words = None
        self.load_assets()

        # Plugins
        self.load_plugins("round")
        self.load_plugins("modifier")
        self.logger.info("Initialization complete")

    def load_plugins(self, plugin_type):
        category = f'{plugin_type}s'
        exclusions = getattr(cfg, f'EXCLUDE_{category.upper()}')
        generator_func = f'{plugin_type.title()}Generator'

        setattr(self, category, {})
        plugin_files = glob.glob(os.path.join(category, "*.py"))
        for f in plugin_files:
            name = os.path.basename(f)[:-3]

            if name in exclusions:
                self.logger.debug(
                    f'Plugin {plugin_type} \'{name}\' is excluded.')
                continue

            try:
                spec = importlib.util.spec_from_file_location(name, f)
                mdl = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mdl)
                getattr(self, category)[name] = getattr(mdl, generator_func)()
            except Exception as e:
                self.logger.error(
                    f'Error loading {plugin_type} \'{name}\': {e}')
            else:
                self.logger.info(f'Loaded {plugin_type} \'{name}\'.')

    def load_assets(self):
        self.logger.info("Loading assets...")
        with open(os.path.join('data', 'CSW12mw-wh.txt'), 'r') as f:
            self.logger.info("	...word list")
            self.words = list(map(lambda x: x.strip(), f.readlines()))
        with open(os.path.join('data', 'CSW12mw-wh-scores.txt'), 'r') as f:
            self.logger.info("	...scores")
            self.scores = list(map(lambda x: int(x.strip()), f.readlines()))
        with open(os.path.join('data', 'CSW12-defs.txt'), 'r') as f:
            self.logger.info("	...definitions")
            self.definitions = dict(
                map(lambda x: x.strip().split("\t", 1), f.readlines()))
        self.scored_words = dict(zip(self.words, self.scores))

    def on_nicknameinuse(self, c, _):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, _):
        c.join(self.channel, self.key)

    def handle_command(self, command, nick, params):
        if command == cfg.START_COMMAND:
            if not self.playing:
                params = map(lambda s: s.split("=", 1), params)
                for p in params:
                    if p[0] in WHBot.valid_params:
                        try:
                            value = int(p[1])
                            assert (value >= WHBot.min_values[p[0]])
                        except Exception:
                            value = WHBot.default_params[p[0]]
                        finally:
                            setattr(self, WHBot.valid_params[p[0]], value)
                self.set_reset_time()
                self.start_game()
            else:
                self.output(chatter.STR_PLAYING.format(nick))
        elif command == cfg.REPEAT_COMMAND and self.playing:
            self.announce_puzzle(reannounce=True)
        elif command == cfg.STOP_COMMAND:
            if self.playing:
                self.stop_game(nick)
            else:
                self.output(chatter.STR_NOT_PLAYING.format(nick))

    def on_pubmsg(self, c, e):
        nick = e.source.nick
        text = e.arguments[0]
        splittext = text.split(' ')
        if text[0:len(cfg.COMMAND_PREFIX)] == cfg.COMMAND_PREFIX:
            command = splittext[0][len(cfg.COMMAND_PREFIX):]
            self.handle_command(command, nick, splittext[1:])
        elif self.playing and self.guessing:
            word = splittext[0]
            self.submit_word(word, nick)
        return

    def output(self, text):
        self.connection.privmsg(self.channel, text)


def main():
    bot = WHBot(cfg.CHANNEL, cfg.KEY, cfg.NICK, cfg.SERVER, cfg.PORT)
    bot.start()


if __name__ == "__main__":
    main()
