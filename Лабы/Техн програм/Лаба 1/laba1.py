import ast
import io
import keyword
import re
import tokenize

STYLES = {
    "snake_case": r"_*[a-z][a-z0-9_]*|_+",
    "UPPER_CASE": r"_*[A-Z][A-Z0-9_]*",
    "camelCase": r"[a-z][a-z0-9]*[A-Z][A-Za-z0-9]*",
    # Аббревиатуры в PascalCase пишутся заглавными: HTTPServer (PEP 8)
    "PascalCase": r"_?[A-Z][A-Za-z0-9]*[a-z][A-Za-z0-9]*",
}
KINDS = {"variable": "snake_case", "function": "snake_case",
         "class": "PascalCase", "constant": "UPPER_CASE"}
FUNCS = (ast.FunctionDef, ast.AsyncFunctionDef)
DEFS = (*FUNCS, ast.ClassDef)
# Бинарные операторы, вокруг которых PEP 8 требует пробелы
BINARY_OPS = {"=", "==", "!=", "<", ">", "<=", ">=", "+", "-", "*", "/",
              "//", "%", "**", "+=", "-=", "*=", "/=", "//=", "%=", "**=",
              "->", ":="}
UNARY_OPS = {"+", "-", "*", "**", "~"}


def get_style(name: str) -> str:
    """Вернуть стиль одного имени."""
    return next((s for s, p in STYLES.items() if re.fullmatch(p, name)),
                "unknown")


def tokens(code: str):
    """Токены кода (строки и комментарии — отдельные токены)."""
    return tokenize.generate_tokens(io.StringIO(code).readline)


def logical_line_starts(code: str) -> set[int] | None:
    """Номера строк, с которых начинаются логические строки кода.

    Строки-продолжения (внутри скобок) и строки многострочных литералов
    сюда не входят. Если код не токенизируется, возвращается None.
    """
    starts, new_line = set(), True
    skip = {tokenize.NL, tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT}
    try:
        for tok in tokens(code):
            if tok.type == tokenize.NEWLINE:
                new_line = True
            elif new_line and tok.type not in skip:
                starts.add(tok.start[0])
                new_line = False
    except (tokenize.TokenError, SyntaxError):
        return None
    return starts


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
    style = KINDS[kind]
    if get_style(name) == style:
        return name
    words = re.findall(r"[A-Z]+(?![a-z])|[A-Z]?[a-z0-9]+", name)
    if style == "PascalCase":
        return "".join(w.capitalize() for w in words)
    joined = "_".join(words)
    return joined.upper() if style == "UPPER_CASE" else joined.lower()


# 4
def check_indentation(code: str, indent_size: int = 4) -> list[str]:
    """Найти ошибки отступов.

    Строки-продолжения внутри скобок не проверяются на кратность:
    PEP 8 разрешает выравнивать их по открывающей скобке.
    """
    errors = []
    starts = logical_line_starts(code)
    for i, line in enumerate(code.splitlines(), 1):
        indent = line[:len(line) - len(line.lstrip())]
        if " " in indent and "\t" in indent:
            errors.append(f"Строка {i}: смешаны табы и пробелы")
        elif (line.strip() and "\t" not in indent
              and len(indent) % indent_size
              and (starts is None or i in starts)):
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
            # Относительный импорт: from . import x -> ".", from ..a -> "..a"
            res["imports"].append("." * node.level + (node.module or ""))
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = (node.targets if isinstance(node, ast.Assign)
                       else [node.target])
            res["constants"] += [t.id for t in targets
                                 if isinstance(t, ast.Name)
                                 and get_style(t.id) == "UPPER_CASE"]
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


# 10
def line_length_stats(code: str, max_length: int = 79) -> dict:
    """Статистика по длине строк."""
    lengths = [len(line) for line in code.splitlines()]
    return {
        "total_lines": len(lengths),
        "lines_over_max": sum(n > max_length for n in lengths),
        "max_line_length": max(lengths, default=0),
        "average_line_length": round(sum(lengths) / (len(lengths) or 1), 2),
    }


# 11
def check_imports_order(code: str) -> list[str]:
    """Найти импорты после определений функций/классов."""
    errors, seen_def = [], False
    for node in ast.parse(code).body:
        seen_def = seen_def or isinstance(node, DEFS)
        if seen_def and isinstance(node, (ast.Import, ast.ImportFrom)):
            errors.append(f"Строка {node.lineno}: импорт не в начале файла")
    return errors


# 12
def max_nesting_level(code: str) -> int:
    """Максимальная вложенность блоков по отступам."""
    lines = code.expandtabs(4).splitlines()
    starts = logical_line_starts(code)
    return max(((len(s) - len(s.lstrip())) // 4
                for i, s in enumerate(lines, 1)
                if s.strip() and (starts is None or i in starts)),
               default=0)


def operator_kind(tok, prev, depth: int, annotated: bool) -> str:
    """Роль токена-оператора: "binary", "unary", "kwarg" или ""."""
    if tok.type != tokenize.OP:
        return ""
    if tok.string == "=" and depth and not annotated:
        return "kwarg"  # именованный аргумент: f(a=1)
    after_operand = prev is not None and (
        prev.type in (tokenize.NUMBER, tokenize.STRING)
        or prev.type == tokenize.NAME and not keyword.iskeyword(prev.string)
        or prev.string in (")", "]", "}")
        or prev.string in ("True", "False", "None"))
    if tok.string == "~" or tok.string in UNARY_OPS and not after_operand:
        return "unary"  # унарный минус, распаковка *args, **kwargs
    return "binary" if tok.string in BINARY_OPS else ""


