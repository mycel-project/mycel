import re

CLOZE_REGEX = r"\{\{c[\d,]+::(.*?)(?:::(.*?))?\}\}"
CLOZE_PATTERN = re.compile(CLOZE_REGEX, re.DOTALL)
