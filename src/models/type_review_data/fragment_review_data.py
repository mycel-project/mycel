from typing import Literal
from src.models.type_review_data.base_type_review_data import BaseTypeReviewData

class FragmentReviewData(BaseTypeReviewData):
    type: Literal["fragment"] = "fragment"
    pass
