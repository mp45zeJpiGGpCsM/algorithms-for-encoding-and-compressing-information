import heapq
from collections import defaultdict


class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq # сравниваем частоты объектов


class Huffman:
    def __init__(self):
        self.freq_table = defaultdict(int) # словарь счетчиков
        self.huffman_tree = None # переменная для хранения дерева Хаффмана
        self.code_table = {} # словарь, который будет хранить коды символов после выполнения алгоритма Хаффмана

    def build_freq_table(self, file_path): # Здесь строим таблицу частот символов в файле
        with open(file_path, 'r') as file:
            data = file.read()
            for char in data:
                self.freq_table[char] += 1

    def build_huffman_tree(self): # Здесь строим дерево Хаффмана
        heap = []   # Создаем пустую кучу
        for char, freq in self.freq_table.items():
            heapq.heappush(heap, HuffmanNode(char, freq))

        while len(heap) > 1:
            lo = heapq.heappop(heap)  # два узла (lo, hi) с наименьшими частотами
            hi = heapq.heappop(heap)
            parent = HuffmanNode(None, lo.freq + hi.freq)   # Создаем нового родителя для них с суммарной частотой
            parent.left = lo   # Устанавливаем левым потомком родителя узел с меньшей частотой
            parent.right = hi  # Устанавливаем правым потомком родителя узел с большей частотой
            heapq.heappush(heap, parent)   # Добавляем созданного родителя обратно в кучу

        self.huffman_tree = heap[0]   # Корневой узел дерева Хаффмана равен единственному элементу в куче

    def build_code_table(self):  # Здесь строим таблицу кодов Хаффмана, связывающую символы с их бинарными кодами
        def traverse(node, code):
            if node.char:   # Если узел содержит символ, то добавляем его в таблицу
                self.code_table[node.char] = code
            else:   # Иначе, рекурсивно вызываем traverse()
                traverse(node.left, code + '0')   # при этом добавляя '0' к коду для левого поддерева
                traverse(node.right, code + '1')  # правого поддерева и '1' для правого

        traverse(self.huffman_tree, '')  # Здесь начинается выполнение traverse() с корневого узла huffman_tree
                                        # и пустая строка передается в качестве начального кода

    def encode_file(self, input_file_path, output_file_path):
        with open(input_file_path, 'r') as input_file, open(output_file_path, 'w') as output_file:
            data = input_file.read()
            encoded_data = ""
            for char in data:
                encoded_data += self.code_table[char]
            output_file.write(encoded_data)

    def decode_file(self, input_file_path, output_file_path):
        with open(input_file_path, 'r') as input_file, open(output_file_path, 'w') as output_file:
            encoded_data = input_file.read()
            decoded_data = ""
            current_node = self.huffman_tree  # Устанавливаем текущий узел в корень дерева Хаффмана
            for bit in encoded_data:
                if bit == '0':  # Если бит равен '0', переходим в левого потомка текущего узла
                    current_node = current_node.left
                else:  # иначе в правого потомка текущего узла
                    current_node = current_node.right
                if current_node.char:  # Если текущий узел является листом
                    decoded_data += current_node.char   # добавляем его символ в раскодированную строку
                    current_node = self.huffman_tree    # Возвращаемся в корень дерева Хаффмана
            output_file.write(decoded_data)



huffman = Huffman()
num = int(input('Вы хотите кодировать(1) или декодировать(0) ваш файл?\n'))
if num == 1:
    text = str(input('Введите ваш файл, только не забудьте в конце написать ".txt"\n'))
    huffman.build_freq_table(text)
    huffman.build_huffman_tree()
    huffman.build_code_table()
    huffman.encode_file(text, 'encoded.txt')
    print('Кодирование прошло успешно ;)')
else:
    text = str(input('Введите ваш файл, только не забудьте в конце написать ".txt"\n'))
    huffman.build_freq_table('input.txt')
    huffman.build_huffman_tree()
    huffman.build_code_table()
    huffman.decode_file(text, 'decoded.txt')
    print('Декодирование прошло успешно ;)')
