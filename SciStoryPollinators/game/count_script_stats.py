import re

with open("script.rpy", encoding="utf-8") as f:
    content = f.readlines()

dialog_lines = []
dialog_option_lines = []

# Pattern for spoken dialog: starts with optional whitespace, then optional character name, then quoted text
dialog_pattern = re.compile(r'^\s*(\w+\s*)?"([^"]+)"')
# Pattern for menu options: quoted text followed by colon
menu_option_pattern = re.compile(r'^\s*"[^"]+":')

for line in content:
    if menu_option_pattern.match(line):
        dialog_option_lines.append(line)
    elif dialog_pattern.match(line):
        dialog_lines.append(line)

# Count dialog options
num_dialog_options = len(dialog_option_lines)

# Join all spoken dialog lines for word/character count
all_dialog_text = " ".join([dialog_pattern.match(line).group(2) for line in dialog_lines])

# Count words and characters in spoken dialog
num_words = len(re.findall(r'\b\w+\b', all_dialog_text))
num_characters = len(all_dialog_text)

print(f"Dialog options: {num_dialog_options}")
print(f"Words in spoken dialog: {num_words}")
print(f"Characters in spoken dialog (including spaces): {num_characters}")