import re

with open("script.rpy", encoding="utf-8") as f:
    content = f.read()

# 1. Count dialog options (lines inside menu blocks that look like "Text":)
dialog_option_pattern = re.compile(r'^\s*"[^"]+":', re.MULTILINE)
dialog_options = dialog_option_pattern.findall(content)
num_dialog_options = len(dialog_options)

# 2. Count words (split on whitespace)
words = re.findall(r'\b\w+\b', content)
num_words = len(words)

# 3. Count all characters (including spaces and punctuation)
num_characters = len(content)

print(f"Dialog options: {num_dialog_options}")
print(f"Words: {num_words}")
print(f"Characters (including spaces): {num_characters}")