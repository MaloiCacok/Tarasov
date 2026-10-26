import contextlib
import hashlib
import io
import random


def sha256(text):
    """Задание 4: SHA-256-хэш строки."""
    return hashlib.sha256(text.encode()).hexdigest()


# 1
def transactions_per_hour(networks):
    """Транзакций за час для каждой сети и сеть-лидер."""
    per_hour = {name: tps * 3600 for name, tps in networks.items()}
    return per_hour, max(per_hour, key=per_hour.get)


def task_1():
    """Задание 1: вывести транзакции за час и сеть-лидера."""
    networks = {"Ethereum": 30, "Binance Smart Chain": 160, "Solana": 50_000}
    per_hour, leader = transactions_per_hour(networks)
    for name, count in per_hour.items():
        print(f"{name}: {count:,} транзакций/час")
    print(f"Лидер: {leader}")


# 2
def read_range(writes):
    """Минимум и максимум операций чтения в секунду."""
    return writes * 100, writes * 10_000


def task_2():
    """Задание 2: вывести диапазон операций чтения."""
    low, high = read_range(500)
    print(f"Записей в секунду: 500\nМинимум чтений/с: {low:,}\n"
          f"Максимум чтений/с: {high:,}")


# 3
class Block:
    """Блок цепочки: индекс, данные, хэш предыдущего блока."""

    def __init__(self, index, data, prev_hash):
        self.index, self.data, self.prev_hash = index, data, prev_hash
        self.hash = self.calc_hash()

    def calc_hash(self):
        """SHA-256 от index + data + prev_hash."""
        return sha256(f"{self.index}{self.data}{self.prev_hash}")


def task_3():
    """Задание 3: собрать и вывести цепочку из трёх блоков."""
    chain = [Block(0, "Genesis", "0")]
    for i in (1, 2):
        chain.append(Block(i, f"Транзакция {i}", chain[-1].hash))
    for b in chain:
        print(f"Блок {b.index}: hash={b.hash[:16]}... "
              f"prev={b.prev_hash[:16]}...")


# 4
def task_4():
    """Задание 4: вывести SHA-256 строки "blockchain"."""
    print(f"SHA-256('blockchain') =\n{sha256('blockchain')}")


# 5
def mine(data, difficulty):
    """Подобрать nonce, при котором хэш начинается с difficulty нулей."""
    prefix = "0" * difficulty
    nonce = 0
    h = sha256(data + str(nonce))
    while not h.startswith(prefix):
        nonce += 1
        h = sha256(data + str(nonce))
    return nonce, h


def task_5():
    """Задание 5: найти nonce для сложности 4."""
    nonce, block_hash = mine("block1", 4)
    print(f"difficulty=4, nonce={nonce}\nhash={block_hash}")


# 6
def merkle_root(transactions):
    """Корень дерева Меркла."""
    level = [sha256(tx) for tx in transactions]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [sha256(level[i] + level[i + 1])
                 for i in range(0, len(level), 2)]
    return level[0]


def task_6():
    """Задание 6: вывести корень дерева Меркла."""
    print(f"Merkle root: {merkle_root(['tx1', 'tx2', 'tx3', 'tx4'])}")


# 7
def is_attack_threat(share):
    """Угроза атаки 51%, если доля мощности больше половины."""
    return share > 0.5


def task_7():
    """Задание 7: проверить доли мощности на угрозу атаки 51%."""
    for p in (0.3, 0.51, 0.49, 0.6):
        verdict = "УГРОЗА (атака 51%)" if is_attack_threat(p) else "безопасно"
        print(f"Доля мощности {p:.0%}: {verdict}")


# 8
def build_tangle(count):
    """Каждая транзакция (кроме двух первых) подтверждает две предыдущие."""
    random.seed(42)
    return [[] if i < 2 else random.sample(range(i), 2) for i in range(count)]


def task_8():
    """Задание 8: вывести структуру подтверждений Tangle."""
    for i, links in enumerate(build_tangle(6)):
        print(f"Транзакция {i} подтверждает: {links or '— (начальная)'}")


