import operator

import pytest

from deepset import (
    ComparisonResult,
    DeepSet,
    _get_comparison_strength,
    deepset,
    zip_compare,
)


class TestDeepSetSets:
    def test_set_subset_comparison(self):
        """Test that sets compare based on element-wise matching"""
        # Example from the original request
        assert deepset({("a", frozenset({2}))}) <= deepset(
            {("a", frozenset({2, 3})), ("a", frozenset({1}))}
        )
        assert deepset({("a", frozenset({1}))}) <= deepset(
            {("a", frozenset({2, 3})), ("a", frozenset({1}))}
        )

        # Contrasting with regular Python behavior
        assert not (
            {("a", frozenset({2}))} <= {("a", frozenset({2, 3})), ("a", frozenset({1}))}
        )
        assert {("a", frozenset({1}))} <= {
            ("a", frozenset({2, 3})),
            ("a", frozenset({1})),
        }

    def test_simple_set_comparison(self):
        """Test basic set comparisons"""
        assert deepset({1, 2}) <= deepset({1, 2, 3})
        assert deepset({1}) <= deepset({1, 2})
        assert not deepset({1, 4}) <= deepset({1, 2, 3})
        assert deepset(set()) <= deepset({1, 2})

    def test_frozenset_comparison(self):
        """Test frozenset comparisons"""
        assert deepset(frozenset({1, 2})) <= deepset(frozenset({1, 2, 3}))
        assert not deepset(frozenset({1, 4})) <= deepset(frozenset({1, 2, 3}))


class TestDeepSetLists:
    def test_list_pairwise_comparison(self):
        """Test that lists compare element by element"""
        assert deepset([1, 2]) <= deepset([0, 1, "a", 2, 3])
        assert deepset([1, 2]) <= deepset([1, 2, 2])
        assert not deepset([1, 2]) <= deepset([1])
        assert not deepset([1, 3]) <= deepset([1, 2])

    def test_nested_list_comparison(self):
        """Test nested list structures"""
        assert deepset([[1, 2], [3]]) <= deepset([[0, 1, 2], [3, 4]])
        assert not deepset([[1, 3], [3]]) <= deepset([[0, 1, 2], [3, 4]])

    def test_tuple_comparison(self):
        """Test tuple comparisons"""
        assert deepset((1, 2)) <= deepset((99, 1, 3, 2))
        assert deepset((1, 2)) <= deepset((1, 2))
        assert not deepset((1, 2)) <= deepset((1, 3))


class TestDeepSetDicts:
    def test_dict_key_value_comparison(self):
        """Test dictionary comparisons"""
        assert deepset({"a": 1, "b": [2]}) <= deepset({"a": 1, "b": [1, 2, 3]})
        assert deepset({"a": 1}) <= deepset({"a": 1})
        assert deepset({"a": 1}) <= deepset({"a": 1, "b": 2})
        assert not deepset({"a": 1, "c": 1}) <= deepset({"a": 1, "b": 2})

    def test_nested_dict_comparison(self):
        """Test nested dictionary structures"""
        d1 = {"outer": {"inner": {1}}}
        d2 = {"outer": {"inner": {1, 2}}}
        assert deepset(d1) <= deepset(d2)


class TestDeepSetMixed:
    def test_mixed_nested_structures(self):
        """Test complex nested structures mixing different types"""
        data1 = {"sets": {frozenset({1, 2}), frozenset({3})}, "lists": [[1, 2], (3, 4)]}
        data2 = {
            "sets": {frozenset({1, 2, 3}), frozenset({3, 4})},
            "lists": [[1, 2, 3], (2, 3, 4, 5)],
        }
        assert deepset(data1) <= deepset(data2)

    def test_tuple_with_nested_sets(self):
        """Test the original example pattern"""
        t1 = ("a", frozenset({2}))
        t2 = ("a", frozenset({2, 3}))
        assert deepset(t1) <= deepset(t2)


