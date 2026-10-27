EMPTY = None
# 2.1
def pair(head, tail):
    return lambda selector: selector(head, tail)


def head(lst):
    return lst(lambda h, t: h)


def tail(lst):
    return lst(lambda h, t: t)


lst = pair(1, pair(2, pair(3, EMPTY)))
print("2.1  head:", head(lst), "| head(tail):", head(tail(lst)))


# 2.2
def make_list(*args):
    return EMPTY if not args else pair(args[0], make_list(*args[1:]))


lst = make_list(1, 2, 3, 4, 5)
print("2.2  make_list(1, 2, 3, 4, 5): готово, head =", head(lst))


# 2.3
def list_to_string(lst):
    def items(node):
        if node is EMPTY:
            return ""
        rest = items(tail(node))
        return str(head(node)) + (", " + rest if rest else "")
    return "[" + items(lst) + "]"


print("2.3  list_to_string:", list_to_string(lst))


# 2.4
def list_range(low, high):
    return EMPTY if low > high else pair(low, list_range(low + 1, high))


print("2.4  list_range(3, 8):", list_to_string(list_range(3, 8)))


# 2.5
def foldl(func, lst, acc):
    return acc if lst is EMPTY else foldl(func, tail(lst), func(acc, head(lst)))


print("2.5  foldl(-, [1..5], 0):", foldl(lambda a, x: a - x, lst, 0))


# 2.6
def list_sum(lst):
    return foldl(lambda acc, x: acc + x, lst, 0)


print("2.6  list_sum:", list_sum(lst))


# 2.7
def fact(n):
    return foldl(lambda acc, x: acc * x, list_range(1, n), 1)


print("2.7  fact(5):", fact(5), "| fact(0):", fact(0))


# 2.8
def list_to_py(lst):
    return foldl(lambda acc, x: acc + [x], lst, [])


print("2.8  list_to_py:", list_to_py(lst))


# 2.9
def list_reverse(lst):
    return foldl(lambda acc, x: pair(x, acc), lst, EMPTY)


print("2.9  list_reverse:", list_to_string(list_reverse(lst)))


# 2.10
def foldr(func, lst, acc):
    return acc if lst is EMPTY else func(head(lst), foldr(func, tail(lst), acc))


print("2.10 foldr(-, [1..5], 0):", foldr(lambda x, a: x - a, lst, 0))


# 2.11
def list_map(func, lst):
    return foldr(lambda x, acc: pair(func(x), acc), lst, EMPTY)


print("2.11 list_map(x*10):", list_to_string(list_map(lambda x: x * 10, lst)))


# 2.12
def list_filter(pred, lst):
    return foldr(lambda x, acc: pair(x, acc) if pred(x) else acc, lst, EMPTY)


print("2.12 list_filter(чётные):",
      list_to_string(list_filter(lambda x: x % 2 == 0, lst)))


# 2.13
def sum_odd_squares(lst):
    return list_sum(list_map(lambda x: x * x,
                             list_filter(lambda x: x % 2 == 1, lst)))


print("2.13 sum_odd_squares:", sum_odd_squares(lst))
