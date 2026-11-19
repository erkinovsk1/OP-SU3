import os
from typing import Dict, List, Optional

PAGE_SIZE = 1024       # 1 КБ
ADDRESS_SPACE = 16384  # 16 КБ (16 страниц: 0..15)


def load_page_table(filename: str) -> Dict[int, Optional[int]]:
    """Загружает таблицу страниц формата 'страница -> кадр' или 'отсутствует'."""
    page_table: Dict[int, Optional[int]] = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            for sep in ("->", "→", ":", "="):
                line = line.replace(sep, " ")
            parts = line.split()
            page = int(parts[0])
            val = parts[1].lower()
            if val in ("none", "null", "absent", "отсутствует", "-"):
                page_table[page] = None
            else:
                page_table[page] = int(val)
    return page_table


def load_refs(filename: str) -> List[int]:
    refs: List[int] = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            for token in line.replace(",", " ").split():
                refs.append(int(token))
    return refs


def translate_address(logical_addr: int, page_table: Dict[int, Optional[int]]) -> str:
    if logical_addr < 0 or logical_addr >= ADDRESS_SPACE:
        return f"Лог. адрес {logical_addr:<5} -> ОШИБКА: выход за пределы адресного пространства (0..{ADDRESS_SPACE - 1})"

    page = logical_addr // PAGE_SIZE
    offset = logical_addr % PAGE_SIZE
    frame = page_table.get(page, None)

    if frame is None:
        return (
            f"Лог. адрес {logical_addr:<5} -> стр. {page:<2}, смещ. {offset:<4} "
            f"-> ОШИБКА: страница отсутствует (Page Fault)"
        )

    physical_addr = frame * PAGE_SIZE + offset
    return (
        f"Лог. адрес {logical_addr:<5} -> стр. {page:<2}, смещ. {offset:<4} "
        f"-> кадр {frame:<2} -> Физ. адрес: {physical_addr}"
    )


def ensure_default_files():
    if not os.path.exists("pagetable.txt"):
        with open("pagetable.txt", "w", encoding="utf-8") as f:
            f.write("# Таблица страниц (страница -> кадр)\n")
            f.write("0 -> 5\n1 -> 2\n2 -> 7\n3 -> 0\n4 -> отсутствует\n")
    if not os.path.exists("refs.txt"):
        with open("refs.txt", "w", encoding="utf-8") as f:
            f.write("1200 3100 5000 0 1024 2500 3500 8192\n")


if __name__ == "__main__":
    ensure_default_files()
    pt = load_page_table("pagetable.txt")
    refs = load_refs("refs.txt")

    print(f"Размер страницы: {PAGE_SIZE} Б | Адресное пространство: {ADDRESS_SPACE} Б\n")
    for addr in refs:
        print(translate_address(addr, pt))