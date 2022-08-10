
def determine_chunk_size(length, num_workers):
    chunksize, extra = divmod(length, num_workers * 10)
    if extra:
        chunksize += 1
    if length == 0:
        chunksize = 0
    return chunksize