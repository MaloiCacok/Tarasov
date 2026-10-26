import contextlib
import io


# 1
def convert_types(data):
    """Числа -> строки, строки -> числа (если можно), остальное -> str."""
    result = []
    for item in data:
        if not isinstance(item, str):
            item = str(item)
        else:
            for kind in (int, float):
                try:
                    item = kind(item)
                    break
                except ValueError:
                    pass
        result.append(item)
    return result


# 2
def swap_values(a, b):
    """Поменять значения местами без третьей переменной."""
    a, b = b, a
    return a, b


# 3
def bool_transform(value):
    """Истинность значения без bool()."""
    if value:
        return True
    return False


# 4
def compound_operations(a, b):
    """Результаты +=, -=, *=, /=, //=, %=, **= (каждая над копией a)."""
    results = []
    x = a
    x += b
    results.append(x)
    x = a
    x -= b
    results.append(x)
    x = a
    x *= b
    results.append(x)
    x = a
    x /= b
    results.append(round(x, 2))
    x = a
    x //= b
    results.append(x)
    x = a
    x %= b
    results.append(x)
    x = a
    x **= b
    results.append(x)
    return results


# 5
def check_type(value, expected_type):
    """Проверить, совпадает ли имя типа value с expected_type."""
    return type(value).__name__ == expected_type


# 6
def logical_and(a, b, c):
    """True, если все три аргумента истинны (без and)."""
    if a:
        if b:
            if c:
                return True
    return False


# 7
def logical_or(a, b, c):
    """True, если хотя бы один аргумент истинный (без or)."""
    if a:
        return True
    if b:
        return True
    if c:
        return True
    return False


# 8
def is_between(value, low, high):
    """Проверить low <= value <= high одним составным условием."""
    if value >= low and value <= high:
        return True
    return False


# 9
def print_even_numbers(n):
    """Вывести чётные числа от 1 до n."""
    for i in range(2, n + 1, 2):
        print(i)


# 10
def countdown_while(n):
    """Вывести числа от n до 1 циклом while."""
    while n >= 1:
        print(n)
        n -= 1


# 11
def skip_multiples(n, multiple):
    """Вывести числа от 1 до n, пропуская кратные multiple."""
    for i in range(1, n + 1):
        if i % multiple == 0:
            continue
        print(i)


# 12
def if_elif_else_chain(x):
    """Знак числа словом."""
    if x > 0:
        return "positive"
    elif x < 0:
        return "negative"
    else:
        return "zero"


# 13
def abs_value(x):
    """Модуль числа без abs()."""
    if x < 0:
        return -x
    return x


# 14
def binary_representation(n):
    """Двоичная запись числа без bin()."""
    if n < 0:
        return "-" + binary_representation(-n)
    digits = ""
    while n > 0:
        digits = str(n % 2) + digits
        n //= 2
    return digits or "0"


# 15
def custom_round(number, ndigits):
    """Округление без round()."""
    factor = 10 ** ndigits
    return int(number * factor + (0.5 if number >= 0 else -0.5)) / factor


# 16
def find_max_min(numbers):
    """Максимум и минимум списка без max() и min()."""
    if not numbers:
        raise ValueError("find_max_min() получила пустой список")
    high = low = numbers[0]
    for x in numbers:
        high = x if x > high else high
        low = x if x < low else low
    return high, low


# 17
def all_true(iterable):
    """Аналог all()."""
    for item in iterable:
        if not item:
            return False
    return True


# 18
def any_true(iterable):
    """Аналог any()."""
    for item in iterable:
        if item:
            return True
    return False


# 19
def custom_enumerate(sequence, start=0):
    """Аналог enumerate()."""
    result = []
    index = start
    for item in sequence:
        result.append((index, item))
        index += 1
    return result


# 20
def custom_filter(func, iterable):
    """Аналог filter()."""
    return [item for item in iterable if func(item)]


# 21
def custom_map(func, iterable):
    """Аналог map()."""
    return [func(item) for item in iterable]


# 22
def custom_zip(list1, list2):
    """Аналог zip() для двух списков."""
    return [(list1[i], list2[i]) for i in range(min(len(list1), len(list2)))]


# 23
def custom_reversed(sequence):
    """Развернуть список без reversed() и [::-1]."""
    return [sequence[i] for i in range(len(sequence) - 1, -1, -1)]