class TestDeepSetOperators:
    def test_equality_operator(self):
        """Test __eq__ operator"""
        assert deepset({1, 2}) == deepset({1, 2})
        assert not deepset({1, 2}) == deepset({1, 2, 3})

    def test_less_than_operator(self):
        """Test __lt__ operator"""
        assert deepset({1, 2}) < deepset({1, 2, 3})
        assert not deepset({1, 2}) < deepset({1, 2})

    def test_strict_subset_semantics(self):
        """Test that < requires at least one strict inequality somewhere in the structure"""
        # Sets: strict subset
        assert deepset({1, 2}) < deepset({1, 2, 3})
        assert not deepset({1, 2}) < deepset({1, 2})

        # Nested sets: strict inequality in nested structure
        assert deepset({frozenset({1, 2})}) < deepset({frozenset({1, 2, 3})})
        assert not deepset({frozenset({1, 2})}) < deepset({frozenset({1, 2})})

        # Dictionaries: extra key makes it strict
        assert deepset({"a": 1}) < deepset({"a": 1, "b": 2})
        assert not deepset({"a": 1}) < deepset({"a": 1})

        # Dictionaries: strict inequality in value
        assert deepset({"a": {1, 2}}) < deepset({"a": {1, 2, 3}})
        assert not deepset({"a": {1, 2}}) < deepset({"a": {1, 2}})

        # Lists: extra elements make it strict
        assert deepset([1, 2]) < deepset([1, 2, 3])
        assert not deepset([1, 2]) < deepset([1, 2])

        # Mixed nested: strict inequality can come from anywhere
        data1 = {"sets": {frozenset({1, 2})}, "lists": [[1, 2]]}
        data2 = {
            "sets": {frozenset({1, 2, 3})},
            "lists": [[1, 2]],
        }  # strict in nested set
        assert deepset(data1) < deepset(data2)

        data3 = {"sets": {frozenset({1, 2})}, "lists": [[1, 2]]}
        data4 = {
            "sets": {frozenset({1, 2})},
            "lists": [[1, 2, 3]],
        }  # strict in nested list
        assert deepset(data3) < deepset(data4)

    def test_greater_than_operators(self):
        """Test __gt__ and __ge__ operators"""
        assert deepset({1, 2, 3}) > deepset({1, 2})
        assert deepset({1, 2, 3}) >= deepset({1, 2})
        assert deepset({1, 2}) >= deepset({1, 2})

    def test_auto_wrapping(self):
        """Test that non-DeepSet objects are automatically wrapped"""
        assert deepset({1, 2}) <= {1, 2, 3}
        assert {1, 2} >= deepset({1})


class TestDeepSetEdgeCases:
    def test_empty_collections(self):
        """Test empty collections"""
        assert deepset(set()) <= deepset({1, 2})
        assert deepset([]) <= deepset([1, 2])
        assert deepset({}) <= deepset({"a": 1})

    def test_non_comparable_types(self):
        """Test with types that don't support comparison"""
        # Should fall back to equality check
        obj1 = object()
        obj2 = object()
        assert deepset([obj1]) == deepset([obj1])
        assert not deepset([obj1]) == deepset([obj2])

    def test_mixed_collection_types_fail(self):
        """Test that comparing different collection types returns False"""
        assert not deepset([1, 2]) <= deepset({1, 2})
        assert not deepset({"a": 1}) <= deepset([1, 2])

    def test_string_comparison(self):
        """Test string comparisons work as expected; literal types only checked for equality"""
        assert not deepset("abc") <= deepset("abcd")
        assert deepset(["a", "b"]) < deepset(["a", "b", "c", "d"])


class TestDeepSetInitialization:
    def test_comparator_function(self):
        """Test the deepset() convenience function"""
        c = deepset([1, 2, 3])
        assert isinstance(c, DeepSet)
        assert c.data == [1, 2, 3]

    def test_direct_instantiation(self):
        """Test direct DeepSet class instantiation"""
        c = DeepSet([1, 2, 3])
        assert isinstance(c, DeepSet)
        assert c.data == [1, 2, 3]


