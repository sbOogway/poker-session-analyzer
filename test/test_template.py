from jinja2 import Environment, FileSystemLoader

import random
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
# Set up the environment to look for templates in the "templates" folder
from config import HANDS
env = Environment(loader=FileSystemLoader("templates"))

# Load the specific template file
template = env.get_template("range.html")

hands_list = []

for hand in HANDS:
    fold_n = random.randrange(0, 5)
    call_n = random.randrange(0, 5)
    raise_n = random.randrange(0, 5)
    total = fold_n + call_n + raise_n

    hands_list.append(
        {
            "name": hand,
            "fold": fold_n,
            "call": call_n,
            "raise": raise_n,
            "fold_frequency": 0 if not total else round(fold_n / total * 100, 2),
            "call_frequency":  0 if not total else round(call_n / total * 100, 2),
            "raise_frequency": 0 if not total else round(raise_n / total * 100, 2) ,
            "not_dealt_frequency": 0 if total else 100,
            "total": total,
        },
    )

# Render the final HTML
output = template.render({"hands": hands_list})

# Write to a file or send as a response
with open("templates/output.html", "w") as f:
    f.write(output)
