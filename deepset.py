import operator
from collections import abc
from enum import Enum


def ordinal(num):
    quo, mod = divmod(num, 10)
    suf = quo % 10 != 1 and ordinal.suffixes.get(mod) or "th"
    return f"{num}{suf}"


ordinal.suffixes = {1: "st", 2: "nd", 3: "rd"}


class ComparisonResult(Enum):
    """Ordered enum representing the strength of subset relationships.

    Values are ordered from weakest to strongest relationship:
    FALSE < LT < LE < EQ

    This allows using min() to aggregate results across nested structures.
    """

    FALSE = 0  # No correspondence (items in a not found in b)
    LT = 1  # Strict subset (a < b, extras in b)
    LE = 2  # Subset or equal (a <= b, may have extras in b)
    EQ = 3  # Equal (a == b, identical)

    def __lt__(self, other):
        if isinstance(other, ComparisonResult):
            return self.value < other.value
        return NotImplemented


class ZipCompareError(ValueError):
    pass


def zip_compare(a, b, op=operator.le):
    """Attempts to compare two iterables for ordered set consistency; that the first iterable's
    items correspond to items in the second iterable.  Thus a "subset" (<=) correspondence between
    lists implies that all items from the first list exist in the second list, perhaps with
    intervening items in the second that don't match items from the first -- the second list may
    have extra items, but it must have the first list's items, in the correct order.

    Consumes two iterators while items are found in the second satisfying 'op' on each item in
    the first.  Yields the matching enumerated items in each iterable.

    Ceases consuming items when first iterator is exhausted; to confirm op=operator.eq, the second
    iterator must be tested for completion by the caller.

    """
    ea = enumerate(a)
    eb = enumerate(b)
    bi = 0
    for ai, x in ea:
        # See an item of b that satisfies the op.  If b is exhausted, a cannot be </<=/== b
        bi_from = bi
        while True:
            try:
                bi, y = next(eb)
            except StopIteration:
                raise ZipCompareError(
                    f"{ordinal(ai+1)} item {x!r} in first iterable not {op}"
                    f" to any item from {ordinal(bi_from+1)} through {ordinal(bi+1)} in second iterable"
                )
            if recursive_compare(x, y, op=op):
                break
            if op == operator.eq:
                raise ZipCompareError(
                    f"{ordinal(ai+1)} item {x!r} in first iterable not {op}"
                    f" to corresponding item {y!r} in second iterable"
                )
        yield (ai, x), (bi, y)


def recursive_compare(a, b, op=operator.le):
    """Recursively apply `op` (only <, <=, =) to all nested elements of a and b.

    Returns True if the relationship between a and b satisfies the requested operator.
    """
    assert op in (operator.le, operator.lt, operator.eq)

    # Get the actual relationship strength
    result = _get_comparison_strength(a, b)

    # Map result to boolean based on requested operator
    if op == operator.eq:
        return result == ComparisonResult.EQ
    elif op == operator.le:
        return result in (ComparisonResult.EQ, ComparisonResult.LE, ComparisonResult.LT)
    elif op == operator.lt:
        return result == ComparisonResult.LT

    return False


def _get_comparison_strength(a, b):
    """Returns the strongest valid relationship between a and b.

    Returns ComparisonResult enum indicating:
    - EQ: a == b (identical)
    - LE: a <= b (subset, may have extras in b)
    - LT: a < b (strict subset, has extras in b)
    - FALSE: no valid relationship (items in a not found in b)
    """
    if isinstance(a, abc.Mapping) and isinstance(b, abc.Mapping):
        return _compare_mappings(a, b)
    elif isinstance(a, abc.Set) and isinstance(b, abc.Set):
        return _compare_sets(a, b)
    elif (
        isinstance(a, abc.Iterable)
        and isinstance(b, abc.Iterable)
        and not isinstance(a, (str, bytes, abc.Mapping, abc.Set))
        and not isinstance(b, (str, bytes, abc.Mapping, abc.Set))
    ):
        return _compare_iterables(a, b)
    else:
        # Literals and unmatched types
        return ComparisonResult.EQ if a == b else ComparisonResult.FALSE


