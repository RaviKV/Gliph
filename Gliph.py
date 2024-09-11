import wx
import os
import re
import fitz  # PyMuPDF for handling PDFs
import pandas as pd
from docx import Document

class MaskingApp(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MaskingApp, self).__init__(*args, **kwargs)

        # Set up the GUI
        panel = wx.Panel(self)

        # Set background color
        # panel.SetBackgroundColour(wx.Colour(200, 255, 200))  # Light green background

        # Create a vertical sizer for the panel
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Add a static text for the description
        description = wx.StaticText(panel, label="This tool helps you mask sensitive data within your file, "
                                                "The config should contains sensitive words to be masked.")
        vbox.Add(description, flag=wx.EXPAND | wx.ALL, border=10)

        # Input file selection
        input_label = wx.StaticText(panel, label="Input File:")
        vbox.Add(input_label, flag=wx.EXPAND | wx.LEFT | wx.TOP, border=10)
        self.input_file_picker = wx.FilePickerCtrl(panel, message="Select the input file")
        vbox.Add(self.input_file_picker, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        # Config file selection
        config_label = wx.StaticText(panel, label="Config File (Sensitive Words):")
        vbox.Add(config_label, flag=wx.EXPAND | wx.LEFT | wx.TOP, border=10)
        self.config_file_picker = wx.FilePickerCtrl(panel, message="Select the config file")
        vbox.Add(self.config_file_picker, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        # Output file selection
        output_label = wx.StaticText(panel, label="Output File:")
        vbox.Add(output_label, flag=wx.EXPAND | wx.LEFT | wx.TOP, border=10)
        self.output_file_picker = wx.FilePickerCtrl(panel, message="Select the output file", style=wx.FLP_SAVE | wx.FLP_OVERWRITE_PROMPT)
        vbox.Add(self.output_file_picker, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        # Button to start masking process
        mask_button = wx.Button(panel, label="Mask & Save")
        vbox.Add(mask_button, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        mask_button.Bind(wx.EVT_BUTTON, self.on_mask)

        # Set the sizer for the panel
        panel.SetSizer(vbox)

        self.SetSize((800, 600))
        self.SetTitle('Mask Sensitive Information')
        self.Centre()

    def on_mask(self, event):
        input_file = self.input_file_picker.GetPath()
        config_file = self.config_file_picker.GetPath()
        output_file = self.output_file_picker.GetPath()

        if not input_file or not config_file or not output_file:
            wx.MessageBox("Please select all the required files.", "Error", wx.OK | wx.ICON_ERROR)
            return

        try:
            self.mask_sensitive_info(input_file, config_file, output_file)
            wx.MessageBox(f"Masked output saved to '{output_file}'", "Success", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f"Error: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)

    def mask_sensitive_info(self, input_file, config_file, output_file):
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file '{input_file}' not found.")
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file '{config_file}' not found.")

        with open(config_file, 'r') as file:
            mask_words = file.read().splitlines()

        file_content = self.read_file(input_file)
        for word in mask_words:
            masked_word = "*" * len(word)
            file_content = re.sub(re.escape(word), masked_word, file_content)

        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        phone_pattern = r'\b(?:\+?\d{1,4}[ -]?)?\(?\d{1,4}\)?[ -]?\d{1,4}[ -]?\d{1,9}\b'

        file_content = re.sub(ip_pattern, lambda x: '*' * len(x.group()), file_content)
        file_content = re.sub(email_pattern, lambda x: '*' * len(x.group()), file_content)
        file_content = re.sub(phone_pattern, lambda x: '*' * len(x.group()), file_content)

        with open(output_file, 'w') as file:
            file.write(file_content)

    def read_file(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return self.read_pdf(file_path)
        elif ext == '.docx':
            return self.read_docx(file_path)
        elif ext in ('.xls', '.xlsx'):
            return self.read_excel(file_path)
        elif ext == '.txt':
            with open(file_path, 'r') as file:
                return file.read()
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def read_pdf(self, file_path):
        text = ""
        pdf_document = fitz.open(file_path)
        for page in pdf_document:
            text += page.get_text()
        return text

    def read_docx(self, file_path):
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def read_excel(self, file_path):
        df = pd.read_excel(file_path, sheet_name=None)
        text = ""
        for sheet_name, sheet_data in df.items():
            text += sheet_data.to_string(index=False) + "\n"
        return text


def main():
    app = wx.App(False)
    frame = MaskingApp(None)
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
