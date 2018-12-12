def pick_file(directory):
    # Local import as some OS's don't have tkinter built-in
    from tkinter import Tk
    from tkinter.filedialog import askopenfilename

    root = Tk()

    # Rearrange windows:
    # `withdraw` hides the "root" window that comes up alongside the actual file dialog window
    # `lift` and "-topmost" bring the file dialog to the front
    root.withdraw()
    root.lift()
    root.attributes("-topmost", True)

    filepath = askopenfilename(
        parent=root,
        initialdir=directory
    )

    root.destroy()  # Make sure the hidden "root" window is closed

    return filepath
