#include <cstdint>
#include <iostream>

// Возвращает количество сравнений, которые сделает сортировка вставками.
int64_t CountComparisons(const int* likes, int n) {
  // TODO
  return 0;
}

int main() {
  int n;
  std::cin >> n;
  int* likes = new int[n];
  for (int i = 0; i < n; ++i) {
    std::cin >> likes[i];
  }
  std::cout << CountComparisons(likes, n) << "\n";
  delete[] likes;
  return 0;
}
