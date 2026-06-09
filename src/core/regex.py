import re

HEADING_REGEX = r'^ {0,3}(#{1,6})(?:[ \x09\x0b\x0c](.*?))?(?:\s+#+\s*)?$'
HEADING_PATTERN = re.compile(HEADING_REGEX, re.MULTILINE)

CLOZE_REGEX = r"\{\{c(\d+)::(.*?)(?:::(.*?))?\}\}"
CLOZE_PATTERN = re.compile(CLOZE_REGEX, re.DOTALL)

BLOCKQUOTE_REGEX = r"^[ ]{0,3}>[ \t]?"
BLOCKQUOTE_PATTERN = re.compile(BLOCKQUOTE_REGEX, re.DOTALL)