# 9
def confirmation_time(n, k=1000):
    """Время подтверждения t = k / n."""
    return k / n


def task_9():
    """Задание 9: вывести время подтверждения в IOTA."""
    for n in (10, 100, 1000):
        print(f"n={n:>4} транзакций -> время подтверждения = "
              f"{confirmation_time(n):.2f} усл.ед.")


# 10
def index_address(transactions, addr):
    """Транзакции адреса и его баланс (входящие минус исходящие)."""
    own = [t for t in transactions if addr in (t["from"], t["to"])]
    incoming = sum(t["amount"] for t in own if t["to"] == addr)
    outgoing = sum(t["amount"] for t in own if t["from"] == addr)
    return own, incoming - outgoing


def task_10():
    """Задание 10: вывести транзакции и баланс Alice."""
    txs = [{"from": "Alice", "to": "Bob", "amount": 50},
           {"from": "Bob", "to": "Alice", "amount": 20},
           {"from": "Bob", "to": "Carol", "amount": 30},
           {"from": "Alice", "to": "Carol", "amount": 10}]
    own, balance = index_address(txs, "Alice")
    print(f"Транзакции Alice ({len(own)}):")
    for t in own:
        print(f"  {t['from']} -> {t['to']}: {t['amount']}")
    print(f"Баланс Alice: {balance}")


# 11
def subgraph_stats(log):
    """Сумма запросов по сабграфам, самый нагруженный и общее число."""
    totals = {}
    for subgraph, count in log:
        totals[subgraph] = totals.get(subgraph, 0) + count
    return totals, max(totals, key=totals.get), sum(totals.values())


def task_11():
    """Задание 11: вывести статистику запросов по сабграфам."""
    log = [("uniswap", 5000), ("aave", 3000), ("uniswap", 7500),
           ("compound", 4500), ("aave", 5500)]
    totals, busiest, total = subgraph_stats(log)
    for name, count in totals.items():
        print(f"{name}: {count:,} запросов")
    print(f"Самый нагруженный: {busiest}\nВсего запросов: {total:,}")


# 12
def sign(message, private_key):
    """Учебная подпись: SHA-256 от сообщения и ключа."""
    return sha256(message + private_key)


def verify(message, signature, private_key):
    """Проверить подпись, вычислив её заново."""
    return sign(message, private_key) == signature


def task_12():
    """Задание 12: подписать сообщение и проверить подпись."""
    message, key = "Alice -> Bob: 10 BTC", "secret_key"
    signature = sign(message, key)
    print(f"Подпись: {signature[:24]} ...\n"
          f"Проверка верной подписи: {verify(message, signature, key)}\n"
          "Проверка при подмене сообщения: "
          f"{verify('Alice -> Bob: 1000 BTC', signature, key)}")


# 13
def quantum_states(n):
    """Число состояний n кубитов."""
    return 2 ** n


def task_13():
    """Задание 13: сравнить число квантовых и классических состояний."""
    for n in (1, 2, 8, 127):
        print(f"{n:>3} кубит(ов): {quantum_states(n):,} состояний "
              f"одновременно | классика: {n} состояний")


# 14
def factorize(n):
    """Разложение числа на простые множители."""
    factors, d = [], 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    return factors + [n] if n > 1 else factors


def task_14():
    """Задание 14: разложить 15, 21 и 91 на простые множители."""
    for n in (15, 21, 91):
        print(f"{n} = {' x '.join(map(str, factorize(n)))}")


# 15
def forecast_qubits(generations):
    """Коэффициенты роста, средний темп и прогноз следующего поколения."""
    rates = [b / a for a, b in zip(generations, generations[1:])]
    average = sum(rates) / len(rates)
    return rates, average, round(generations[-1] * average)


