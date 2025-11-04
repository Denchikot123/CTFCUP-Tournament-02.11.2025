Write-up CTFCUP 02.11.2025
-

[RUS] Решение задания из категории Crypto в CTFCUP 02.11.2025
-

В задани нам было предоставлено 2 файла (task.py, task_data.txt) и необходимо было попытаться расшифровать исходный текст с помощью мастера ключа путем изменения кода на дешифровку. В одном из них был код на языке Python, в другом предоставлен зашифрованный текст и мастер-ключ.

Начнем с анализа программы Python.

Архитектура шифрования
-

Изучив код можно увидеть 4 слоя шифрования: 
- **Подстановка**

-- Что делает:

Каждый байт заменяется по случайной таблице

- **XOR с вращением битов**

-- Что делает:

Данные комбинируются с временной меткой
  
- **XOR с хешем ключа**

-- Что делает:

Побайтовый XOR с криптографическим хешем

- **Base64**

-- Что делает:

Стандартная кодировка Base64 с кастомным алфавитом

Решение задачи
-

У нас есть уже в наличии зашифрованный текст и ключ шифрования, что облегчает нашу работу.

Для того чтобы нам расшифровать данный текст, нам нужно сделать лишь обратную последовательность данных шифрований, но с небольшой оговоркой

В коде присутствует комбинация с временной меткой в 1-ом и 2-ом слое шифрования (_layer1_substitution, _layer2_xor) которая не даст нам просто выполнить обратное шифрование.

Нам необходимо перебрать данную временную метку, чтобы найти ту, с которой был зашифрован данный текст

Делается это путем добавления перебора seed и "отзеркаливание" таблицы

----------------

**Изменения в _init**:

    def __init__(self, master_key: str):
      self.master_key = master_key.encode()
      self.key_hash = hashlib.sha256(self.master_key).digest()
      # НОВОЕ: Предварительное вычисление key_seed
      self.key_seed = int.from_bytes(self.key_hash[:4], 'little') % 1000000

Для оптимизации мы предварительно вычислили числовой идентификатор ключа, который используется в нескольких этапах дешифровки

-----------------

**Добавление функции _generate_inverse_substitution_table**:

    def _generate_inverse_substitution_table(self, seed: int):
        table = self._generate_substitution_table(seed)
        inverse_table = [0] * 256
        for i, val in enumerate(table):
            inverse_table[val] = i
        return inverse_table

Для дешифровки 1 слоя нам необходима "зеркальная" таблица, которая будет делать обратную операцию

-----------------

**Реализация ключевой идеи перебора**:

    for time_seed in range(100000):
      decrypted = decrypt(encrypted_data, time_seed)
      if decrypted.startswith("Your flag is: ctfcup{"):
        break

Для перебора будем использовать 100000 значений time_seed, так как в исходном коде использовалось именно это число, что позволит нам покрыть все возможные случаи
Мы изначально уже знаем формат флага ( ctfcup{ ), соответственно добавляем данный формат в вывод, что позволит нам получить уже готовый флаг

Вывод данной программы:

    Found time_seed: 29667
    Your flag is: ctfcup{1t5_m000r3_4b0ut_pr0gramm1ng_1_gu35555}

Как раз этот флаг и является зашифрованным текстом

Итог:
-

Задача на первый взгляд имеет сложную структуру шифрования (несколько этапов), но если разобрав каждый метов, то можно выявить несколько ошибок:

- Ограниченное пространство ключей
- Избыточная сложность != безопасность
- Временные метки != криптографическая случайность
- Кастомные алгоритмы часто содержат в себе скрытые уязвимости

-----------------

[ENG] Solution to a Crypto assignment in CTFCUP, November 2, 2025
-
In the assignment, we were given two files (task.py, task_data.txt) and had to attempt to decrypt the original text using a master key by changing the decryption code. One of them contained Python code, while the other contained the encrypted text and the master key.

Let's start by analyzing the Python program.

Encryption Architecture
-

By examining the code, you can see four layers of encryption:
- **Substitution**

-- What it does:

Each byte is replaced using a random table

- **XOR with bit rotation**

-- What it does:

Data is combined with a timestamp

- **XOR with key hash**

-- What it does:

Byte-by-byte XOR with a cryptographic hash

- **Base64**

-- What it does:

Standard Base64 encoding with a custom alphabet

Problem Solution
-
We already have the ciphertext and encryption key, which makes our work easier.

To decrypt this text, we only need to reverse the encryption sequence, but with a small caveat.

The code contains a combination of timestamps in the first and second encryption layers (_layer1_substitution, _layer2_xor), which prevents us from simply performing the reverse encryption.

We need to iterate over a given timestamp to find the one with which the given text was encrypted.

This is done by iterating over the seed and "mirroring" the table.

----------------

**Changes in _init**:

    def __init__(self, master_key: str):
      self.master_key = master_key.encode()
      self.key_hash = hashlib.sha256(self.master_key).digest()
      # NEW: Precomputing key_seed
      self.key_seed = int.from_bytes(self.key_hash[:4], 'little') % 1000000

For optimization, we precomputed the numeric key identifier, which is used in several stages of decryption.

-----------------

**Adding _generate_inverse_substitution_table** function:

    def _generate_inverse_substitution_table(self, seed: int):
        table = self._generate_substitution_table(seed)
        inverse_table = [0] * 256
        for i, val in enumerate(table):
            inverse_table[val] = i
        return inverse_table

To decrypt layer 1, we need a "mirror" table that will perform the reverse operation.

-----------------
**Implementation of the key idea of ​​the enumeration**:

    for time_seed in range(100000):
      decrypted = decrypt(encrypted_data, time_seed)
      if decrypted.startswith("Your flag is: ctfcup{"):
        break

For the enumeration, we will use 100,000 time_seed values, since this is the number used in the original code, which will allow us to cover all possible cases.
We already know the flag format ( ctfcup{ ), so we add this format to the output, which will allow us to obtain a ready-made flag.

Output of this Programs:

    Found time_seed: 29667
    Your flag is: ctfcup{1t5_m000r3_4b0ut_pr0gramm1ng_1_gu35555}

This flag is the ciphertext.

Result:
-
At first glance, the problem has a complex encryption structure (several stages), but if you analyze each stage, you can identify several errors:

- Limited key space
- Excessive complexity != security
- Timestamps != cryptographic randomness
- Custom algorithms often contain hidden vulnerabilities
