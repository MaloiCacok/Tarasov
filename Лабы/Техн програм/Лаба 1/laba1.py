"""Практическая работа: инструменты проверки стиля кода по PEP 8."""
import ast
import io
import keyword
import re
import tokenize

STYLES = {
    "snake_case": r"[a-z_][a-z0-9_]*",
    "UPPER_CASE": r"[A-Z_][A-Z0-9_]*",
    "camelCase": r"[a-z][a-z0-9]*(?:[A-Z][a-z0-9]*)+",
    "PascalCase": r"[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]*)*",
}
KINDS = {"variable": "snake_case", "function": "snake_case",
         "class": "PascalCase", "constant": "UPPER_CASE"}
FUNCS = (ast.FunctionDef, ast.AsyncFunctionDef)
DEFS = (*FUNCS, ast.ClassDef)


def get_style(name: str) -> str:
    """Вернуть стиль одного имени."""
    return next((s for s, p in STYLES.items() if re.fullmatch(p, name)),
                "unknown")


def tokens(code: str):
    """Токены кода (строки и комментарии — отдельные токены)."""
    return tokenize.generate_tokens(io.StringIO(code).readline)


# 1
def check_naming_style(names: list[str]) -> dict[str, str]:
    """Определить стиль каждого имени."""
    return {name: get_style(name) for name in names}


# 2
def is_valid_python_identifier(name: str, kind: str) -> bool:
    """Проверить, соответствует ли имя PEP 8 для данного вида."""
    return (name.isidentifier() and not keyword.iskeyword(name)
            and get_style(name) == KINDS[kind])


# 3
def to_pep8_name(name: str, kind: str) -> str:
    """Преобразовать имя к стилю PEP 8."""
    words = re.findall(r"[A-Z]+(?![a-z])|[A-Z]?[a-z0-9]+", name)
    style = KINDS[kind]
    if style == "PascalCase":
        return "".join(w.capitalize() for w in words)
    joined = "_".join(words)
    return joined.upper() if style == "UPPER_CASE" else joined.lower()


# 4
def check_indentation(code: str, indent_size: int = 4) -> list[str]:
    """Найти ошибки отступов."""
    errors = []
    for i, line in enumerate(code.splitlines(), 1):
        indent = line[:len(line) - len(line.lstrip())]
        if " " in indent and "\t" in indent:
            errors.append(f"Строка {i}: смешаны табы и пробелы")
        elif line.strip() and len(indent) % indent_size and "\t" not in indent:
            errors.append(f"Строка {i}: отступ не кратен {indent_size}")
    return errors


# 5
def find_magic_numbers(code: str) -> list[tuple[int, int]]:
    """Найти целые числа, кроме 0, 1, -1 (не в строках и комментариях)."""
    return [(t.start[0], int(t.string, 0)) for t in tokens(code)
            if t.type == tokenize.NUMBER
            and re.fullmatch(r"[\d_]+|0[xob]\w+", t.string, re.I)
            and int(t.string, 0) > 1]


# 6
def extract_module_structure(code: str) -> dict:
    """Получить импорты, константы, функции и классы модуля."""
    res = {"imports": [], "constants": [], "functions": [], "classes": []}
    for node in ast.parse(code).body:
        if isinstance(node, ast.Import):
            res["imports"] += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            res["imports"].append(node.module)
        elif isinstance(node, ast.Assign):
            res["constants"] += [t.id for t in node.targets
                                 if isinstance(t, ast.Name) and t.id.isupper()]
        elif isinstance(node, ast.ClassDef):
            res["classes"].append(node.name)
        elif isinstance(node, FUNCS):
            res["functions"].append(node.name)
    return res


# 7
def check_docstrings(code: str) -> dict[str, bool]:
    """Проверить наличие docstring у функций и классов."""
    return {n.name: ast.get_docstring(n) is not None
            for n in ast.walk(ast.parse(code)) if isinstance(n, DEFS)}


# 8
def generate_module_template(module_name: str, functions: list[str],
                             classes: list[str]) -> str:
    """Сгенерировать шаблон модуля."""
    body = ':\n    """TODO: описание."""\n    pass'
    parts = [f'# Модуль {module_name}\nimport typing\n\n__version__ = "0.1.0"']
    parts += [f"def {f}(){body}" for f in functions]
    parts += [f"class {c}{body}" for c in classes]
    return "\n\n\n".join(parts) + "\n"


# 9
def add_main_guard(code: str, main_function: str = "main") -> str:
    """Добавить if __name__ == "__main__", если его нет."""
    if re.search(r"if\s+__name__\s*==\s*['\"]__main__['\"]", code):
        return code
    return (code.rstrip() + '\n\n\nif __name__ == "__main__":\n'
            f"    {main_function}()\n")


