class MinHeap:
    def __init__(self):
        self.heap = []

    def parent(self, i):
        return (i - 1) // 2

    def left(self, i):
        return 2*i + 1

    def right(self, i):
        return 2*i + 2

    def swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def push(self, val):
        self.heap.append(val)
        self._heapify_up(len(self.heap) - 1)

    def _heapify_up(self, i):
        while i > 0 and self.heap[i] < self.heap[self.parent(i)]:
            self.swap(i, self.parent(i))
            i = self.parent(i)

    def pop(self):
        if not self.heap:
            return None

        if len(self.heap) == 1:
            return self.heap.pop()

        root = self.heap[0]

        self.heap[0] = self.heap.pop()

        self._heapify_down(0)

        return root

    def _heapify_down(self, i):
        n = len(self.heap)

        while True:
            smallest = i
            left = self.left(i)
            right = self.right(i)

            if left < n and self.heap[left] < self.heap[smallest]:
                smallest = left

            if right < n and self.heap[right] < self.heap[smallest]:
                smallest = right

            if smallest == i:
                break

            self.swap(i, smallest)
            i = smallest

    def top(self):
        return self.heap[0] if self.heap else None
    
def build_heap(arr):
    heap = MinHeap()
    heap.heap = arr[:]

    n = len(arr)

    for i in range((n // 2) - 1, -1, -1):
        heap._heapify_down(i)

    return heap

arr = [i for i in range(10)]
heap = build_heap(arr)
print(heap.heap)
