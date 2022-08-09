# pfutils

This program is a basic sketching step. (I'm benchmarking performance with basic code)
---
Basically, concurrency is not important when using Direct-attached storage(DAS). Reading blocks is a major bottleneck for DAS because metadata is very small and can be read immediately.

But what about network-attached storage (NAS)? To read metadata from a file system that satisfies concurrency, communication with the metadata server(MDS) is required. The MDS may need to be read by communicating with another NAS. In that case, a round trip time of several milliseconds may occur. This is part of an unnecessary bottleneck, as it introduces another overhead that DAS does not have.

Basic file handling commands such as cp and rm in linux do not meet this requirement because they are made to target the traditional DAS. This application is designed to meet these needs.

# Usage

## Installation

Depending on how python is installed, the command may be slightly different. You can usually install it with one of the commands below.

```
# If python3-pip is named "pip3"
$ pip3 install pfutils
# If pip is unnamed but there is pip module in "python3"
$ python3 -m pip install pfutils
# If it is named without "3", remove "3" as appropriate...
```

Following the flow of the Python package installer, the pftuils command can be used as follows:

```
# If you have sudo privileges, the command will be installed in /usr/local/bin and so on, and you can run it right away.
$ pfutils --help

# If you don't have sudo privileges, the commands will be installed in ~/.local/bin etc. and you need to add this path to $PATH so
# that it can be executed without path.

# Regardless of the environment variable, if python3 is in the path, it can be executed as follows.
$ python3 -m pfutils --help
```

## Commands

```
Usage: pfutils cp [OPTIONS] SRC DST

  copy files and directories

Options:
  -j, --num-workers INTEGER  number of concurrent workers
  -c, --chunksize INTEGER    size of chunk
  -r, --recursive            copy directories recursively
  --help                     Show this message and exit.

Usage: pfutils rm [OPTIONS] [FILE]...

  remove files or directories

Options:
  -j, --num-workers INTEGER  number of concurrent workers
  -r, --recursive            remove directories and their contents recursively
  -c, --chunksize INTEGER    size of chunk
  --help                     Show this message and exit.
```

# Implementation focus

Under Python's GIL constraints, using threads is known to improve IO performance, but when concurrency is actually granted using ThreadPoolExecutor, you can see that this is not really the case. So I used ProcessPoolExecutor in my implementation of Python.
 
In case of using the map method, since the block operation starts after reading all the metadata, operation loss occurs during that time. However, when the submit method is used, the performance is greatly degraded because chunks are not divided. (It is the same as when giving chunksize=1 in the map.) Therefore, I modified the ProcessPoolExecutor so that it can be executed in chunks to give concurrency to the task.

I can give concurrency to reading metadata as well, but there doesn't seem to be a need for that operation to improve performance. However, its implementation may change in the future to work with more metadata.

When implemented as a thread in C++ and bound to Python, there was a performance improvement under a small cpu resource due to the difference in overhead between process and thread. However, my C++ implementation is not smooth, so I plan to implement the same behavior in C++ after completing the python implementation.

# Performance Benchmark under cephfs

## Cluster configuration

```mermaid
  graph TD;
      Client-->OSD_0;
      Client-->OSD_1;
      Client-->OSD_2;
      Client-->MDS;
      MDS-->OSD_0;
      MDS-->OSD_1;
      MDS-->OSD_2;
```

OSD is used to write blocks in cephfs and MDS is used to perform file system related operations. MDS also writes data into the OSD to safely manage the metadata it uses. I connected Client, OSD, and MDS through L2 switch of 10Gbps, and 3 OSD nodes were configured using ramdisk to sufficiently satisfy 10Gbps switch. No replication is configured.

## Experiment

Writing a large amount to a single file does not reveal the metadata overhead, which is a problem when using a network-based file system when only block IO is used. I will use as an example the copy and delete of imagenet, which may appear in general.

## cp

### DAS to DAS (different filesystems)

### DAS to DAS (same filesystem)

### DAS to NAS

### NAS to NAS (same filesystem)

### NAS to DAS

## pfutils cp -j20 -c20000 -r

### DAS to DAS (different filesystems)

### DAS to DAS (same filesystem)

### DAS to NAS

### NAS to NAS (same filesystem)

### NAS to DAS