# 13
def fix_spaces_around_operators(line: str) -> str:
    """Добавить пробелы вокруг операторов (кроме строк и комментариев).

    Унарные операторы (-1, *args), именованные аргументы (f(a=1)) и
    числа вида 1e-5 остаются без пробелов, как требует PEP 8.
    """
    indent = line[:len(line) - len(line.lstrip())]
    code = line.strip()
    toks = []
    try:
        for tok in tokens(code):
            if tok.type in (tokenize.NEWLINE, tokenize.NL,
                            tokenize.ENDMARKER):
                break
            toks.append(tok)
    except (tokenize.TokenError, SyntaxError):
        if not toks:
            return line
    out, prev, prev_kind, pos = [], None, "", 0
    depth, annotated = 0, False
    for tok in toks:
        kind = operator_kind(tok, prev, depth, annotated)
        gap = code[pos:tok.start[1]]
        if tok.type != tokenize.COMMENT:
            if "binary" in (kind, prev_kind):
                gap = " "
            elif kind == "kwarg" or prev_kind in ("kwarg", "unary"):
                gap = ""
            elif kind == "unary" and prev.type == tokenize.NAME:
                gap = " "  # return -x, else -1
        out.append(gap + tok.string)
        if tok.string in ("(", "[", "{"):
            depth += 1
            annotated = False
        elif tok.string in (")", "]", "}"):
            depth -= 1
        elif tok.string == ",":
            annotated = False
        elif tok.string == ":" and depth:
            annotated = True  # def f(a: int = 1) — тут пробелы нужны
        prev, prev_kind, pos = tok, kind, tok.end[1]
    return indent + "".join(out) + code[pos:]


# 14
def analyze_comments(code: str) -> dict:
    """Посчитать комментарии и строки docstring."""
    comments = {t.start[0] for t in tokens(code) if t.type == tokenize.COMMENT}
    docs = sum(n.body[0].end_lineno - n.body[0].lineno + 1
               for n in ast.walk(ast.parse(code))
               if isinstance(n, (ast.Module, *DEFS)) and ast.get_docstring(n))
    total = len(code.splitlines()) or 1
    return {"total_comments": len(comments), "docstring_lines": docs,
            "comment_ratio": round(len(comments) / total, 2)}


# 15
def find_long_functions(code: str,
                        max_lines: int = 50) -> list[tuple[str, int]]:
    """Найти функции с телом длиннее max_lines."""
    found = [(n.name, n.end_lineno - n.body[0].lineno + 1)
             for n in ast.walk(ast.parse(code)) if isinstance(n, FUNCS)]
    return [f for f in found if f[1] > max_lines]


# 16
def normalize_blank_lines_between_functions(code: str) -> str:
    """Две пустые строки между функциями/классами верхнего уровня.

    Комментарий, стоящий вплотную над def/class, остаётся с ним.
    """
    out = []
    for line in code.splitlines():
        if re.match(r"@|def |class |async def ", line):
            head = len(out)  # начало блока «комментарии + определение»
            if out and out[-1].strip():
                while head and out[head - 1].startswith("#"):
                    head -= 1
            block = out[head:]
            del out[head:]
            while out and not out[-1].strip():
                out.pop()
            if out and not out[-1].startswith("@"):
                out += ["", ""]
            out += block
        out.append(line)
    return "\n".join(out) + "\n"


# 17
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


# 18
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


class MagicNumberExtractor(ast.NodeTransformer):
    """Заменяет целые числа, кроме 0 и 1, на константы VALUE_<число>."""

    def __init__(self):
        self.values = set()

    def visit_Constant(self, node):
        """Число -> имя константы (строки и bool не трогаем)."""
        value = node.value
        if type(value) is int and value > 1:
            self.values.add(value)
            return ast.copy_location(ast.Name(f"VALUE_{value}"), node)
        return node


# 19
def refactor_bad_code(code: str) -> str:
    """Улучшить плохо оформленный код (простой шаблон)."""
    tree = ast.parse(code)
    # Параметры переименовываем всегда (W -> w), прочие имена в UPPER_CASE
    # считаем константами и не трогаем
    params = {n.arg for n in ast.walk(tree) if isinstance(n, ast.arg)}
    for n in ast.walk(tree):
        if isinstance(n, DEFS):
            kind = "class" if isinstance(n, ast.ClassDef) else "function"
            n.name = to_pep8_name(n.name, kind)
            if not ast.get_docstring(n):
                # С docstring тело не пустое, поэтому pass больше не нужен
                n.body = [ast.Expr(ast.Constant("TODO: описание."))] + [
                    s for s in n.body if not isinstance(s, ast.Pass)]
        elif isinstance(n, ast.arg):
            n.arg = to_pep8_name(n.arg, "variable")
        elif isinstance(n, ast.Name) and (
                n.id in params or get_style(n.id) != "UPPER_CASE"):
            n.id = to_pep8_name(n.id, "variable")
    extractor = MagicNumberExtractor()
    tree = extractor.visit(tree)
    # Константы ставим после docstring модуля и импортов
    pos = 0
    while pos < len(tree.body) and (
            isinstance(tree.body[pos], (ast.Import, ast.ImportFrom))
            or pos == 0 and ast.get_docstring(tree)):
        pos += 1
    tree.body[pos:pos] = [
        ast.Assign([ast.Name(f"VALUE_{v}", ast.Store())], ast.Constant(v))
        for v in sorted(extractor.values)]
    # ast.unparse сам исправляет отступы и пробелы
    new = ast.unparse(ast.fix_missing_locations(tree))
    return normalize_blank_lines_between_functions(new)


# 20
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
