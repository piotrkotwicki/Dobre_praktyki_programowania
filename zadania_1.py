import string

def is_palindrome(text: str) -> bool:
    cleaned = ''.join(c.lower() for c in text if c != ' ')
    return cleaned == cleaned[::-1]


def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("Indeks Fibonacciego nie może być ujemny")
    if n == 0:
        return 0
    elif n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_vowels(text: str) -> int:
    vowels = set("aeiouy")
    return sum(1 for c in text.lower() if c in vowels)


def calculate_discount(price: float, discount: float) -> float:
    if not 0 <= discount <= 1:
        raise ValueError("Zniżka musi być w zakresie od 0 do 1")
    return price * (1 - discount)


def flatten_list(nested_list: list) -> list:
    flattened = []
    for item in nested_list:
        if isinstance(item, list):
            flattened.extend(flatten_list(item))
        else:
            flattened.append(item)
    return flattened


def word_frequencies(text: str) -> dict:
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    words = text.split()
    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1
    return freq


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True
