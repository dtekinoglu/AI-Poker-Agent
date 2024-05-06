from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from tree_player import TreePlayer
from stump_player import StumpPlayer
from evil_player import EvilPlayer
from smart_player import SmartPlayer

#TODO:config the config as our wish
config = setup_config(max_round=1000, initial_stack=10000, small_blind_amount=10)

config.register_player(name="raise", algorithm=RaisedPlayer())
config.register_player(name="tree", algorithm=TreePlayer())

game_result = start_poker(config, verbose=0)
