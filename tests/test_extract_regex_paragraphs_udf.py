import pytest
import pandas as pd
import re
from typing import Callable, List, Tuple
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, ArrayType
from pyregularexpression.extract_regex_paragraphs_udf import extract_regex_paragraphs_udf

# Helper function to create finders
def create_finder(pattern: str, flags: int = 0) -> Callable[[str], List[Tuple[int, int, str]]]:
    """
    Creates a function that finds all non-overlapping matches of a regex pattern in a string.
    """
    def find_all(text: str) -> List[Tuple[int, int, str]]:
        return [(m.start(), m.end(), m.group(0)) for m in re.finditer(pattern, text, flags)]
    return find_all

# A simple finder for the word 'test'
find_test = create_finder(r'test')

# Another simple finder for the word 'word'
find_word = create_finder(r'word')

@pytest.fixture(scope="session")
def spark_session():
    return SparkSession.builder.master("local[1]").appName("testing").getOrCreate()

def test_extract_regex_paragraphs_udf_single_match(spark_session):
    # Test case with a single matching paragraph
    data = [("This is the first paragraph.\n\nThis is a test.",)]
    schema = StructType([StructField("text", StringType(), True)])
    df = spark_session.createDataFrame(data, schema=schema)

    udf = extract_regex_paragraphs_udf([find_test])
    result_df = df.withColumn("matched_paragraphs", udf(df["text"]))

    result = result_df.collect()[0]["matched_paragraphs"]
    assert result == ["This is a test."]

def test_extract_regex_paragraphs_udf_no_match(spark_session):
    # Test case with no matching paragraphs
    data = [("This is the first paragraph.\n\nThis is the second paragraph.",)]
    schema = StructType([StructField("text", StringType(), True)])
    df = spark_session.createDataFrame(data, schema=schema)

    udf = extract_regex_paragraphs_udf([find_test])
    result_df = df.withColumn("matched_paragraphs", udf(df["text"]))

    result = result_df.collect()[0]["matched_paragraphs"]
    assert result == []

def test_extract_regex_paragraphs_udf_multiple_matches(spark_session):
    # Test case with multiple matching paragraphs
    data = [("This is a test.\n\nThis is another test.",)]
    schema = StructType([StructField("text", StringType(), True)])
    df = spark_session.createDataFrame(data, schema=schema)

    udf = extract_regex_paragraphs_udf([find_test])
    result_df = df.withColumn("matched_paragraphs", udf(df["text"]))

    result = result_df.collect()[0]["matched_paragraphs"]
    assert result == ["This is a test.", "This is another test."]

def test_extract_regex_paragraphs_udf_empty_input(spark_session):
    # Test case with empty input
    data = [("",)]
    schema = StructType([StructField("text", StringType(), True)])
    df = spark_session.createDataFrame(data, schema=schema)

    udf = extract_regex_paragraphs_udf([find_test])
    result_df = df.withColumn("matched_paragraphs", udf(df["text"]))

    result = result_df.collect()[0]["matched_paragraphs"]
    assert result == []

def test_extract_regex_paragraphs_udf_none_input(spark_session):
    # Test case with None input
    data = [(None,)]
    schema = StructType([StructField("text", StringType(), True)])
    df = spark_session.createDataFrame(data, schema=schema)

    udf = extract_regex_paragraphs_udf([find_test])
    result_df = df.withColumn("matched_paragraphs", udf(df["text"]))

    result = result_df.collect()[0]["matched_paragraphs"]
    assert result == []

def test_extract_regex_paragraphs_udf_custom_split(spark_session):
    # Test case with a custom split pattern
    data = [("This is a test.--This is another paragraph.",)]
    schema = StructType([StructField("text", StringType(), True)])
    df = spark_session.createDataFrame(data, schema=schema)

    udf = extract_regex_paragraphs_udf([find_test], split_pattern=r'--')
    result_df = df.withColumn("matched_paragraphs", udf(df["text"]))

    result = result_df.collect()[0]["matched_paragraphs"]
    assert result == ["This is a test."]

def test_extract_regex_paragraphs_udf_multiple_finders(spark_session):
    # Test case with multiple regex finders
    data = [("This is a test.\n\nThis is a word.",)]
    schema = StructType([StructField("text", StringType(), True)])
    df = spark_session.createDataFrame(data, schema=schema)

    udf = extract_regex_paragraphs_udf([find_test, find_word])
    result_df = df.withColumn("matched_paragraphs", udf(df["text"]))

    result = result_df.collect()[0]["matched_paragraphs"]
    assert result == ["This is a test.", "This is a word."]

def test_extract_regex_paragraphs_udf_no_match_multiple_finders(spark_session):
    # Test case with multiple regex finders but no match
    data = [("This is a sentence.\n\nThis is another sentence.",)]
    schema = StructType([StructField("text", StringType(), True)])
    df = spark_session.createDataFrame(data, schema=schema)

    udf = extract_regex_paragraphs_udf([find_test, find_word])
    result_df = df.withColumn("matched_paragraphs", udf(df["text"]))

    result = result_df.collect()[0]["matched_paragraphs"]
    assert result == []
