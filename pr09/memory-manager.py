from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class Block:
    start: int
    size: int
    pid: Optional[str] = None

    @property
    def is_free(self) -> bool:
        return self.pid is None


class MemoryManager:
    def __init__(self, total_size: int = 1024):
        self.total_size = total_size
        self.blocks: List[Block] = [Block(start=0, size=total_size, pid=None)]

    def _allocate_in_block(self, index: int, pid: str, size: int) -> bool:
        block = self.blocks[index]
        if not block.is_free or block.size < size:
            return False

        if block.size == size:
            block.pid = pid
        else:
            allocated = Block(start=block.start, size=size, pid=pid)
            remaining = Block(start=block.start + size, size=block.size - size, pid=None)
            self.blocks[index : index + 1] = [allocated, remaining]
        return True

    def first_fit(self, pid: str, size: int) -> bool:
        """Первый подходящий свободный блок."""
        for i, block in enumerate(self.blocks):
            if block.is_free and block.size >= size:
                return self._allocate_in_block(i, pid, size)
        return False

    def best_fit(self, pid: str, size: int) -> bool:
        """Наименьший подходящий свободный блок."""
        best_idx = -1
        best_size = self.total_size + 1
        for i, block in enumerate(self.blocks):
            if block.is_free and size <= block.size < best_size:
                best_size = block.size
                best_idx = i
        if best_idx != -1:
            return self._allocate_in_block(best_idx, pid, size)
        return False

    def worst_fit(self, pid: str, size: int) -> bool:
        """Наибольший подходящий свободный блок."""
        worst_idx = -1
        worst_size = -1
        for i, block in enumerate(self.blocks):
            if block.is_free and block.size >= size and block.size > worst_size:
                worst_size = block.size
                worst_idx = i
        if worst_idx != -1:
            return self._allocate_in_block(worst_idx, pid, size)
        return False

    def free(self, pid: str) -> bool:
        """Освобождение памяти процесса (с объединением соседних свободных блоков)."""
        found = False
        for block in self.blocks:
            if block.pid == pid:
                block.pid = None
                found = True

        i = 0
        while i < len(self.blocks) - 1:
            if self.blocks[i].is_free and self.blocks[i + 1].is_free:
                self.blocks[i].size += self.blocks[i + 1].size
                self.blocks.pop(i + 1)
            else:
                i += 1
        return found

    def render_map(self) -> str:
        """Текстовая визуализация карты памяти."""
        parts = []
        for b in self.blocks:
            label = f"FREE:{b.size}" if b.is_free else f"{b.pid}:{b.size}"
            parts.append(f"[{b.start}..{b.start + b.size - 1} | {label}]")
        return " ".join(parts)

    def external_fragmentation(self) -> Tuple[int, int]:
        """Возвращает (сумма свободных блоков, размер наибольшего свободного блока)."""
        free_sizes = [b.size for b in self.blocks if b.is_free]
        total_free = sum(free_sizes)
        max_free = max(free_sizes) if free_sizes else 0
        return total_free, max_free


def run_simulation(strategy_name: str, operations: List[str]):
    print(f"\n{'=' * 70}\nСТРАТЕГИЯ: {strategy_name.upper()}\n{'=' * 70}")
    mm = MemoryManager(1024)
    alloc_fn = getattr(mm, strategy_name)

    for step, op in enumerate(operations, 1):
        parts = op.strip().split()
        if not parts:
            continue
        cmd = parts[0].lower()
        if cmd == "alloc":
            pid, size = parts[1], int(parts[2])
            ok = alloc_fn(pid, size)
            status = "OK" if ok else "ОТКАЗ (недостаточно непрерывной памяти)"
            print(f"{step:02d}. alloc {pid} {size:<4} -> {status}")
        elif cmd == "free":
            pid = parts[1]
            ok = mm.free(pid)
            status = "OK" if ok else "ПРОЦЕСС НЕ НАЙДЕН"
            print(f"{step:02d}. free  {pid:<9} -> {status}")
        print(f"    Карта: {mm.render_map()}")

    total_free, max_free = mm.external_fragmentation()
    print(f"\nИтог ({strategy_name}):")
    print(f"  Сумма свободных блоков:      {total_free} ед.")
    print(f"  Наибольший свободный блок:   {max_free} ед.")
    return total_free, max_free


if __name__ == "__main__":
    ops1 = [
        "alloc P1 200",
        "alloc P2 150",
        "alloc P3 300",
        "alloc P4 100",
        "free P2",
        "alloc P5 120",
        "free P4",
        "alloc P6 80",
        "free P1",
        "alloc P7 90",
        "free P3",
        "alloc P8 110",
    ]


    results = {}
    for strat in ("first_fit", "best_fit", "worst_fit"):
        results[strat] = run_simulation(strat, ops1)

    print("\n" + "=" * 55)
    print(f"{'Стратегия':<15} | {'Свободно всего':<16} | {'Макс. блок':<15}")
    print("-" * 55)
    for strat, (tot, mx) in results.items():
        print(f"{strat:<15} | {tot:<16} | {mx:<15}")