def _compare_mappings(a, b):
    """Compare two mappings and return relationship strength."""
    a_keys = set(a.keys())
    b_keys = set(b.keys())

    # Check if a's keys are subset of b's keys
    if not a_keys.issubset(b_keys):
        return ComparisonResult.FALSE

    # Start with best case - determine if we have extra keys in b
    result = ComparisonResult.LT if len(b_keys) > len(a_keys) else ComparisonResult.EQ

    # Compare values for all keys in a
    for k in a_keys:
        child_result = _get_comparison_strength(a[k], b[k])
        result = min(result, child_result)
        if result == ComparisonResult.FALSE:
            break

    return result


def _compare_sets(a, b):
    """Compare two sets and return relationship strength."""
    # Check for items in a not in b first
    equal = a & b
    a_uniq = a - equal
    b_uniq = b - equal

    # If sets are identical
    if len(equal) == len(a):
        if len(b) == len(a):
            return ComparisonResult.EQ
        if len(b) > len(a):
            return ComparisonResult.LT

    # If a has items not in b, check recursive relationships
    a_used = set()
    b_used = set()
    result = ComparisonResult.LT if len(b_uniq) > 0 else ComparisonResult.LE

    for x in a_uniq:
        # Try to find a match in b_uniq first
        found = False
        for y in b_uniq:
            child_result = _get_comparison_strength(x, y)
            if child_result != ComparisonResult.FALSE:
                a_used.add(x)
                b_used.add(y)
                b_uniq.remove(y)
                result = min(result, child_result)
                found = True
                break

        if not found:
            # Try to find a match in already used items from b
            for y in b_used:
                child_result = _get_comparison_strength(x, y)
                if child_result != ComparisonResult.FALSE:
                    a_used.add(x)
                    result = min(result, child_result)
                    found = True
                    break

        if not found:
            return ComparisonResult.FALSE

    return result


def _compare_iterables(a, b):
    """Compare two iterables and return relationship strength."""
    a_list = list(a)
    b_list = list(b)

    try:
        # Use zip_compare to find matching pairs
        result = ComparisonResult.EQ
        a_iter = iter(a_list)
        b_iter = iter(b_list)
        matched_b_indices = set()

        for (ai, x), (bi, y) in zip_compare(a_iter, b_iter, op=operator.le):
            matched_b_indices.add(bi)
            # Get relationship for this pair
            child_result = _get_comparison_strength(x, y)
            result = min(result, child_result)
            if result == ComparisonResult.FALSE:
                return ComparisonResult.FALSE

        # Check if b has unmatched elements (makes it LT if we had EQ)
        if len(matched_b_indices) < len(b_list) and result == ComparisonResult.EQ:
            result = ComparisonResult.LT

        return result

    except ZipCompareError:
        return ComparisonResult.FALSE


class DeepSet:
    def __init__(self, data):
        self.data = data

    def __eq__(self, other):
        if not isinstance(other, DeepSet):
            other = DeepSet(other)
        return recursive_compare(self.data, other.data, operator.eq)

    def __ne__(self, other):
        if not isinstance(other, DeepSet):
            other = DeepSet(other)
        return not recursive_compare(self.data, other.data, operator.eq)

    def __lt__(self, other):
        if not isinstance(other, DeepSet):
            other = DeepSet(other)
        return recursive_compare(self.data, other.data, operator.lt)

    def __le__(self, other):
        if not isinstance(other, DeepSet):
            other = DeepSet(other)
        return recursive_compare(self.data, other.data, operator.le)

    def __ge__(self, other):
        if not isinstance(other, DeepSet):
            other = DeepSet(other)
        return recursive_compare(other.data, self.data, operator.le)

    def __gt__(self, other):
        if not isinstance(other, DeepSet):
            other = DeepSet(other)
        return recursive_compare(other.data, self.data, operator.lt)


def deepset(data):
    return DeepSet(data)
