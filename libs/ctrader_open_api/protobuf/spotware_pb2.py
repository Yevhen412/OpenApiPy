# spotware_pb2.py — заглушка для обхода ошибки импорта

# Пример структуры, чтобы не падало приложение
class ProtoStub:
    def __init__(self):
        self.field = None

# Заглушка сообщений и классов
SomeMessage = ProtoStub
AnotherMessage = ProtoStub
# Добавь другие нужные заглушки по аналогии

# Или подключи реальные protobuf, если есть .proto файлы