def task_15():
    """Задание 15: вывести прогноз роста числа кубитов."""
    generations = [127, 433, 1121]
    rates, average, forecast = forecast_qubits(generations)
    print(f"Поколения кубитов: {generations}\n"
          f"Коэффициенты роста: {[round(r, 2) for r in rates]}\n"
          f"Средний темп роста: x{average:.2f}\n"
          f"Прогноз следующего поколения: ~{forecast} кубитов")


# Ожидаемый вывод из файла с заданием
EXPECTED = {
    1: """Ethereum: 108,000 транзакций/час
Binance Smart Chain: 576,000 транзакций/час
Solana: 180,000,000 транзакций/час
Лидер: Solana""",
    2: """Записей в секунду: 500
Минимум чтений/с: 50,000
Максимум чтений/с: 5,000,000""",
    3: """Блок 0: hash=00a30cc109e5f537... prev=0...
Блок 1: hash=e6c304c849b2975e... prev=00a30cc109e5f537...
Блок 2: hash=1594922ea06f6ad6... prev=e6c304c849b2975e...""",
    4: """SHA-256('blockchain') =
ef7797e13d3a75526946a3bcf00daec9fc9c9c4d51ddc7cc5df888f74dd434d1""",
    5: """difficulty=4, nonce=52533
hash=00005d679a4732611132fb28f8cbc90cc513f51a35efca8a6a25bfdab2bf7e69""",
    6: "Merkle root: "
       "773bc304a3b0a626a520a8d6eacc36809ac18c0b174f3ff3cdaf0a4e9c64433d",
    7: """Доля мощности 30%: безопасно
Доля мощности 51%: УГРОЗА (атака 51%)
Доля мощности 49%: безопасно
Доля мощности 60%: УГРОЗА (атака 51%)""",
    8: """Транзакция 0 подтверждает: — (начальная)
Транзакция 1 подтверждает: — (начальная)
Транзакция 2 подтверждает: [0, 1]
Транзакция 3 подтверждает: [2, 1]
Транзакция 4 подтверждает: [1, 0]
Транзакция 5 подтверждает: [1, 0]""",
    9: """n=  10 транзакций -> время подтверждения = 100.00 усл.ед.
n= 100 транзакций -> время подтверждения = 10.00 усл.ед.
n=1000 транзакций -> время подтверждения = 1.00 усл.ед.""",
    10: """Транзакции Alice (3):
  Alice -> Bob: 50
  Bob -> Alice: 20
  Alice -> Carol: 10
Баланс Alice: -40""",
    11: """uniswap: 12,500 запросов
aave: 8,500 запросов
compound: 4,500 запросов
Самый нагруженный: uniswap
Всего запросов: 25,500""",
    12: """Подпись: a04f8e9328c67bfdc0f9391e ...
Проверка верной подписи: True
Проверка при подмене сообщения: False""",
    13: """  1 кубит(ов): 2 состояний одновременно | классика: 1 состояний
  2 кубит(ов): 4 состояний одновременно | классика: 2 состояний
  8 кубит(ов): 256 состояний одновременно | классика: 8 состояний
127 кубит(ов): 170,141,183,460,469,231,731,687,303,715,884,105,728 \
состояний одновременно | классика: 127 состояний""",
    14: """15 = 3 x 5
21 = 3 x 7
91 = 7 x 13""",
    15: """Поколения кубитов: [127, 433, 1121]
Коэффициенты роста: [3.41, 2.59]
Средний темп роста: x3.00
Прогноз следующего поколения: ~3362 кубитов""",
}


def main():
    """Выполнить все задания и сравнить вывод с ожидаемым."""
    for number, expected in EXPECTED.items():
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            globals()[f"task_{number}"]()
        result = output.getvalue().rstrip()
        status = "OK" if result == expected else "ОТЛИЧАЕТСЯ"
        print(f"{'=' * 60}\nЗадание {number}  [{status}]\n"
              f"--- ожидается:\n{expected}\n--- получено:\n{result}\n")
    print("* Задание 12: сообщение и ключ в условии не даны, поэтому хэш "
          "подписи\n  другой; результаты проверок (True/False) совпадают.")


if __name__ == "__main__":
    main()
