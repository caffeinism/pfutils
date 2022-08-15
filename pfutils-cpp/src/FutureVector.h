#pragma once

#include <vector>
#include <future>

template <typename T>
class FutureVectorIterator {
private:
    std::vector<std::future<T>>::iterator it;
public:
    FutureVectorIterator(std::vector<std::future<T>>::iterator it): it(it) {}
    T operator*() const { return it->get(); }
    FutureVectorIterator<T>& operator++() { ++it; return *this; }
    bool operator== (const FutureVectorIterator<T> &other) { return this->it == other.it; }
    bool operator!= (const FutureVectorIterator<T> &other) { return this->it != other.it; }
};

template <typename T>
class FutureVector {
private:
    std::vector<std::future<T>> futures;
public:
    FutureVector(std::vector<std::future<T>> &&futures) : futures(std::move(futures)) {}
    FutureVectorIterator<T> begin() {
        return FutureVectorIterator<T>(this->futures.begin());
    }
    FutureVectorIterator<T> end() {
        return FutureVectorIterator<T>(this->futures.end());
    }
    int size() {
        return this->futures.size();
    }
};
