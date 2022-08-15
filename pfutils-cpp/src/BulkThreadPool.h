#include "BS_thread_pool.hpp"
#include "FutureVector.h"
#include <vector>
#include <memory>

template <typename R>
class BulkThreadPool{
private:
    BS::thread_pool pool;
    uint32_t chunk_size;
    std::vector<std::function<R()>> task_queue;
    std::vector<std::future<R>> futures;
public:
    BulkThreadPool(
        uint32_t num_threads, 
        uint32_t chunk_size
    ) : pool(num_threads), chunk_size(chunk_size)
    {}
    
    template <typename F, typename... A>
    void push(F&&, A&&...);
    void flush();
    std::shared_ptr<FutureVector<R>> flush_and_iter();
};

template <typename R>
template <typename F, typename... A>
void BulkThreadPool<R>::push(F&& task, A&&... args) {
    this->task_queue.emplace_back(
        [task=std::forward<F>(task), ...args=std::forward<A>(args)] () -> void {
            task(args...);
        }
    );
    if (task_queue.size() == this->chunk_size) {
        this->flush();
    }
}

template <typename R>
void BulkThreadPool<R>::flush() {
    if (this->task_queue.size() == 0)
        return;

    this->futures.emplace_back(
        this->pool.submit(
            [task_queue = task_queue]() -> void {
                for (auto &task : task_queue) {
                    task();
                }
            }
        )
    );
    this->task_queue.clear();
}

template <typename R>
std::shared_ptr<FutureVector<R>> BulkThreadPool<R>::flush_and_iter() {
    this->flush();
    return std::make_shared<FutureVector<R>>(std::move(this->futures));
}