# 24
def custom_sorted(iterable, reverse=False):
    """Сортировка пузырьком без sorted() и .sort()."""
    items = list(iterable)
    for i in range(len(items)):
        for j in range(len(items) - 1 - i):
            if (items[j] > items[j + 1]) != reverse:
                items[j], items[j + 1] = items[j + 1], items[j]
    return items


# 25
def sum_digits(n):
    """Сумма цифр числа циклом while."""
    if n < 0:
        n = -n
    total = 0
    while n > 0:
        total += n % 10
        n //= 10
    return total


# 26
def count_vowels(text):
    """Количество гласных без учёта регистра."""
    return len([char for char in text if char in "aeiouAEIOU"])


# 27
def power(base, exp):
    """Возведение в целую степень без ** и pow()."""
    result = 1
    for _ in range(exp if exp >= 0 else -exp):
        result *= base
    return result if exp >= 0 else 1 / result


# 28
def is_prime(n):
    """Проверка числа на простоту (делители от 2 до sqrt(n))."""
    if n < 2:
        return False
    for d in range(2, int(n ** 0.5) + 1):
        if n % d == 0:
            return False
    return True


# 29
def factorial(n):
    """Факториал циклом for."""
    if n < 0:
        raise ValueError("факториал определён только для n >= 0")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


# 30
def fibonacci(n):
    """n-е число Фибоначчи циклом for."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


TESTS = [
    ('convert_types([1, "2", "hello", 3.5])', ["1", 2, "hello", "3.5"]),
    ("swap_values(5, 10)", (10, 5)),
    ("bool_transform(5), bool_transform(0)", (True, False)),
    ("compound_operations(10, 3)", [13, 7, 30, 3.33, 3, 1, 1000]),
    ('check_type(5, "int"), check_type("5", "int")', (True, False)),
    ('logical_and(True, 5, "x"), logical_and(True, 0, "x")', (True, False)),
    ('logical_or(0, "", False), logical_or(0, 5, False)', (False, True)),
    ("is_between(5, 1, 10), is_between(15, 1, 10)", (True, False)),
    ("print_even_numbers(10)", "2 4 6 8 10"),
    ("countdown_while(5)", "5 4 3 2 1"),
    ("skip_multiples(10, 3)", "1 2 4 5 7 8 10"),
    ("if_elif_else_chain(5), if_elif_else_chain(-3), if_elif_else_chain(0)",
     ("positive", "negative", "zero")),
    ("abs_value(-5), abs_value(3)", (5, 3)),
    ("binary_representation(10), binary_representation(0)", ("1010", "0")),
    ("custom_round(3.14159, 2), custom_round(2.5, 0)", (3.14, 3.0)),
    ("find_max_min([3, 7, 1, 9, 2])", (9, 1)),
    ("all_true([1, 2, 3]), all_true([1, 0, 3])", (True, False)),
    ('any_true([0, "", False]), any_true([0, 5, False])', (False, True)),
    ('custom_enumerate(["a", "b", "c"], start=1)',
     [(1, "a"), (2, "b"), (3, "c")]),
    ("custom_filter(lambda x: x % 2 == 0, [1, 2, 3, 4, 5])", [2, 4]),
    ("custom_map(lambda x: x * 2, [1, 2, 3])", [2, 4, 6]),
    ('custom_zip([1, 2, 3], ["a", "b", "c"])', [(1, "a"), (2, "b"), (3, "c")]),
    ("custom_reversed([1, 2, 3, 4])", [4, 3, 2, 1]),
    ("custom_sorted([3, 1, 4, 1, 5]), custom_sorted([3, 1, 4], reverse=True)",
     ([1, 1, 3, 4, 5], [4, 3, 1])),
    ("sum_digits(1234), sum_digits(99)", (10, 18)),
    ('count_vowels("Hello World"), count_vowels("Python")', (3, 1)),
    ("power(2, 5), power(3, 3)", (32, 27)),
    ("is_prime(17), is_prime(18)", (True, False)),
    ("factorial(5), factorial(0)", (120, 1)),
    ("fibonacci(10), fibonacci(0), fibonacci(1)", (55, 0, 1)),
]


def main():
    """Сравнить результат каждой функции с ожидаемым из задания."""
    for number, (call, expected) in enumerate(TESTS, 1):
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            result = eval(call)
        if result is None:
            result = " ".join(printed.getvalue().split())
        status = "OK" if result == expected else "ОШИБКА"
        print(f"Задача {number}: {call}\n"
              f"  ожидается: {expected}\n"
              f"  получено:  {result}  [{status}]\n")


if __name__ == "__main__":
    main()
