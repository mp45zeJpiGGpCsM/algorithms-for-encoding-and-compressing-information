from decimal import Decimal, getcontext

class ArithmeticCoding:
    def __init__(self):
        self.frequencies = {}  # Создаём словарь для хранения частоты каждого символа
        self.probabilities = {}  # Создаём словарь для хранения вероятности каждого символа
        self.cumulative_probabilities = {}  # Создаём словарь для хранения накопленной вероятности каждого символа
        self.low = Decimal(0)  # Устанавливаем нижнее значение low в десятичное число 0
        self.high = Decimal(1)  # Устанавливаем верхнее значение high в десятичное число 1
        self.precision = None  # Устанавливаем точность precision в None.

    def compress(self, input_file, output_file):
        with open(input_file, 'r') as file:
            data = file.read()

        self.calculate_frequencies(data)  # Подсчет частоты каждого символа в исходных данных

        self.calculate_probabilities()  # Нормализация частоты символов

        self.calculate_cumulative_probabilities()  # Создание таблицы кумулятивных вероятностей

        # Инициализация переменных для кодирования
        self.low = Decimal(0)
        self.high = Decimal(1)
        self.precision = Decimal(10) ** -len(data)  # точность кодирования

        # Кодирование данных
        for symbol in data:
            range_width = self.high - self.low
            self.low += range_width * Decimal(self.cumulative_probabilities[symbol][0])
            self.high = self.low + range_width * Decimal(self.cumulative_probabilities[symbol][1])

        with open(output_file, 'w') as file:
            file.write(str((self.low + self.high) / 2) + '\n')
            file.write(str(self.precision) + '\n')

    def decompress(self, input_file, output_file):
        with open(input_file, 'r') as file:
            encoded_data = Decimal(file.readline())
            precision = Decimal(file.readline())

        # Инициализация переменных для декодирования
        self.low = Decimal(0)
        self.high = Decimal(1)
        result = ""

        # Декодирование данных
        while True:
            range_width = self.high - self.low
            if range_width == 0:  # Проверка ширины диапазона и прерывание цикла, если ширина равна нулю
                break
            value = (encoded_data - self.low) / Decimal(range_width)  # Расчет значения на основе закодированных данных
            # Поиск символа, соответствующего значению
            symbol = None
            for s, (start, end) in self.cumulative_probabilities.items():
                if start <= value < end:
                    symbol = s
                    break

            if symbol is None:  # Прерывание цикла, если символ не найден
                break

            result += symbol  # Добавление найденного символа к результату

            # Обновление границ диапазона
            self.low += range_width * Decimal(self.cumulative_probabilities[symbol][0])
            self.high = self.low + range_width * Decimal(self.cumulative_probabilities[symbol][1])

        with open(output_file, 'w') as file:
            file.write(result)

    def calculate_frequencies(self, data):  # Подсчет частоты каждого символа в исходных данных
        self.frequencies = {}
        for symbol in data:
            if symbol in self.frequencies:  # Если символ уже есть в словаре, увеличиваем его частоту на 1
                self.frequencies[symbol] += 1
            else:  # иначе добавляем его и устанавливаем частоту в 1
                self.frequencies[symbol] = 1

    def calculate_probabilities(self):
        # Здесь происходит нормализация частоты символов путем деления каждой частоты на общее число символов
        total = sum(self.frequencies.values())
        self.probabilities = {symbol: freq / total for symbol, freq in self.frequencies.items()}

    def calculate_cumulative_probabilities(self):
        # Создание таблицы кумулятивных вероятностей
        cumulative_prob = 0
        # Для каждого символа мы сохраняем диапазон вероятностей, в котором он может появиться
        for symbol, probability in self.probabilities.items():
            self.cumulative_probabilities[symbol] = (cumulative_prob, cumulative_prob + probability)
            cumulative_prob += probability  # добавляем вероятность текущего символа



ac = ArithmeticCoding()
input_file = 'inp.txt'
output_file = 'out.txt'

# Сжатие данных
ac.compress(input_file, output_file)

# Декомпрессия данных
ac.decompress(output_file, 'decompressed_' + input_file)
