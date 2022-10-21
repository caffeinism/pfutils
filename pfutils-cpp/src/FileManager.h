#pragma once
#include <filesystem>
#include "BulkThreadPool.h"
#include <exception>

class FileManager {
private:
    BulkThreadPool<void> bulk_pool;
    const std::filesystem::copy_options copy_options;
public:
    FileManager(uint32_t, uint32_t);
    void copy_file(std::filesystem::path&, std::filesystem::path&);
    void remove_file(std::filesystem::path&);
    void write_file(std::filesystem::path&, uint32_t file_size, bool randomness);
    std::shared_ptr<FutureVector<void>> flush_and_iter();
};
