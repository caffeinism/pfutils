from collections.abc import Sequence, Mapping

def chain_get(indexable, indexes, default=None):
    pivot = indexable
    
    for index in indexes:
        if (isinstance(pivot, Mapping) and index in pivot) or (isinstance(pivot, Sequence) and len(pivot) > index):
            pass
        else:
            return default
        
        pivot = pivot[index]
        
    return pivot
