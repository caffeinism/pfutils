import concurrent.futures

def _result_or_cancel(fut, timeout=None):
    try:
        try:
            return fut.result(timeout)
        finally:
            fut.cancel()
    finally:
        del fut

def _chain_from_iterable_of_lists(iterable):
    for element in iterable:
        element.reverse()
        while element:
            yield element.pop()

def _process_chunk(chunk):
    return [fn(*args, **kwargs) for fn, args, kwargs in chunk]

class ProcessPoolExecutor(concurrent.futures.ProcessPoolExecutor):
    def __init__(self, *args, chunksize, **kwargs):
        super().__init__(*args, **kwargs)
        self._chunk = []
        self.chunksize = chunksize
        self._futures = []

    def _submit_chunk(self):
        chunk, self._chunk = self._chunk, []
        self._futures.append(future := super().submit(_process_chunk, chunk))
        return future
        
    def submit(self, fn, /, *args, **kwargs):
        self._chunk.append((fn, args, kwargs))
        if len(self._chunk) == self.chunksize:
            self._submit_chunk()

    def flush(self):
        if self._chunk:
            self._submit_chunk()

        futures, self._futures = self._futures, []

        def result_iterator():
            try:
                futures.reverse()
                while futures:
                    yield _result_or_cancel(futures.pop())
            finally:
                for future in futures:
                    future.cancel()

        return _chain_from_iterable_of_lists(result_iterator())

    def __exit__(self, *args, **kwargs):
        if self._chunk:
            raise RuntimeError('there are remaining tasks. flush() is required')
        return super().__exit__(*args, **kwargs)
