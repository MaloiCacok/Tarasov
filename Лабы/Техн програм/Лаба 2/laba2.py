# 1
def convert_types(data):
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


print("Задача 1")
print(convert_types([1, "2", "hello", 3.5]))


# 2
def swap_values(a, b):
    a, b = b, a
    return a, b


print("\nЗадача 2")
print(swap_values(5, 10))


# 3
def bool_transform(value):
    if value:
        return True
    return False


print("\nЗадача 3")
print(bool_transform(5), bool_transform(0))


# 4
def compound_operations(a, b):
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


print("\nЗадача 4")
print(compound_operations(10, 3))


# 5
def check_type(value, expected_type):
    return type(value).__name__ == expected_type


print("\nЗадача 5")
print(check_type(5, "int"), check_type("5", "int"))


# 6
def logical_and(a, b, c):
    if a:
        if b:
            if c:
                return True
    return False


print("\nЗадача 6")
print(logical_and(True, 5, "x"), logical_and(True, 0, "x"))


# 7
def logical_or(a, b, c):
    if a:
        return True
    if b:
        return True
    if c:
        return True
    return False


print("\nЗадача 7")
print(logical_or(0, "", False), logical_or(0, 5, False))


# 8
def is_between(value, low, high):
    if value >= low and value <= high:
        return True
    return False


print("\nЗадача 8")
print(is_between(5, 1, 10), is_between(15, 1, 10))


# 9
def print_even_numbers(n):
    for i in range(2, n + 1, 2):
        print(i)


print("\nЗадача 9")
print_even_numbers(10)


# 10
def countdown_while(n):
    while n >= 1:
        print(n)
        n -= 1


print("\nЗадача 10")
countdown_while(5)


# 11
def skip_multiples(n, multiple):
    for i in range(1, n + 1):
        if i % multiple == 0:
            continue
        print(i)


print("\nЗадача 11")
skip_multiples(10, 3)


# 12
def if_elif_else_chain(x):
    if x > 0:
        return "positive"
    elif x < 0:
        return "negative"
    else:
        return "zero"


print("\nЗадача 12")
print(if_elif_else_chain(5), if_elif_else_chain(-3), if_elif_else_chain(0))


# 13
def abs_value(x):
    if x < 0:
        return -x
    return x


print("\nЗадача 13")
print(abs_value(-5), abs_value(3))


# 14
def binary_representation(n):
    if n < 0:
        return "-" + binary_representation(-n)
    digits = ""
    while n > 0:
        digits = str(n % 2) + digits
        n //= 2
    return digits or "0"


print("\nЗадача 14")
print(binary_representation(10), binary_representation(0))


# 15
def custom_round(number, ndigits):
    factor = 10 ** ndigits
    return int(number * factor + (0.5 if number >= 0 else -0.5)) / factor


print("\nЗадача 15")
print(custom_round(3.14159, 2), custom_round(2.5, 0))


# 16
def find_max_min(numbers):
    if not numbers:
        raise ValueError("find_max_min() получила пустой список")
    high = low = numbers[0]
    for x in numbers:
        high = x if x > high else high
        low = x if x < low else low
    return high, low


print("\nЗадача 16")
print(find_max_min([3, 7, 1, 9, 2]))


# 17
def all_true(iterable):
    for item in iterable:
        if not item:
            return False
    return True


print("\nЗадача 17")
print(all_true([1, 2, 3]), all_true([1, 0, 3]))


# 18
def any_true(iterable):
    for item in iterable:
        if item:
            return True
    return False


print("\nЗадача 18")
print(any_true([0, "", False]), any_true([0, 5, False]))


# 19
def custom_enumerate(sequence, start=0):
    result = []
    index = start
    for item in sequence:
        result.append((index, item))
        index += 1
    return result


print("\nЗадача 19")
print(custom_enumerate(["a", "b", "c"], start=1))


# 20
def custom_filter(func, iterable):
    return [item for item in iterable if func(item)]


print("\nЗадача 20")
print(custom_filter(lambda x: x % 2 == 0, [1, 2, 3, 4, 5]))


# 21
def custom_map(func, iterable):
    return [func(item) for item in iterable]


print("\nЗадача 21")
print(custom_map(lambda x: x * 2, [1, 2, 3]))


# 22
def custom_zip(list1, list2):
    return [(list1[i], list2[i]) for i in range(min(len(list1), len(list2)))]


print("\nЗадача 22")
print(custom_zip([1, 2, 3], ["a", "b", "c"]))


# 23
def custom_reversed(sequence):
    return [sequence[i] for i in range(len(sequence) - 1, -1, -1)]


print("\nЗадача 23")
print(custom_reversed([1, 2, 3, 4]))


# 24
def custom_sorted(iterable, reverse=False):
    items = list(iterable)
    for i in range(len(items)):
        for j in range(len(items) - 1 - i):
            if (items[j] > items[j + 1]) != reverse:
                items[j], items[j + 1] = items[j + 1], items[j]
    return items


print("\nЗадача 24")
print(custom_sorted([3, 1, 4, 1, 5]), custom_sorted([3, 1, 4], reverse=True))


# 25
def sum_digits(n):
    if n < 0:
        n = -n
    total = 0
    while n > 0:
        total += n % 10
        n //= 10
    return total


print("\nЗадача 25")
print(sum_digits(1234), sum_digits(99))


# 26
def count_vowels(text):
    return len([char for char in text if char in "aeiouAEIOU"])


print("\nЗадача 26")
print(count_vowels("Hello World"), count_vowels("Python"))


# 27
def power(base, exp):
    result = 1
    for _ in range(exp if exp >= 0 else -exp):
        result *= base
    return result if exp >= 0 else 1 / result


print("\nЗадача 27")
print(power(2, 5), power(3, 3))


# 28
def is_prime(n):
    if n < 2:
        return False
    for d in range(2, int(n ** 0.5) + 1):
        if n % d == 0:
            return False
    return True


print("\nЗадача 28")
print(is_prime(17), is_prime(18))


# 29
def factorial(n):
    if n < 0:
        raise ValueError("факториал определён только для n >= 0")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


print("\nЗадача 29")
print(factorial(5), factorial(0))


# 30
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


print("\nЗадача 30")
print(fibonacci(10), fibonacci(0), fibonacci(1))
