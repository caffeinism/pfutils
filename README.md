# pfutils

This program is a basic sketching step. (I'm benchmarking performance with basic code)
---
Basically, concurrency is not important when using Direct-attached storage(DAS). Reading blocks is a major bottleneck for DAS because metadata is very small and can be read immediately.

But what about network-attached storage (NAS)? To read metadata from a file system that satisfies concurrency, communication with the metadata server(MDS) is required. The MDS may need to be read by communicating with another NAS. In that case, a round trip time of several milliseconds may occur. This is part of an unnecessary bottleneck, as it introduces another overhead that DAS does not have.

Basic file handling commands such as cp and rm in linux do not meet this requirement because they are made to target the traditional DAS. This application is designed to meet these needs.
