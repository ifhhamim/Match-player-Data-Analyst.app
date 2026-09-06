import tkinter as tk
from ui import SportAnalyzerUI
from data_manager import DataManager

def main():
    root = tk.Tk()
    data_manager = DataManager()
    app = SportAnalyzerUI(root, data_manager)
    root.mainloop()

if __name__ == "__main__":
    main() 
    