class TestZipCompare:
    def test_ordered_subset_le(self):
        """Test ordered subset relationship - all items from first must appear in second in order"""
        # First list items all appear in second list in correct order with intervening items
        a = ["x", "z"]
        b = ["w", "x", "y", "z", "a"]

        results = list(
            zip_compare(a, b, op=operator.le)
        )  # Using le for subset semantics
        expected = [((0, "x"), (1, "x")), ((1, "z"), (3, "z"))]
        assert results == expected

    def test_nested_structure_le(self):
        """Test with nested structures using recursive_compare semantics"""
        # Sets can have subset relationships
        a = [frozenset({1, 2}), frozenset({4})]
        b = [frozenset({1, 2, 3}), frozenset({3, 5}), frozenset({4, 6})]

        results = list(zip_compare(a, b, op=operator.le))
        expected = [
            ((0, frozenset({1, 2})), (0, frozenset({1, 2, 3}))),
            ((1, frozenset({4})), (2, frozenset({4, 6}))),
        ]
        assert results == expected

    def test_equality_exact_match(self):
        """Test equality requires exact correspondence"""
        a = [1, 2, 3]
        b = [1, 2, 3]

        results = list(zip_compare(a, b, op=operator.eq))
        expected = [((0, 1), (0, 1)), ((1, 2), (1, 2)), ((2, 3), (2, 3))]
        assert results == expected

    def test_skip_intervening_items(self):
        """Test that second iterator can have intervening items that don't match"""
        a = [2, 5]
        b = [1, 2, 3, 4, 5, 6]  # 2 and 5 present but with intervening items

        results = list(zip_compare(a, b, op=operator.le))
        expected = [((0, 2), (1, 2)), ((1, 5), (4, 5))]
        assert results == expected

    def test_first_shorter_than_second(self):
        """Test successful completion when first iterator exhausts before second"""
        a = [1, 3]
        b = [1, 2, 3, 4, 5]

        results = list(zip_compare(a, b, op=operator.le))
        expected = [((0, 1), (0, 1)), ((1, 3), (2, 3))]
        assert results == expected

        with pytest.raises(
            ValueError, match="2nd item 3 in first iterable not .* corresponding"
        ):
            list(zip_compare(a, b, op=operator.eq))

    def test_exception_item_not_found_le(self):
        """Test ValueError when item from first iterator not found in remaining second iterator"""
        a = [1, "missing"]
        b = [1, 2, 3]  # 'missing' string not in remaining items

        with pytest.raises(
            ValueError, match="2nd item 'missing' in first iterable not"
        ):
            list(zip_compare(a, b, op=operator.le))

    def test_exception_subset_not_satisfied(self):
        """Test ValueError when subset relationship not satisfied"""
        a = [frozenset({1, 5})]  # {1,5} is not subset of {1,2,3}
        b = [frozenset({1, 2, 3})]

        with pytest.raises(
            ValueError, match="1st item frozenset.*in first iterable not"
        ):
            list(zip_compare(a, b, op=operator.le))

    def test_exception_eq_mismatch(self):
        """Test ValueError when equality comparison fails due to mismatch"""
        a = [1, 3]
        b = [1, 2, 4]  # 3 != 2, and eq requires exact match at each position

        with pytest.raises(
            ValueError,
            match="2nd item 3 in first iterable not .* to corresponding item 2",
        ):
            list(zip_compare(a, b, op=operator.eq))

    def test_exception_second_exhausted(self):
        """Test ValueError when second iterator exhausts before finding match"""
        a = [1, 2, "not_found"]
        b = [1, 2]  # Missing item for 'not_found'

        with pytest.raises(
            ValueError, match="3rd item 'not_found' in first iterable not"
        ):
            list(zip_compare(a, b, op=operator.eq))

    def test_empty_iterators(self):
        """Test zip_compare with empty iterators"""
        results = list(zip_compare([], [], op=operator.eq))
        assert results == []

    def test_first_empty_second_not(self):
        """Test zip_compare when first iterator is empty but second is not"""
        results = list(zip_compare([], [1, 2, 3], op=operator.le))
        assert results == []

    def test_with_mixed_types(self):
        """Test with mixed data types that support recursive comparison"""
        a = [{"a": 1}, [2, 3]]
        b = [{"a": 1, "b": 2}, [1, 2, 4], [2, 3]]

        results = list(zip_compare(a, b, op=operator.le))
        expected = [((0, {"a": 1}), (0, {"a": 1, "b": 2})), ((1, [2, 3]), (2, [2, 3]))]
        assert results == expected

    def test_with_generator_inputs(self):
        """Test zip_compare works with generator inputs"""

        def gen_a():
            yield "first"
            yield "third"

        def gen_b():
            yield "first"
            yield "second"
            yield "third"
            yield "fourth"

        results = list(zip_compare(gen_a(), gen_b(), op=operator.le))
        expected = [((0, "first"), (0, "first")), ((1, "third"), (2, "third"))]
        assert results == expected

        with pytest.raises(
            ValueError, match="2nd item 'third' in first iterable not .* corresponding"
        ):
            list(zip_compare(gen_a(), gen_b(), op=operator.eq))


