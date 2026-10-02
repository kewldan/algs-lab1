CXX      := c++
CXXFLAGS := -std=c++20 -O2 -Wall -Wextra -Wno-unused-parameter
PYTHON   := python3

TASKS := a b c d e f g h i
BUILD := build
JUDGE_FLAGS :=

# make a SAN=1 — сборка с AddressSanitizer и UBSan. Лимиты времени и памяти
# при этом не проверяются: санитайзеры сильно замедляют программу.
ifeq ($(SAN),1)
  CXXFLAGS := -std=c++20 -O1 -g -Wall -Wextra -Wno-unused-parameter \
              -fsanitize=address,undefined -fno-omit-frame-pointer
  BUILD := build/san
  JUDGE_FLAGS := --no-limits
endif

JUDGE := CXX="$(CXX)" CXXFLAGS="$(CXXFLAGS)" $(PYTHON) tools/judge.py --build-dir $(BUILD) $(JUDGE_FLAGS)

.DEFAULT_GOAL := help
.PHONY: help test $(TASKS) $(addprefix run-,$(TASKS)) format clean

help:
	@echo "Лаба 1. Сортировки: музыкальный стриминг"
	@echo
	@echo "  make a ... make i   собрать задачу и прогнать её тесты"
	@echo "  make test           прогнать тесты всех задач"
	@echo "  make run-a          собрать задачу и запустить с вводом с клавиатуры"
	@echo "  make a SAN=1        то же, что make a, но с санитайзерами"
	@echo "  make format         отформатировать решения по Google C++ Style"
	@echo "  make clean          удалить собранные файлы"

test:
	@$(JUDGE) $(TASKS)

$(TASKS):
	@$(JUDGE) $@

$(addprefix run-,$(TASKS)): run-%:
	@$(JUDGE) --build-only $*
	@./$(BUILD)/$*

format:
	clang-format -i tasks/*.cpp

clean:
	rm -rf build
