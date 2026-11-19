from typing import List, Set


def simulate_fifo(refs: List[int], frames_count: int) -> int:
    """Алгоритм замещения страниц FIFO (First-In, First-Out)."""
    frames: List[int] = []
    faults = 0

    for page in refs:
        if page not in frames:
            faults += 1
            if len(frames) < frames_count:
                frames.append(page)
            else:
                frames.pop(0)
                frames.append(page)
    return faults


def simulate_lru(refs: List[int], frames_count: int) -> int:
    """Алгоритм замещения страниц LRU (Least Recently Used)."""
    frames: List[int] = []  # В конце списка — самый недавно использованный кадр
    faults = 0

    for page in refs:
        if page in frames:
            # Обновляем порядок использования при каждом обращении (и при hit, и при miss)
            frames.remove(page)
            frames.append(page)
        else:
            faults += 1
            if len(frames) < frames_count:
                frames.append(page)
            else:
                # Вытесняем страницу, к которой дольше всего не обращались
                frames.pop(0)
                frames.append(page)
    return faults


def simulate_optimal(refs: List[int], frames_count: int) -> int:
    """Оптимальный алгоритм замещения страниц (заглядывание вперёд)."""
    frames: List[int] = []
    faults = 0
    n = len(refs)

    for idx, page in enumerate(refs):
        if page in frames:
            continue

        faults += 1
        if len(frames) < frames_count:
            frames.append(page)
        else:
            # Ищем страницу в кадрах, которая понадобится позже всех (или не понадобится вовсе)
            farthest_idx = -1
            victim_page = frames[0]

            for f_page in frames:
                try:
                    next_use = refs.index(f_page, idx + 1)
                except ValueError:
                    # Страница больше не встретится в строке — идеальный кандидат на вытеснение
                    victim_page = f_page
                    break

                if next_use > farthest_idx:
                    farthest_idx = next_use
                    victim_page = f_page

            frames.remove(victim_page)
            frames.append(page)

    return faults


if __name__ == "__main__":
    ref_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]

    print("Контрольная строка:", " ".join(map(str, ref_string)))
    print("-" * 52)
    print(f"{'Алгоритм':<12} | {'3 кадра (эталон)':<20} | {'4 кадра':<10}")
    print("-" * 52)

    expected_3 = {"FIFO": 15, "LRU": 12, "Optimal": 9}
    for name, func in [("FIFO", simulate_fifo), ("LRU", simulate_lru), ("Optimal", simulate_optimal)]:
        f3 = func(ref_string, 3)
        f4 = func(ref_string, 4)
        exp = expected_3[name]
        print(f"{name:<12} | {f3:<3} (ожидалось {exp:<2}) | {f4:<10}")