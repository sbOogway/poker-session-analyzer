


import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from  utils import categorize_hand

print(categorize_hand("Ac 2h"))