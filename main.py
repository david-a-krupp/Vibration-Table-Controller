import tkinter as tk
from gui import VibrationControllerUI

if __name__ == "__main__":
    root = tk.Tk()
    app = VibrationControllerUI(root)
    root.mainloop()