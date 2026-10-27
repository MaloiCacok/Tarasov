import hashlib
import socket
import time
from concurrent.futures import ThreadPoolExecutor

import requests


class Block:
    NUM_ZEROS = 4

    def __init__(self, index, surname, group, prev_hash,
                 message="Привет, блокчейн!", timestamp=None, nonce=0):
        self.index = index
        self.surname = surname
        self.group = group
        self.message = message
        self.prev_hash = prev_hash
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.nonce = nonce
        self.hash = None

    @property
    def data(self):
        return f"{self.surname}, группа {self.group} — {self.message}"

    def header(self):
        return f"{self.index}|{self.prev_hash}|{self.data}|{self.timestamp}|{self.nonce}"

    def calc_hash(self):
        return hashlib.sha256(self.header().encode("utf-8")).hexdigest()

    def mine(self):
        prefix = "0" * Block.NUM_ZEROS
        self.hash = self.calc_hash()
        while not self.hash.startswith(prefix):
            self.nonce += 1
            self.hash = self.calc_hash()
        return self.nonce, self.hash

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "surname": self.surname,
            "group": self.group,
            "prev_hash": self.prev_hash,
            "nonce": self.nonce,
            "hash": self.hash,
        }


class StudentClient:

    def __init__(self, server_url, surname, group):
        url = server_url.strip().rstrip("/")
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        self.server = url
        self.surname = surname
        self.group = group

    @staticmethod
    def local_ip():
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]

    @staticmethod
    def check_server(ip, port, timeout=0.5):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            if s.connect_ex((ip, port)) != 0:
                return None
        url = f"http://{ip}:{port}"
        try:
            last = requests.get(f"{url}/last_block", timeout=5).json()
        except (requests.RequestException, ValueError):
            return None
        return url if "hash" in last and "index" in last else None

    @classmethod
    def find_server(cls, port=5000, known_ip=None):
        if known_ip:
            print(f"Проверяю известный адрес {known_ip}:{port}…")
        if known_ip and cls.check_server(known_ip, port, timeout=3):
            print(f"Найден сервер: http://{known_ip}:{port}")
            return f"http://{known_ip}:{port}"
        my_ip = cls.local_ip()
        network = my_ip.rsplit(".", 1)[0]
        print(f"Мой IP: {my_ip}. Ищу сервер в сети {network}.0/24 на порту {port}…")
        ips = ["127.0.0.1"] + [f"{network}.{i}" for i in range(1, 255)]
        with ThreadPoolExecutor(max_workers=100) as pool:
            found = [url for url in pool.map(cls.check_server, ips,
                                             [port] * len(ips)) if url]
        if not found:
            return None
        print(f"Найден сервер: {found[0]}")
        return found[0]

    def get_last_block(self):
        return requests.get(f"{self.server}/last_block", timeout=10).json()

    def create_block(self, last, message):
        return Block(last["index"] + 1, self.surname, self.group, last["hash"],
                     message=message)

    def submit(self, block):
        r = requests.post(f"{self.server}/add_block", json=block.to_dict(), timeout=10)
        return r.status_code, r.json()

    def show_chain(self):
        chain = requests.get(f"{self.server}/chain", timeout=10).json()["chain"]
        print("\nТекущая цепочка преподавателя:")
        for b in chain:
            who = "ГЕНЕЗИС" if b["index"] == 0 else f"{b['surname']} (гр. {b['group']})"
            print(f"  #{b['index']:>2}  {who:<30} hash={b['hash'][:12]}…  prev={b['prev_hash'][:12]}…")

    def run(self, message="Привет, блокчейн!"):
        print(f"Подключаюсь к {self.server}  как  {self.surname} (гр. {self.group})")
        for attempt in range(1, 6):
            last = self.get_last_block()
            block = self.create_block(last, message)
            print(f"[Попытка {attempt}] Майнинг блока #{block.index} … "
                  f"(ищем хэш с {Block.NUM_ZEROS} нулями)")
            nonce, h = block.mine()
            print(f"  Найден nonce={nonce}, hash={h[:20]}…  отправляем преподавателю…")
            status, res = self.submit(block)
            if res.get("accepted"):
                print(f"\n✔ БЛОК ПРИНЯТ! Ваш блок #{res['index']} добавлен в цепочку. "
                      f"Длина цепочки: {res['chain_length']}.")
                break
            print(f"✖ Блок отклонён: {res.get('reason')}")
            if status == 409 and "last_block" in res:
                print("  Цепочка изменилась — перемайниваем…")
                continue
            break
        self.show_chain()


if __name__ == "__main__":
    server = StudentClient.find_server(5000, known_ip="10.39.120.52")
    if server is None:
        print("Сервер не найден. Проверьте, что вы в одной Wi-Fi сети "
              "с преподавателем и сервер запущен.")
    else:
        client = StudentClient(server_url=server,
                               surname="Камиль Закиров", group="ОКБП-401итмп")
        client.run("Привет я зашел")