# 10 (в Word — 11)
def line_length_stats(code: str, max_length: int = 79) -> dict:
    """Статистика по длине строк."""
    lengths = [len(line) for line in code.splitlines()]
    return {
        "total_lines": len(lengths),
        "lines_over_max": sum(n > max_length for n in lengths),
        "max_line_length": max(lengths, default=0),
        "average_line_length": round(sum(lengths) / (len(lengths) or 1), 2),
    }


# 11 (в Word — 12)
def check_imports_order(code: str) -> list[str]:
    """Найти импорты после определений функций/классов."""
    errors, seen_def = [], False
    for node in ast.parse(code).body:
        seen_def = seen_def or isinstance(node, DEFS)
        if seen_def and isinstance(node, (ast.Import, ast.ImportFrom)):
            errors.append(f"Строка {node.lineno}: импорт не в начале файла")
    return errors


# 12 (в Word — 13)
def max_nesting_level(code: str) -> int:
    """Максимальная вложенность блоков по отступам."""
    return max(((len(s) - len(s.lstrip())) // 4
                for s in code.expandtabs(4).splitlines() if s.strip()),
               default=0)


# 13 (в Word — 14)
def fix_spaces_around_operators(line: str) -> str:
    """Добавить пробелы вокруг операторов (кроме строк и комментариев)."""
    indent = line[:len(line) - len(line.lstrip())]
    parts = re.split(r"""("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|#.*)""",
                     line.strip())
    op = r"\s*(==|!=|<=|>=|[+\-*/%]=|//|[=<>+\-*/%])\s*"
    for i in range(0, len(parts), 2):  # чётные части — код
        parts[i] = re.sub(op, r" \1 ", parts[i])
    return indent + "".join(parts).strip()


# 14 (в Word — 15)
def analyze_comments(code: str) -> dict:
    """Посчитать комментарии и строки docstring."""
    comments = {t.start[0] for t in tokens(code) if t.type == tokenize.COMMENT}
    docs = sum(n.body[0].end_lineno - n.body[0].lineno + 1
               for n in ast.walk(ast.parse(code))
               if isinstance(n, (ast.Module, *DEFS)) and ast.get_docstring(n))
    total = len(code.splitlines()) or 1
    return {"total_comments": len(comments), "docstring_lines": docs,
            "comment_ratio": round(len(comments) / total, 2)}


# 15 (в Word — 16)
def find_long_functions(code: str,
                        max_lines: int = 50) -> list[tuple[str, int]]:
    """Найти функции с телом длиннее max_lines."""
    found = [(n.name, n.end_lineno - n.body[0].lineno + 1)
             for n in ast.walk(ast.parse(code)) if isinstance(n, FUNCS)]
    return [f for f in found if f[1] > max_lines]


# 16 (в Word — 17)
def normalize_blank_lines_between_functions(code: str) -> str:
    """Две пустые строки между функциями/классами верхнего уровня."""
    out = []
    for line in code.splitlines():
        if re.match(r"@|def |class |async def ", line):
            while out and not out[-1].strip():
                out.pop()
            if out and not out[-1].startswith("@"):
                out += ["", ""]
        out.append(line)
    return "\n".join(out) + "\n"


# 17 (в Word — 18)
def simple_linter(code: str) -> list[str]:
    """Комплексная проверка стиля."""
    msgs = [(int(m.split()[1][:-1]), m) for m in check_indentation(code)]
    msgs += [(i, f"Строка {i}: длина больше 79")
             for i, s in enumerate(code.splitlines(), 1) if len(s) > 79]
    msgs += [(i, f"Строка {i}: магическое число {v}")
             for i, v in find_magic_numbers(code)]
    for n in ast.walk(ast.parse(code)):
        if isinstance(n, FUNCS) and not ast.get_docstring(n):
            msgs.append((n.lineno, f"Строка {n.lineno}: нет docstring"))
        if isinstance(n, FUNCS) and get_style(n.name) != "snake_case":
            msgs.append((n.lineno, f"Строка {n.lineno}: не snake_case"))
    return [m for _, m in sorted(msgs)]


def coverage(code: str) -> float:
    """Процент функций/классов с docstring."""
    docs = check_docstrings(code)
    return round(100 * sum(docs.values()) / len(docs), 1) if docs else 100.0


# 18 (в Word — 19)
def style_report(code: str, module_name: str) -> str:
    """Текстовый отчёт о стиле модуля."""
    struct = extract_module_structure(code)
    return (f"Module: {module_name}\n"
            f"Total lines: {line_length_stats(code)['total_lines']}\n"
            f"Functions: {len(struct['functions'])}\n"
            f"Classes: {len(struct['classes'])}\n"
            f"Docstring coverage: {coverage(code)}%\n"
            f"Lines over 79 chars: {line_length_stats(code)['lines_over_max']}"
            f"\nMagic numbers found: {len(find_magic_numbers(code))}")


