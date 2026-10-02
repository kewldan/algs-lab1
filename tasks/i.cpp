#include <cstdint>
#include <iostream>

// Состояние генератора псевдослучайных чисел из условия.
struct Generator {
  uint32_t a;
  uint32_t b;
  uint32_t cur;  // Начальное значение 0.
};

// 24-битное число: от 0 до 2^24 - 1. Вычисления идут с переполнением
// по модулю 2^32.
uint32_t Next24(Generator* generator) {
  generator->cur = (generator->cur * generator->a) + generator->b;
  return generator->cur >> 8;
}

// 32-битное число на основе двух 24-битных: от 0 до 2^32 - 1.
uint32_t Next32(Generator* generator) {
  uint32_t x = Next24(generator);
  uint32_t y = Next24(generator);
  return (x << 8) ^ y;
}

// Сортирует values по неубыванию сортировкой за линейное время и возвращает
// сумму x_i * i, где i — позиция в отсортированном массиве (с 1).
uint64_t SortAndWeigh(uint32_t* values, int n) {
  // TODO
  return 0;
}

int main() {
  std::ios::sync_with_stdio(false);
  std::cin.tie(nullptr);

  int tests;
  int n;
  uint32_t a;
  uint32_t b;
  std::cin >> tests >> n >> a >> b;
  auto* values = new uint32_t[n];
  Generator generator = {a, b, 0};
  while (tests-- > 0) {
    for (int i = 0; i < n; ++i) {
      values[i] = Next32(&generator);
    }
    std::cout << SortAndWeigh(values, n) << "\n";
  }
  delete[] values;
  return 0;
}
