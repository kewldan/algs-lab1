#include <iostream>

struct Track {
  int popularity;
  int stability;
};

// Записывает в headliners номера (с 1) минимального набора треков, которые
// вместе перекрывают все остальные: x_a >= x_b и y_a >= y_b.
// Возвращает размер набора.
int FindHeadliners(const Track* tracks, int n, int* headliners) {
  // TODO
  return 0;
}

int main() {
  std::ios::sync_with_stdio(false);
  std::cin.tie(nullptr);

  int n;
  std::cin >> n;
  auto* tracks = new Track[n];
  int* headliners = new int[n];
  for (int i = 0; i < n; ++i) {
    std::cin >> tracks[i].popularity >> tracks[i].stability;
  }
  int count = FindHeadliners(tracks, n, headliners);
  std::cout << count << "\n";
  for (int i = 0; i < count; ++i) {
    std::cout << headliners[i] << " ";
  }
  std::cout << "\n";
  delete[] tracks;
  delete[] headliners;
  return 0;
}
