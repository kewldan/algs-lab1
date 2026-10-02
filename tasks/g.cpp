#include <iostream>

// Вставляет трек с рейтингом rating в chart[0..*size - 1] так, чтобы чарт
// остался отсортирован по неубыванию, увеличивает *size на единицу и
// возвращает индекс (с нуля), на который трек встал.
// Среди равных рейтингов трек идёт самым правым.
int InsertTrack(int* chart, int* size, int rating) {
  // TODO
  return 0;
}

int main() {
  std::ios::sync_with_stdio(false);
  std::cin.tie(nullptr);

  int n;
  std::cin >> n;
  int* chart = new int[n];
  int size = 0;
  for (int i = 0; i < n; ++i) {
    int rating;
    std::cin >> rating;
    std::cout << InsertTrack(chart, &size, rating) << " ";
  }
  std::cout << "\n";
  delete[] chart;
  return 0;
}
