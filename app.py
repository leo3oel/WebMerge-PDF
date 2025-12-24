# Run

from flask import Flask, render_template_string, url_for, request, redirect
from PdfEditor import PdfEditor
from pathlib import Path
import os

app = Flask(__name__)
pdf_editor = PdfEditor(Path.cwd() / "static")

@app.route('/')
def home():
    pdf_editor.create_pdf_list()
    return render_template_string(f"""
        <h1>PDF Selection</h1>
        <form action="/pdf-editor" method="get">
            <button type="submit">Dateien zusammenfügen</button>
        </form>""") 

@app.route('/pdf-editor', methods=['GET', 'POST'])
def edit_pdfs():
    pdf_files = pdf_editor.get_pdf_files()

    # Handle requests from buttons
    if request.method == 'POST':
        action = request.form.get('action')
        filename = request.form.get('filename')
        if action == 'up':
            pdf_editor.move_file_up(filename)
        elif action == 'down':
            pdf_editor.move_file_down(filename)
        elif action == 'delete':
            pdf_editor.delete_file(filename)
        elif action == 'rotate_cw':
            pdf_editor.rotate_file_cw(filename)
        elif action == 'rotate_ccw':
            pdf_editor.rotate_file_ccw(filename)
        elif action == 'split_pdf':
            pdf_editor.split_pdf(filename)
        return redirect('/pdf-editor') # reload page to see changes

    # Create PDFs with control in HTML
    pdf_iframes = ""
    for pdf in pdf_files:
        pdf_url = url_for('static', filename=pdf.filepath.name)
        pdf_iframes += f"""
        <div style="display: flex; align-items: center; margin-bottom: 30px;">
            <iframe src="{pdf_url}" width="350px" height="500px" style="border:1px solid #ccc;"></iframe>
            <form method="post" style="display: flex; flex-direction: column; margin-left: 20px;">
                <input type="hidden" name="filename" value="{pdf.filepath.name}">
                <button name="action" value="up" style="margin-bottom: 10px;">⬆️ Move Up</button>
                <button name="action" value="down" style="margin-bottom: 10px;">⬇️ Move Down</button>
                <button name="action" value="delete" style="margin-bottom: 10px;">🗑️ Delete</button>
                <button name="action" value="rotate_cw" style="margin-bottom: 10px;">⟳ Rotate CW</button>
                <button name="action" value="rotate_ccw" style="margin-bottom: 10px;">⟲ Rotate CCW</button>
                """
        if pdf.num_pages > 1:
            pdf_iframes += f"""<button name="action" value="split_pdf" style="margin-bottom: 10px;">✂️ Split PDF</button>"""
        else:
            pdf_iframes += f"""<button disabled style="margin-bottom: 10px;">✂️ Split PDF</button>"""
        pdf_iframes += f"""
            </form>
        </div>
        """
    return render_template_string(f"""
        <h1>PDF Edit</h1>
        {pdf_iframes}
    """)

if __name__ == '__main__':
    app.run(debug=True)
