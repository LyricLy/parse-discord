import sys
import requests
import re
from pathlib import Path

version = sys.argv[1]

r = requests.get(f"https://raw.githubusercontent.com/mathiasbynens/emoji-test-regex-pattern/main/dist/emoji-{version}/javascript-u.txt").text

with open(Path(__file__).parent / "../parse_discord/emoji.txt", "w") as f:
    f.write(re.sub(r"\\u\{(.{5})\}", r"\\U000\1", r))
