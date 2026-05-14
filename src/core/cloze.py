import re

CLOZE_REGEX = r"(?s)\{\{c[\d,]+::(.*?)(?:::(.*?))?\}\}"
CLOZE_PATTERN = re.compile(CLOZE_REGEX)
