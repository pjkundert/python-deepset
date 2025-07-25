import operator
from collections import abc


def ordinal(num):
    quo, mod = divmod(num, 10)
    suf = quo % 10 != 1 and ordinal.suffixes.get(mod) or "th"
    return f"{num}{suf}"


ordinal.suffixes = {1: "st", 2: "nd", 3: "rd"}


class ZipCompareError( ValueError ):
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
    """Recursively apply `op` (only <, <=, =) to all nested elements of a and b."""
    assert op in (operator.le, operator.lt, operator.eq)

    if isinstance(a, abc.Mapping) and isinstance(b, abc.Mapping):
        # Keys compared as sets (subset), values compared recursively for shared keys
        a_keys = set(a.keys())
        b_keys = set(b.keys())

        # For equality, key sets must be identical
        if op == operator.eq and a_keys != b_keys:
            return False

        # Check if a_keys is subset of b_keys
        if not a_keys.issubset(b_keys):
            return False

        # Compare values for all keys in a
        return all(recursive_compare(a[k], b[k], op) for k in a_keys)

    elif isinstance(a, abc.Set) and isinstance(b, abc.Set):
        # For sets, every non-equal non-literal element in a must be 'op' (eg <=, a subset) of some element in b.
        # The problem is, literals and exactly matching complex objects are easy to factor out using standard set operations.
        equal = a & b
        a_uniq = a - equal
        b_uniq = b - equal
        a_used = set()
        b_used = set()
        if len(equal) == len(a) == len(b):
            return op in (operator.eq, operator.le)
        # The sets are not trivially equal.  Examine the remaining unique items in a vs. b's
        # unique, then previously matched items.
        for x in a_uniq:
            for y in b_uniq:
                if recursive_compare(x, y, op):
                    a_used.add(x)
                    b_used.add(y)
                    b_uniq.remove(y)
                    break
            else:
                for y in b_used:
                    if recursive_compare(x, y, op):
                        a_used.add(x)
                        break
                else:
                    # Item x from a not found in b!  A cannot be </<=/==
                    return False
        # All x in a were found to be equal or match 'op' via recursive_compare w/ some y in b.
        # This satisfies <=/==/>=.  For <, we must have some b_uniq left unmatched by any a.
        if op == operator.lt:
            return len(b_uniq) > 0
        if op == operator.eq:
            return len(b_uniq) == 0
        return True
    elif (
        isinstance(a, abc.Iterable)
        and isinstance(b, abc.Iterable)
        and not isinstance(a, (str, bytes, abc.Mapping, abc.Set))
        and not isinstance(b, (str, bytes, abc.Mapping, abc.Set))
    ):
        # Sequential matching: each element in a must match some element at same or later position in b
        a_iter = iter(a)
        b_iter = iter(b)
        try:
            for (ai, x), (bi, y) in zip_compare(a_iter, b_iter, op=op):
                pass
        except ZipCompareError:
            return False

        if op == operator.eq:
            try:
                y = next(b_iter)
                raise ZipCompareError(
                    f"{ordinal(ai+1)} item {x!r} in first iterable not {op}"
                    f" due to additional {ordinal(bi+2)} item {y!r} in second iterable"
                )
            except StopIteration:
                pass

        return True

    else:
        # Unmatched types and Literals: only equality comparison
        if op in (operator.lt, operator.le, operator.gt, operator.ge):
            return a == b
        else:
            return op(a, b)


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
        return recursive_compare(other.data, self.data, operator.le)


def deepset(data):
    return DeepSet(data)