class TestComparisonStrength:
    def test_enum_values_ordered(self):
        """Test that ComparisonResult enum values are properly ordered"""
        assert ComparisonResult.FALSE < ComparisonResult.LT
        assert ComparisonResult.LT < ComparisonResult.LE
        assert ComparisonResult.LE < ComparisonResult.EQ

    def test_basic_enum_results(self):
        """Test _get_comparison_strength returns correct enum values"""
        # Sets
        assert _get_comparison_strength({1, 2}, {1, 2, 3}) == ComparisonResult.LT
        assert _get_comparison_strength({1, 2}, {1, 2}) == ComparisonResult.EQ
        assert _get_comparison_strength({1, 4}, {1, 2, 3}) == ComparisonResult.FALSE

        # Lists
        assert _get_comparison_strength([1, 2], [1, 2, 3]) == ComparisonResult.LT
        assert _get_comparison_strength([1, 2], [1, 2]) == ComparisonResult.EQ
        assert _get_comparison_strength([1, 4], [1, 2, 3]) == ComparisonResult.FALSE

        # Dicts
        assert (
            _get_comparison_strength({"a": 1}, {"a": 1, "b": 2}) == ComparisonResult.LT
        )
        assert _get_comparison_strength({"a": 1}, {"a": 1}) == ComparisonResult.EQ
        assert (
            _get_comparison_strength({"a": 1, "c": 1}, {"a": 1, "b": 2})
            == ComparisonResult.FALSE
        )

        # Literals
        assert _get_comparison_strength(1, 1) == ComparisonResult.EQ
        assert _get_comparison_strength(1, 2) == ComparisonResult.FALSE

    def test_nested_structure_aggregation(self):
        """Test that min() aggregation works correctly for nested structures"""
        # Nested sets: child has LT, should propagate
        assert (
            _get_comparison_strength({frozenset({1, 2})}, {frozenset({1, 2, 3})})
            == ComparisonResult.LT
        )

        # Dict with nested structure having strict subset
        assert (
            _get_comparison_strength({"a": {1, 2}}, {"a": {1, 2, 3}})
            == ComparisonResult.LT
        )

        # Mixed: dict has extra key (LT) but nested value is equal (EQ) -> min = LT
        assert (
            _get_comparison_strength({"a": 1}, {"a": 1, "b": 2}) == ComparisonResult.LT
        )

        # Both structures have differences
        data1 = {"sets": {frozenset({1, 2})}, "lists": [[1, 2]]}
        data2 = {"sets": {frozenset({1, 2, 3})}, "lists": [[1, 2, 3]]}
        assert _get_comparison_strength(data1, data2) == ComparisonResult.LT

    def test_strict_subset_semantics_with_enum(self):
        """Test that the new implementation correctly handles strict subset"""
        # Test cases that should return LT (strict subset)
        assert deepset({1, 2}) < deepset({1, 2, 3})
        assert not deepset({1, 2}) < deepset({1, 2})

        # Nested strict subset
        assert deepset({frozenset({1, 2})}) < deepset({frozenset({1, 2, 3})})
        assert not deepset({frozenset({1, 2})}) < deepset({frozenset({1, 2})})

        # Dict with extra key
        assert deepset({"a": 1}) < deepset({"a": 1, "b": 2})
        assert not deepset({"a": 1}) < deepset({"a": 1})

        # Dict with nested strict subset
        assert deepset({"a": {1, 2}}) < deepset({"a": {1, 2, 3}})
        assert not deepset({"a": {1, 2}}) < deepset({"a": {1, 2}})

        # Lists with extra elements
        assert deepset([1, 2]) < deepset([1, 2, 3])
        assert not deepset([1, 2]) < deepset([1, 2])
