from typing import Union

from src.models.type_review_data.fragment_review_data import FragmentReviewData
from src.models.type_review_data.spore_review_data import SporeReviewData

TypeReviewData = Union[SporeReviewData, FragmentReviewData]