# 19 (в Word — 26)
def refactor_bad_code(code: str) -> str:
    """Улучшить плохо оформленный код (простой шаблон)."""
    tree = ast.parse(code)
    for n in ast.walk(tree):
        if isinstance(n, FUNCS):
            n.name = to_pep8_name(n.name, "function")
            if not ast.get_docstring(n):
                n.body.insert(0, ast.Expr(ast.Constant("TODO: описание.")))
        elif isinstance(n, ast.arg):
            n.arg = to_pep8_name(n.arg, "variable")
        elif isinstance(n, ast.Name):
            n.id = to_pep8_name(n.id, "variable")
    new = ast.unparse(tree)  # ast.unparse сам исправляет отступы и пробелы
    nums = sorted({v for _, v in find_magic_numbers(new)})
    new = re.sub(r"\b\d+\b", lambda m: "VALUE_" * (int(m[0]) > 1) + m[0], new)
    consts = "".join(f"VALUE_{v} = {v}\n" for v in nums)
    return normalize_blank_lines_between_functions(consts + new)


# 20 (в Word — 27)
def compare_module_versions(old_code: str, new_code: str) -> dict:
    """Сравнить две версии модуля."""
    old = extract_module_structure(old_code)
    new = extract_module_structure(new_code)
    return {
        "added_functions": sorted({*new["functions"]} - {*old["functions"]}),
        "removed_functions": sorted({*old["functions"]} - {*new["functions"]}),
        "added_classes": sorted({*new["classes"]} - {*old["classes"]}),
        "removed_classes": sorted({*old["classes"]} - {*new["classes"]}),
        "docstring_coverage_old": coverage(old_code),
        "docstring_coverage_new": coverage(new_code),
    }


BAD = "def AreaIfLarge(W,H):\n  if W*H>100:\n      return W*H\n  return 0\n"
SAMPLE = '''"""Пример модуля."""
import os
from re import sub

SIZE = 42  # размер


def good_func():
    """Есть docstring."""
    for i in range(10):
        if i > 5:
            print(i)


def BadFunc():
    return 7


class User:
    pass
'''


def main() -> None:
    """Демонстрация работы всех функций."""
    results = {
        "Стиль имён": check_naming_style(
            ["user_name", "userName", "UserName", "MAX_SIZE", "user-name"]),
        "UserName подходит для класса?":
            is_valid_python_identifier("UserName", "class"),
        "UserName -> имя переменной": to_pep8_name("UserName", "variable"),
        "Ошибки отступов в BAD": check_indentation(BAD),
        "Магические числа в SAMPLE (строка, число)":
            find_magic_numbers(SAMPLE),
        "Структура SAMPLE": extract_module_structure(SAMPLE),
        "Наличие docstring в SAMPLE": check_docstrings(SAMPLE),
        "Шаблон модуля": generate_module_template("demo", ["run"], ["App"]),
        "Добавление main-guard": add_main_guard("def main():\n    pass"),
        "Длина строк SAMPLE": line_length_stats(SAMPLE),
        "Порядок импортов": check_imports_order(
            "import os\n\ndef f():\n    pass\nimport re"),
        "Максимальная вложенность SAMPLE": max_nesting_level(SAMPLE),
        "Пробелы: x=a+b  # a=b": fix_spaces_around_operators("x=a+b  # a=b"),
        "Комментарии SAMPLE": analyze_comments(SAMPLE),
        "Функции BAD длиннее 2 строк": find_long_functions(BAD, 2),
        "Пустые строки между функциями":
            normalize_blank_lines_between_functions(
                "def a():\n    pass\ndef b():\n    pass"),
        "Мини-линтер SAMPLE": simple_linter(SAMPLE),
        "Отчёт о стиле": style_report(SAMPLE, "sample.py"),
        "Рефакторинг BAD": refactor_bad_code(BAD),
        "Сравнение BAD и исправленной версии":
            compare_module_versions(BAD, refactor_bad_code(BAD)),
    }
    print("SAMPLE:\n" + SAMPLE + "\nBAD:\n" + BAD)
    for number, (title, result) in enumerate(results.items(), 1):
        print(f"\n{'=' * 60}\n{number}. {title}\n{'-' * 60}")
        if isinstance(result, dict):
            result = "\n".join(f"  {k}: {v}" for k, v in result.items())
        elif isinstance(result, list):
            result = "\n".join(f"  - {item}" for item in result) or "  —"
        print(str(result).rstrip())


if __name__ == "__main__":
    main()
