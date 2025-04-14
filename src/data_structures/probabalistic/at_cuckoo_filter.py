import random
from typing import Any, Optional

import mmh3


class ATCuckooFilter:
    class Bucket:
        def __init__(self, size: int):
            self._array: list[Optional[int]] = [None] * size
            self._size = size

        def insert(self, item: int):
            for i, x in enumerate(self._array):
                if not x:
                    self._array[i] = item
                    return

        def is_full(self):
            if None in self._array:
                return False
            return True

        def contains(self, item: int):
            if item in self._array:
                return True
            return False

        def delete(self, item: int):
            self._array[self._array.index(item)] = None

        def evict(self):
            rand_i = random.randint(0, self._size - 1)
            evicted_fingerprint = self._array[rand_i]
            self._array[rand_i] = None

            return evicted_fingerprint

    def __init__(
        self,
        num_buckets: int,
        bucket_size: int,
        fingerprint_size: int = 12,
        max_tries: int = 400,
    ):
        self.num_buckets = num_buckets
        self.buckets = [self.Bucket(bucket_size) for _ in range(num_buckets)]
        self.bucket_size = bucket_size
        self.fingerprint_size = fingerprint_size
        self.max_tries = max_tries

    def add(self, item: Any):
        # calculate fingerprint and buckets
        fingerprint = self._fingerprint(item)
        first_bucket = self._first_bucket(item)
        second_bucket = self._second_bucket(first_bucket, fingerprint)

        # place item in buckets
        # if first is full, place in second
        # if second is full, reallocate buckets until space is found
        # if all buckets are full, raise error
        if not self.buckets[first_bucket].is_full():
            self.buckets[first_bucket].insert(fingerprint)
            return True
        elif not self.buckets[second_bucket].is_full():
            self.buckets[second_bucket].insert(fingerprint)
            return True
        else:
            for _ in range(self.max_tries):
                # randomly pick one of the buckets to evict from
                if random.randint(0, 1) == 0:
                    evicting_bucket = first_bucket
                else:
                    evicting_bucket = second_bucket
                # evict a fingerprint from the bucket
                evicted_fingerprint = self.buckets[evicting_bucket].evict()
                # calculate what the evicted fingerprint's other bucket is
                other_bucket = self._second_bucket(evicting_bucket, evicted_fingerprint)

                # insert the original fingerprint in the bucket now that
                # there is space
                self.buckets[evicting_bucket].insert(fingerprint)

                # if the evicted fingerprint's other bucket has space,
                # insert the fingerprint and stop looping
                if not self.buckets[other_bucket].is_full():
                    self.buckets[other_bucket].insert(evicted_fingerprint)
                    return True
                # else reset variable and repeat
                first_bucket = evicting_bucket
                second_bucket = other_bucket

            raise ValueError(
                f"All buckets are full or max_tries ({str(self.max_tries)}) exceeded"
            )

    def prob_contains(self, item: Any):
        fingerprint = self._fingerprint(item)
        first_bucket = self._first_bucket(item)
        second_bucket = self._second_bucket(first_bucket, fingerprint)

        if (self.buckets[first_bucket] == fingerprint) or (
            self.buckets[second_bucket] == fingerprint
        ):
            return True

        return False

    def delete(self, item: Any):
        fingerprint = self._fingerprint(item)
        first_bucket = self._first_bucket(item)
        second_bucket = self._second_bucket(first_bucket, fingerprint)

        if self.buckets[first_bucket].contains(fingerprint):
            self.buckets[first_bucket].delete(fingerprint)
            return True
        elif self.buckets[second_bucket].contains(fingerprint):
            self.buckets[second_bucket].delete(fingerprint)
            return True

        return False

    def _first_bucket(self, item):
        return self._hash(item)

    def _second_bucket(self, first_bucket, fingerprint):
        return (first_bucket ^ self._hash(fingerprint)) % self.num_buckets

    def _fingerprint(self, item: Any):
        return mmh3.hash(str(item), seed=123) & ((1 << self.fingerprint_size) - 1)

    def _hash(self, item: Any):
        return mmh3.hash(str(item), seed=321) % self.num_buckets
