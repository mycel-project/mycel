from typing import TypeAlias
from src.schemas.fragment_review import FragmentReview
from src.schemas.spore_review import SporeReview


NodeReview: TypeAlias = FragmentReview | SporeReview
