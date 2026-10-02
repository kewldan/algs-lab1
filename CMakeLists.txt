# Сборка для IDE (CLion, VS Code с CMake Tools, Visual Studio).
# Из терминала проще пользоваться make, см. README.
cmake_minimum_required(VERSION 3.16)
project(algs_lab1 LANGUAGES CXX)

# На sort-me решения проверяются на GNU C++20.
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Release)
endif()

if(MSVC)
  add_compile_options(/W4 /wd4100)
else()
  add_compile_options(-Wall -Wextra -Wno-unused-parameter)
endif()

set(TASKS a b c d e f g h i)

find_package(Python3 COMPONENTS Interpreter)
enable_testing()

foreach(task IN LISTS TASKS)
  add_executable(${task} tasks/${task}.cpp)

  # ctest -R a прогоняет тесты задачи A через тот же tools/judge.py, что и make.
  # В Debug-сборке время и память не проверяются: без оптимизаций код медленнее.
  if(Python3_FOUND)
    add_test(
      NAME ${task}
      COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/judge.py
              --binary $<TARGET_FILE:${task}>
              $<IF:$<CONFIG:Debug>,--no-limits,--limits>
              ${task})
  endif()
endforeach()
