from typing import Annotated, Union

from pydantic import Field

from src.models.type_review_data.fragment_review_data import FragmentReviewData
from src.models.type_review_data.spore_review_data import SporeReviewData

TypeReviewData = Annotated[
    Union[SporeReviewData, FragmentReviewData],
    Field(discriminator="type")
]
