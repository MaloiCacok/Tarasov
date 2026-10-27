import hashlib
import random


def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()


# 1
def transactions_per_hour(networks):
    per_hour = {name: tps * 3600 for name, tps in networks.items()}
    return per_hour, max(per_hour, key=per_hour.get)


print("Задание 1")
networks = {"Ethereum": 30, "Binance Smart Chain": 160, "Solana": 50_000}
per_hour, leader = transactions_per_hour(networks)
for name, count in per_hour.items():
    print(f"{name}: {count:,} транзакций/час")
print(f"Лидер: {leader}")


# 2
def read_range(writes):
    return writes * 100, writes * 10_000


print("\nЗадание 2")
low, high = read_range(500)
print(f"Записей в секунду: 500\nМинимум чтений/с: {low:,}\n"
      f"Максимум чтений/с: {high:,}")


# 3
class Block:

    def __init__(self, index, data, prev_hash):
        self.index, self.data, self.prev_hash = index, data, prev_hash
        self.hash = self.calc_hash()

    def calc_hash(self):
        return sha256(f"{self.index}{self.data}{self.prev_hash}")


print("\nЗадание 3")
chain = [Block(0, "Genesis", "0")]
for i in (1, 2):
    chain.append(Block(i, f"Транзакция {i}", chain[-1].hash))
for b in chain:
    print(f"Блок {b.index}: hash={b.hash[:16]}... "
          f"prev={b.prev_hash[:16]}...")


# 4
print("\nЗадание 4")
print(f"SHA-256('blockchain') =\n{sha256('blockchain')}")


# 5
def mine(data, difficulty):
    prefix = "0" * difficulty
    nonce = 0
    h = sha256(data + str(nonce))
    while not h.startswith(prefix):
        nonce += 1
        h = sha256(data + str(nonce))
    return nonce, h


print("\nЗадание 5")
nonce, block_hash = mine("block1", 4)
print(f"difficulty=4, nonce={nonce}\nhash={block_hash}")


# 6
def merkle_root(transactions):
    level = [sha256(tx) for tx in transactions]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [sha256(level[i] + level[i + 1])
                 for i in range(0, len(level), 2)]
    return level[0]


print("\nЗадание 6")
print(f"Merkle root: {merkle_root(['tx1', 'tx2', 'tx3', 'tx4'])}")


# 7
def is_attack_threat(share):
    return share > 0.5


print("\nЗадание 7")
for p in (0.3, 0.51, 0.49, 0.6):
    verdict = "УГРОЗА (атака 51%)" if is_attack_threat(p) else "безопасно"
    print(f"Доля мощности {p:.0%}: {verdict}")


# 8
def build_tangle(count):
    random.seed(42)
    return [[] if i < 2 else random.sample(range(i), 2) for i in range(count)]


print("\nЗадание 8")
for i, links in enumerate(build_tangle(6)):
    print(f"Транзакция {i} подтверждает: {links or '— (начальная)'}")


# 9
def confirmation_time(n, k=1000):
    return k / n


print("\nЗадание 9")
for n in (10, 100, 1000):
    print(f"n={n:>4} транзакций -> время подтверждения = "
          f"{confirmation_time(n):.2f} усл.ед.")


# 10
def index_address(transactions, addr):
    own = [t for t in transactions if addr in (t["from"], t["to"])]
    incoming = sum(t["amount"] for t in own if t["to"] == addr)
    outgoing = sum(t["amount"] for t in own if t["from"] == addr)
    return own, incoming - outgoing


print("\nЗадание 10")
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
    totals = {}
    for subgraph, count in log:
        totals[subgraph] = totals.get(subgraph, 0) + count
    return totals, max(totals, key=totals.get), sum(totals.values())


print("\nЗадание 11")
log = [("uniswap", 5000), ("aave", 3000), ("uniswap", 7500),
       ("compound", 4500), ("aave", 5500)]
totals, busiest, total = subgraph_stats(log)
for name, count in totals.items():
    print(f"{name}: {count:,} запросов")
print(f"Самый нагруженный: {busiest}\nВсего запросов: {total:,}")


# 12
def sign(message, private_key):
    return sha256(message + private_key)


def verify(message, signature, private_key):
    return sign(message, private_key) == signature


print("\nЗадание 12")
message, key = "Alice -> Bob: 10 BTC", "secret_key"
signature = sign(message, key)
print(f"Подпись: {signature[:24]} ...\n"
      f"Проверка верной подписи: {verify(message, signature, key)}\n"
      "Проверка при подмене сообщения: "
      f"{verify('Alice -> Bob: 1000 BTC', signature, key)}")


# 13
def quantum_states(n):
    return 2 ** n


print("\nЗадание 13")
for n in (1, 2, 8, 127):
    print(f"{n:>3} кубит(ов): {quantum_states(n):,} состояний "
          f"одновременно | классика: {n} состояний")


# 14
def factorize(n):
    factors, d = [], 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    return factors + [n] if n > 1 else factors


print("\nЗадание 14")
for n in (15, 21, 91):
    print(f"{n} = {' x '.join(map(str, factorize(n)))}")


# 15
def forecast_qubits(generations):
    rates = [b / a for a, b in zip(generations, generations[1:])]
    average = sum(rates) / len(rates)
    return rates, average, round(generations[-1] * average)


print("\nЗадание 15")
generations = [127, 433, 1121]
rates, average, forecast = forecast_qubits(generations)
print(f"Поколения кубитов: {generations}\n"
      f"Коэффициенты роста: {[round(r, 2) for r in rates]}\n"
      f"Средний темп роста: x{average:.2f}\n"
      f"Прогноз следующего поколения: ~{forecast} кубитов")
