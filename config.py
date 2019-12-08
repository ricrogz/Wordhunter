#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import yaml
import logging


class Config:

    def __init__(self, cfg_file):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.WARNING)

        self.cfg_file = cfg_file
        if not os.path.isfile(self.cfg_file):
            self.logger.critical(f'Config file {cfg_file} not found.')
            quit(1)

        with open(self.cfg_file, 'rt') as f:
            self.cfg = yaml.safe_load(f.read())
        self.logger.debug(f'Read config from file {cfg_file}.')

    def __getitem__(self, item):
        return self.cfg[item]
