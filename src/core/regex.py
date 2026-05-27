import re

HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.*)', re.MULTILINE)

CLOZE_REGEX = r"\{\{c[\d,]+::(.*?)(?:::(.*?))?\}\}"
CLOZE_PATTERN = re.compile(CLOZE_REGEX, re.DOTALL)
