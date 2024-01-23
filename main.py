import tkinter as tk
from tkinter import messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
import json

class ImageMetadataViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Metadata Viewer")
        self.setup_ui()

    def setup_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.text_output = tk.Text(frame, wrap=tk.WORD, height=50, width=100)
        scrollbar = tk.Scrollbar(frame, command=self.text_output.yview)
        self.text_output.config(yscrollcommand=scrollbar.set)

        self.text_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.extract_metadata)

    def extract_png_metadata(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                png_data = bytearray(file.read())
                data_view = memoryview(png_data)

                if data_view[:4].tobytes() != b'\x89PNG':
                    messagebox.showerror("Error", "Not a valid PNG file")
                    return

                offset = 8
                txt_chunks = {}

                while offset < len(png_data):
                    length = int.from_bytes(data_view[offset:offset + 4], byteorder='big')
                    chunk_type = data_view[offset + 4:offset + 8].tobytes().decode('utf-8')

                    if chunk_type == "tEXt" or chunk_type == "comf":
                        keyword_end = offset + 8
                        while data_view[keyword_end] != 0:
                            keyword_end += 1
                        keyword = data_view[offset + 8:keyword_end].tobytes().decode('utf-8')

                        content_array_segment = data_view[keyword_end + 1:offset + 8 + length]
                        content_json = ''.join(chr(s) for s in content_array_segment)
                        txt_chunks[keyword] = json.loads(content_json)

                    offset += 12 + length

                return txt_chunks

        except Exception as e:
            messagebox.showerror("Error", f"Error extracting PNG metadata: {str(e)}")
            return

    def extract_metadata(self, event):
        file_path = event.data
        try:
            metadata = self.extract_png_metadata(file_path)

            if metadata:
                self.text_output.delete(1.0, tk.END)
                self.text_output.insert(tk.END, json.dumps(metadata, indent=2))
            else:
                messagebox.showerror("Error", "Failed to extract metadata")

        except Exception as e:
            messagebox.showerror("Error", f"Error handling drop: {str(e)}")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    root.title("Metadata Viewer")
    root.resizable(False, False)

    app = ImageMetadataViewer(root)
    root.mainloop()