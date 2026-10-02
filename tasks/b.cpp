#include <iostream>

// Сортирует plays[left..right] по неубыванию быстрой сортировкой.
// Готовыми функциями сортировки пользоваться нельзя.
void QuickSort(int* plays, int left, int right) {
  // TODO
}

int main() {
  std::ios::sync_with_stdio(false);
  std::cin.tie(nullptr);

  int n;
  std::cin >> n;
  int* plays = new int[n];
  for (int i = 0; i < n; ++i) {
    std::cin >> plays[i];
  }
  QuickSort(plays, 0, n - 1);
  for (int i = 0; i < n; ++i) {
    std::cout << plays[i] << " ";
  }
  std::cout << "\n";
  delete[] plays;
  return 0;
}
