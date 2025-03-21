#
# The purpose of this python file is to read some text as an input and format it using
# environment variables. This is useful in particular to rewrite the nginx configuration at runtime.
#

import os
import string


lines = []
try:
    while True:
        lines.append(input())
except EOFError:
    pass

input_text = '\n'.join(lines)

def count_suffix (text: str, chr: str):
    for i in range(len(text) - 1, - 1, - 1):
        if text[i] != chr:
            return len(text) - 1 - i

    return len(text)
def find_all (text: str, chr: str, eschr: str):
    res = []
    for i in range(len(text)):
        if text[i] == chr and (count_suffix(text[:i], eschr) % 2) == 0:
            res.append(i)
    return res

holders = find_all(input_text, "%", "\\")

holder_chars = string.ascii_letters + string.digits + "_"

def find_envname (text: str, location: int) -> "str | None":
    offset = location + 1
    while offset < len(text) and text[offset] in holder_chars:
        offset = offset + 1
    
    envname = text[location + 1:offset]
    if len(envname) == 0:
        return None

    return envname

new_holders = []
for holder in holders:
    name = find_envname( input_text, holder )
    if name is None:
        continue
    new_holders.append((holder, name))

new_holders.sort()
holders = new_holders

start = 0
texts = []

for location, envname in holders:
    print(location, envname)
    texts.append( input_text[start:location] )
    texts.append( os.environ.get( envname, "" ) )
    start = location + 1 + len(envname)

texts.append( input_text[start:] )
print(texts)
output_text = "".join(texts)

print(output_text, end="")
