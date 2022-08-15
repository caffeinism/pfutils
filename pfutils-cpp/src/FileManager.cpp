#include "FileManager.h"
#include <utility>

FileManager::FileManager(
    uint32_t num_threads, 
    uint32_t chunk_size
) : bulk_pool(num_threads, chunk_size), copy_options(std::filesystem::copy_options::update_existing)
{}

void FileManager::copy_file(
    std::filesystem::path &src,
    std::filesystem::path &dst
) {
    this->bulk_pool.push(
        [src, dst, copy_options=copy_options]()->void{
            std::filesystem::copy_file(src, dst, copy_options);
        }
    );
}

void FileManager::remove_file(
    std::filesystem::path &path
) {
    this->bulk_pool.push(
        [path]()->void{
            std::filesystem::remove(path);
        }
    );
}

std::shared_ptr<FutureVector<void>> FileManager::flush_and_iter() {
    return this->bulk_pool.flush_and_iter();
}
