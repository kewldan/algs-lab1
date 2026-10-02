#include <iostream>

struct Track {
  int popularity;
  int stability;
  int index;  // Номер трека, нумерация с 1.
};

// Упорядочивает треки: сначала менее популярные, затем менее стабильные.
// При полном совпадении показателей сохраняется исходный порядок.
void SortTracks(Track* tracks, int n) {
  // TODO
}

int main() {
  std::ios::sync_with_stdio(false);
  std::cin.tie(nullptr);

  int n;
  std::cin >> n;
  auto* tracks = new Track[n];
  for (int i = 0; i < n; ++i) {
    std::cin >> tracks[i].popularity >> tracks[i].stability;
    tracks[i].index = i + 1;
  }
  SortTracks(tracks, n);
  for (int i = 0; i < n; ++i) {
    std::cout << tracks[i].index << " ";
  }
  std::cout << "\n";
  delete[] tracks;
  return 0;
}
