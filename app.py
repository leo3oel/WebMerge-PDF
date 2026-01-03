# Run

from flask import Flask, render_template_string, url_for, request, redirect, render_template
from PdfEditor import PdfEditor
from pathlib import Path
import os
from datetime import datetime
PDFHEIGHT = 450
PDFWIDTH = 350

app = Flask(__name__)
pdf_editor = PdfEditor(Path.cwd() / "static")
# initialize file list once on startup so moves persist in-memory across requests
pdf_editor.create_pdf_list()

@app.route('/', methods=['GET', 'POST'])
def home():
    # Always refresh the list from disk so changes are visible when returning from other pages
    pdf_editor.create_pdf_list()

    # Handle delete action from homepage (submitted via hidden form)
    if request.method == 'POST':
        action = request.form.get('action')
        filename = request.form.get('filename')
        if action == 'delete' and filename:
            pdf_editor.delete_file(filename)
        return redirect('/')

    # build list with checkboxes and per-item delete buttons (delete via JS to avoid nested forms)
    pdf_editor.set_urls()
    pdf_files = pdf_editor.get_pdf_files()
    return render_template('selection.html',
        pdf_files=pdf_files,
        PDFHEIGHT=PDFHEIGHT,
        PDFWIDTH=PDFWIDTH
    )


@app.route('/pdf-editor', methods=['GET', 'POST'])
def edit_pdfs():
    # NOTE: Do NOT call create_pdf_list() here — that would reset the in-memory order.
    # POST: handle action buttons (move/delete/rotate/split)
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
        return redirect('/pdf-editor')  # reload page to see changes

    # Decide which files to show: if 'selected' present in query, filter the list for display only
    selected = request.args.getlist('selected')
    if selected:
        pdf_editor.select_files(selected)
    pdf_files = pdf_editor.get_pdf_files()
    pdf_editor.set_urls()

    return render_template('edit.html',
        pdf_files=pdf_files,
        PDFHEIGHT=PDFHEIGHT,
        PDFWIDTH=PDFWIDTH
    )

if __name__ == '__main__':
    app.run(debug=True)
