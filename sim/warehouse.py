import json
import os
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

class WarehouseMap:
    def __init__(self, filepath: str):
        with open(filepath, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.name = self.data["name"]
        self.width = self.data["width"]
        self.height = self.data["height"]
        self.layout = self.data["layout"]
        self.legend = self.data["legend"]
        
    def print_ascii_grid(self):
        print(f"Warehouse: {self.name} ({self.width}x{self.height}, {self.data.get('cell_size_m', 0.5)}m cells)")
        for row in self.layout:
            display_row = ""
            for char in row:
                if char == '.': display_row += ' '
                elif char == 'R': display_row += '▓'
                elif char == 'J': display_row += '◆'
                elif char == 'P': display_row += 'P'
                elif char == 'D': display_row += 'D'
                elif char == 'C': display_row += '⚡'
                else: display_row += char
            print(display_row)

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    map_path = os.path.join(current_dir, "maps", "small_3amr.json")
    warehouse = WarehouseMap(map_path)
    warehouse.print_ascii_grid()
