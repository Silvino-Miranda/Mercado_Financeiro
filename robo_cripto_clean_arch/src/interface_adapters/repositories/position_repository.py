# interface_adapters/repositories/position_repository.py
import csv
from entities.position import Position

class PositionRepository:
    def __init__(self, csv_file='position.csv', delimiter=';'):
        self.csv_file = csv_file
        self.delimiter = delimiter
        self.fields = ['entry_date', 'exit_date', 'ativo', 'position', 'entry_price', 'exit_price']

    def read_data(self):
        with open(self.csv_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=self.delimiter)
            return [Position(**row) for row in reader]

    def write_data(self, data):
        with open(self.csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=self.fields, delimiter=self.delimiter)
            writer.writeheader()
            writer.writerows([vars(position) for position in data])

    def create(self, position: Position):
        data = self.read_data()
        data.append(position)
        self.write_data(data)

    def read(self, filter=None):
        data = self.read_data()
        if filter:
            data = [position for position in data if all(getattr(position, k) == v for k, v in filter.items())]
        return data

    def update(self, filter, update: dict):
        data = self.read_data()
        for position in data:
            if all(getattr(position, k) == v for k, v in filter.items()):
                for key, value in update.items():
                    setattr(position, key, value)
        self.write_data(data)

    def delete(self, filter):
        data = self.read_data()
        data = [position for position in data if not all(getattr(position, k) == v for k, v in filter.items())]
        self.write_data(data)