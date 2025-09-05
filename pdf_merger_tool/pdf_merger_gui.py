import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfMerger

def merge_pdfs():
    files = filedialog.askopenfilenames(
        title="Select PDF files to merge",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not files:
        return

    save_path = filedialog.asksaveasfilename(
        title="Save Merged PDF As",
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not save_path:
        return

    try:
        merger = PdfMerger()
        for pdf in files:
            merger.append(pdf)
        merger.write(save_path)
        merger.close()
        messagebox.showinfo("Success", f"Merged PDF saved as:\n{save_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")

# GUI setup
root = tk.Tk()
root.title("PDF Merger Tool")
root.geometry("400x200")

label = tk.Label(root, text="Merge Multiple PDFs Easily", font=("Arial", 14))
label.pack(pady=20)

merge_button = tk.Button(root, text="Select PDFs & Merge", command=merge_pdfs, font=("Arial", 12), bg="blue", fg="white")
merge_button.pack(pady=20)

root.mainloop()
