import tkinter as tk


class MyGUI:

    def __init__(self):
        self.root = tk.Tk()

        self.root.geometry("800x500")
        self.root.title("First GUI")

        self.label = tk.Label(self.root, text = "Hello World", font = ('Arial', 16))
        self.label.pack(padx = 20, pady= 20)

        self.textbox = tk.Text(self.root, height=3, font = ('Arial', 16))
        self.textbox.pack(padx = 10, pady = 10)

        self.button = tk.Button(self.root, text="Click Me!", font = ('Arial',18))
        self.button.pack(padx = 10, pady = 10)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(fill = 'x')

        self.root.mainloop()