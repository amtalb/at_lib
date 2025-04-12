import math
from typing import Any, Optional


class ATBloomFilter:
    """A bloom filter"""

    def __init__(
        self,
        m: Optional[int] = None,
        k: Optional[int] = None,
    ):
        """Initialize the object

        Args:
            m (int): the number of bits in the bit array
            k (int): the number of hash functions
        """
        # check for valid inputs
        if not k or not m:
            raise ValueError("Must specify parameters 'k' and 'm'")

        self.k = k
        self.m = m

        # init n -- number of items in filter
        self.n = 0

        # init p -- false positive rate
        self.p = None
        self._calculate_p()

        self._bit_array = [0] * self.m

    def add(self, item: Any):
        """Add an item to the bloom filter

        Args:
            item (Any): The item to add to the bloom filter

        Returns:
            None
        """
        for _ in range(self.k):
            hash_val = self._hash(item)
            self._bit_array[hash_val % self.m] = 1

        # update n and p
        self.n += 1
        self._calculate_p()

    def prob_contains(self, item: Any):
        """Check if an item is in the bloom filter

        This function returns True if the item is in the bloom filter and
        _might_ return False if the item is not in the bloom filter. This
        false positive rate is specified in self.p

        Args:
            item (Any): The item to check for existence in the bloom filter

        Returns:
            bool
        """
        for _ in range(self.k):
            hash_val = self._hash(item)
            if self._bit_array[hash_val % self.m] != 1:
                return False

        return True

    def _calculate_p(self):
        """Calculate probability of false positive

        Args:
            None

        Returns:
            None
        """
        if self.n == 0:
            self.p = 0
        else:
            self.p = pow(1 - math.exp(-self.k / (self.m / self.n)), self.k)

    def _hash(self, item: Any):
        """Hash the item

        Args:
            item (Any): the item to be hashed

        Returns:
            int: the hashed value
        """
        return hash(item)


class ATScalableBloomFilter:
    """A self-scaling implementation of a bloom filter

    This data structure will automatically create a new bloom filter on top
    of the existing bloom filter(s) when the probability of false positives (p)
    exceeds the specified threshold (desired_p). In order to check for membership,
    all bloom filters in the stack must be searched.
    """

    def __init__(
        self,
        m: Optional[int] = None,
        k: Optional[int] = None,
        desired_p: Optional[float] = None,
    ):
        """ """
        if not desired_p:
            raise ValueError("Parameter 'desired_p' must be specified")

        self._bloom_filters = [ATBloomFilter(m, k)]
        self.desired_p = desired_p
        self.n = 0

        self._check_for_scale()

    def add(self, item: Any):
        self._bloom_filters[-1].add(item)

        self.n += 1
        self._check_for_scale()

    def prob_contains(self, item: Any):
        for bf in self._bloom_filters:
            if bf.prob_contains(item):
                return True

        return False

    def _check_for_scale(self):
        if self._bloom_filters[-1].p > self.desired_p:
            self._scale()

    def _scale(self):
        calculated_m = math.ceil(
            (self._bloom_filters[-1].n * math.log(self.desired_p))
            / math.log(1 / pow(2, math.log(2)))
        )
        calculated_k = round((calculated_m / self._bloom_filters[-1].n) * math.log(2))
        new_bf = ATBloomFilter(calculated_m, calculated_k)
        self._bloom_filters.append(new_bf)
