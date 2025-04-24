"""Test the ABAPClassRepository class."""

import pytest
from react_agent.src.util.abap_repository import ABAPClassRepository


def test_empty_source_code_cannot_be_indexed():
    """Test that no source code cannot be indexed"""
    # Given
    source_code = ""

    with pytest.raises(ValueError):  # Then
        ABAPClassRepository(source_code=source_code)  # When


def test_invalid_datatypes_cannot_be_indexed():
    """Test that invalid data types cannot be indexed"""
    # Given
    source_code_int = 42
    source_code_float = 42.42
    source_code_tuple = ("number", 42)

    with pytest.raises(ValueError):  # Then
        ABAPClassRepository(source_code=source_code_int)  # When

    with pytest.raises(ValueError):  # Then
        ABAPClassRepository(source_code=source_code_float)  # When

    with pytest.raises(ValueError):  # Then
        ABAPClassRepository(source_code=source_code_tuple)  # When


def test_single_class_no_methods_not_indexed():
    """Test that a single class without methods cannot be indexed"""
    # Given
    source_code = "CLASS CL_TEST_CLASS PUBLIC CRATE PUBLIC.\nENDCLASS.\nCLASS CL_TEST_CLASS IMPLEMENTATION.\nENDCLASS."

    # When
    repository = ABAPClassRepository(source_code=source_code)

    # Then
    assert len(repository.classes) == 0
    with pytest.raises(KeyError):
        repository.get_content_by_class("cl_test_class")
    with pytest.raises(KeyError):
        repository.get_content_by_class_and_method("cl_test_class", "foo")


def test_single_class_with_single_method_indexed():
    """Test that a single class with methods can be indexed"""
    # Given
    source_code = "CLASS CL_TEST_CLASS PUBLIC CRATE PUBLIC.\nMETHOD foo.\nENDCLASS.\nCLASS CL_TEST_CLASS IMPLEMENTATION.\nMETHOD foo.\nENDMETHOD.\nENDCLASS."

    # When
    repository = ABAPClassRepository(source_code=source_code)

    # Then
    assert len(repository.classes) == 1
    assert repository.get_content_by_class("cl_test_class")
    assert len(repository.list_indexed_classes()) == 1
    assert repository.get_content_by_class_and_method("cl_test_class", "foo")
    assert len(repository.classes["cl_test_class"]) == 1


def test_single_class_with_multiple_methods_indexed():
    """Test that a single class with multiple methods can be indexed"""
    # Given
    source_code = "CLASS CL_TEST_CLASS PUBLIC CRATE PUBLIC.\nMETHOD foo.\nMETHOOD bar.\nENDCLASS.\nCLASS CL_TEST_CLASS IMPLEMENTATION.\nMETHOD foo.\nENDMETHOD.\nMETHOD bar.\nENDMETHOD.\nENDCLASS."

    # When
    repository = ABAPClassRepository(source_code=source_code)

    # Then
    assert len(repository.classes) == 1
    assert repository.get_content_by_class("cl_test_class")
    assert len(repository.list_indexed_classes()) == 1
    assert repository.get_content_by_class_and_method("cl_test_class", "foo")
    assert repository.get_content_by_class_and_method("cl_test_class", "bar")
    assert len(repository.classes["cl_test_class"]) == 2


def test_indexing_only_indexes_method_implentations():
    """Test that only method implementations are indexed"""
    # Given
    source_code = "CLASS CL_TEST_CLASS PUBLIC CRATE PUBLIC.\nMETHOD foo.\nMETHOOD bar.\nENDCLASS.\nCLASS CL_TEST_CLASS IMPLEMENTATION.\nMETHOD foo.\nENDMETHOD.\nENDCLASS."

    # When
    repository = ABAPClassRepository(source_code=source_code)

    # Then
    assert len(repository.classes) == 1
    assert repository.get_content_by_class("cl_test_class")
    assert len(repository.list_indexed_classes()) == 1
    assert repository.get_content_by_class_and_method("cl_test_class", "foo")
    assert len(repository.classes["cl_test_class"]) == 1
    with pytest.raises(KeyError):
        repository.get_content_by_class_and_method("cl_test_class", "bar")
    with pytest.raises(KeyError):
        repository.get_content_by_method("bar")


def test_multiple_classes_with_same_methods_indexed():
    """Test that multiple classes with the same methods can be indexed"""
    # Given
    class_1 = "CLASS CL_TEST_CLASS PUBLIC CRATE PUBLIC.\nMETHOD foo.\nENDCLASS.\nCLASS CL_TEST_CLASS IMPLEMENTATION.\nMETHOD foo.\nENDMETHOD.\nENDCLASS."
    class_2 = "CLASS CL_TEST_CLASS_2 PUBLIC CRATE PUBLIC.\nMETHOD foo.\nENDCLASS.\nCLASS CL_TEST_CLASS_2 IMPLEMENTATION.\nMETHOD foo.\nENDMETHOD.\nENDCLASS."
    source_code = f"{class_1}\n{class_2}"

    # When
    repository = ABAPClassRepository(source_code=source_code)

    # Then
    assert len(repository.classes) == 2
    assert repository.get_content_by_class("cl_test_class")
    assert repository.get_content_by_class("cl_test_class_2")
    assert len(repository.list_indexed_classes()) == 2
    assert repository.get_content_by_class_and_method("cl_test_class", "foo")
    assert repository.get_content_by_class_and_method("cl_test_class_2", "foo")
    assert len(repository.classes["cl_test_class"]) == 1
    assert len(repository.classes["cl_test_class_2"]) == 1
    assert repository.get_content_by_method("foo")


def test_repository_string_conversion():
    """Test string creation for object works correctly"""
    # Given
    source_code = "CLASS CL_TEST_CLASS PUBLIC CRATE PUBLIC.\nMETHOD foo.\nENDCLASS.\nCLASS CL_TEST_CLASS IMPLEMENTATION.\nMETHOD foo.\nENDMETHOD.\nENDCLASS."
    repository = ABAPClassRepository(source_code=source_code)
    str_should_value = "cl_test_class:\nfoo"

    # When
    str_repository: str = str(repository)

    # Then
    assert str_repository == str_should_value
