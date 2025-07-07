# file: spark_regex_utils.py

import re
from typing import Callable, Sequence, Any, Dict, List, Tuple

import pandas as pd
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import ArrayType, StringType

__all__ = [
    "extract_regex_paragraphs_udf",
]

def extract_regex_paragraphs_udf(
    regex_funcs: Sequence[Callable[[str], List[Tuple[int, int, str]]]],
    split_pattern: str = r'\n\s*\n'
):
    """
    Returns a pandas UDF that:
      - Splits each input string into paragraphs by `split_pattern`
      - Applies each function in `regex_funcs` to each paragraph
      - Keeps only paragraphs where any regex-finder returned a non-empty list

    Args:
        regex_funcs: list of functions f(text: str) -> List[(start, end, snippet)]
        split_pattern: regex on which to split paragraphs (default = blank lines)

    Returns:
        A pandas_udf(BooleanType) that maps a Series[str] to Series[List[str]]
    """
    @pandas_udf(ArrayType(StringType()))
    def _matched_paragraphs(texts: pd.Series) -> pd.Series:
        def extract_paras(doc: str) -> List[str]:
            if doc is None:
                return []
            # 1) split into paragraphs
            paras = re.split(split_pattern, doc)
            kept = []
            for p in paras:
                # 2) apply every finder; stop on first hit
                for fn in regex_funcs:
                    if fn(p):
                        kept.append(p.strip())
                        break
            return kept

        return texts.apply(extract_paras)

    return _matched_paragraphs
