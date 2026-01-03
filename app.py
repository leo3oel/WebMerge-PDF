# Run

from flask import Flask, render_template_string, url_for, request, redirect, render_template
from PdfEditor import PdfEditor
from pathlib import Path
from datetime import datetime

from Config import Config

PDFHEIGHT = 450
PDFWIDTH = 350

config = Config()
app = Flask(__name__)
pdf_editor = PdfEditor(Path.cwd() / "static" / "input")
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
        if action == 'up' and filename:
            pdf_editor.move_file_up(filename)
        elif action == 'down' and filename:
            pdf_editor.move_file_down(filename)
        elif action == 'delete' and filename:
            pdf_editor.delete_file(filename)
        elif action == 'rotate_cw' and filename:
            pdf_editor.rotate_file_cw(filename)
        elif action == 'rotate_ccw' and filename:
            pdf_editor.rotate_file_ccw(filename)
        elif action == 'split_pdf' and filename:
            pdf_editor.split_pdf(filename)
        elif action == 'back':
            return redirect('/')  # go back to selection page
        elif action == 'save':
            return redirect('/save')  # go to save page
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

@app.route('/save', methods=['GET', 'POST'])
def save():
    selected_save_path = None
    if request.method == 'POST':
        action = request.form.get('action')
        save_path = request.form.get('savepath')
        filename = request.form.get('filename')
        if action == 'back':
            return redirect('/pdf-editor')  # go back to edit page
        if action == 'save' and save_path and filename:
            filename = save_path.split(" -- ")[0] + "_" + filename
            pdf_editor.create_merged_pdf(Path.cwd() / "output" / filename)
            pdf_editor.delete_preview()
            return redirect('/cleanup')  # go to cleanup page
        return redirect(url_for('/save'))  # reload page
    
    # TODO: Delete preview file after done
    pdf_files = pdf_editor.get_pdf_files()
    preview_url = pdf_editor.create_preview()
    filename=datetime.now().strftime("%Y-%m-%d_%H-%M-%S.pdf")
    save_paths = [f"{save_path.name} -- {save_path.description}" for save_path in config.save_paths]
    return render_template('save.html',
        pdf_files=pdf_files,
        preview_url=preview_url,
        filename=filename,
        save_paths=save_paths,
        PDFHEIGHT=PDFHEIGHT*1.5,
        PDFWIDTH=PDFWIDTH*1.5)

@app.route('/cleanup', methods=['GET', 'POST'])
def cleanup():
    # Always refresh the list from disk
    pdf_editor.create_pdf_list()

    # Handle delete action
    if request.method == 'POST':
        action = request.form.get('action')
        filename = request.form.get('filename')
        if action == 'delete':
            if filename == "ALL":
                # Delete all files
                pdf_editor.delete_all_files()
            elif filename:
                pdf_editor.delete_file(filename)
        elif action == 'back':
            return redirect('/')
        return redirect('/cleanup')

    # Get all PDF files
    pdf_files = pdf_editor.get_pdf_files()
    pdf_editor.set_urls()
    
    return render_template('cleanup.html',
        pdf_files=pdf_files,
        PDFHEIGHT=PDFHEIGHT,
        PDFWIDTH=PDFWIDTH
    )

if __name__ == '__main__':
    app.run(debug=True)
