#include "FileManager.h"
#include <utility>
#include <fstream>

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

void FileManager::write_file(
    std::filesystem::path &path,
    uint32_t file_size,
    bool randomness
) {
    this->bulk_pool.push(
        [path, file_size]()->void{
            char *byte_array = "0123456789abcdef";
            std::ofstream file(path, std::ios::binary | std::ios::out);

            for(uint32_t i=0; i<64 * file_size; ++i) {
                file.write(byte_array, 16);
            }
        }
    );
}

std::shared_ptr<FutureVector<void>> FileManager::flush_and_iter() {
    return this->bulk_pool.flush_and_iter();
}
