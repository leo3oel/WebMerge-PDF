# Run

from flask import Flask, render_template_string, url_for, request, redirect
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


def human_readable_size(num: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return f"{num:3.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} PB"


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
    pdf_files = pdf_editor.get_pdf_files()

    items_html = ""
    for pdf in pdf_files:
        name = pdf.filepath.name
        url = url_for('static', filename=name)
        filesize = getattr(pdf, "filesize", None)
        filesize_str = human_readable_size(filesize) if filesize is not None else "unknown"
        timestamp = getattr(pdf, "timestamp", None)
        timestamp_str = timestamp.strftime("%H:%M:%S %d.%m.%Y") if timestamp else "unknown"

        items_html += f"""
        <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 8px; border-bottom:1px solid #eee;">
            <div style="display:flex; align-items:center; gap:12px; width:100%;">
                <div style="flex:0 0 160px;">
                    <iframe src="{url}" width="{PDFWIDTH}px" height="{PDFHEIGHT}px" style="border:1px solid #ddd;"></iframe>
                </div>
                <div style="flex:1; display:flex; flex-direction:column; gap:6px; padding-left:12px;">
                    <div style="font-weight:600;"><a href="{url}" target="_blank" style="text-decoration:none; color:inherit;">{name}</a></div>
                    <div style="color:#666; font-size:0.9em;">Size: {filesize_str} · Modified: {timestamp_str}</div>
                </div>
                <div style="width:180px; display:flex; flex-direction:column; gap:8px; margin-left:12px;">
                    <label class="btn btn-select">
                        <input
                            type="checkbox"
                            name="selected"
                            value="{name}"
                            form="selectionForm"
                            class="select-checkbox"
                            onchange="this.parentElement.classList.toggle('selected', this.checked)"
                        >
                        ✔ Select
                        </label>
                    <button type="button" onclick="deleteFile('{name}')" class="btn btn-delete">🗑️ Delete</button>
                </div>
            </div>
        </div>
        """

    return render_template_string(f"""
        <link rel="stylesheet" href="{url_for('static', filename='styles.css')}">

                <h1>PDF Auswahl</h1>

        <!-- selection form (GET) sends selected filenames to /pdf-editor as ?selected=... -->
        <form id="selectionForm" action="/pdf-editor" method="get" style="margin-bottom:20px;">
            <div style="max-width:1100px; margin-bottom:12px;">
                {items_html}
            </div>
            <button type="submit" class="btn btn-submit">Edit Selected</button>
        </form>

        <!-- hidden delete form (POST) to avoid nested forms; JS will populate and submit it -->
        <form id="deleteForm" method="post" style="display:none;">
            <input type="hidden" name="action" value="delete">
            <input type="hidden" name="filename" id="deleteFilename" value="">
        </form>

        <script>
            function deleteFile(filename) {{
                if (!confirm("Delete '" + filename + "'? This will remove the file from disk.")) return;
                const f = document.getElementById('deleteFilename');
                f.value = filename;
                document.getElementById('deleteForm').submit();
            }}
        </script>

        <p>Wähle die PDFs aus, die du auf der nächsten Seite bearbeiten willst. Verwende die Lösch-Buttons, um Dateien direkt zu entfernen. Sind keine PDFs ausgewählt, werden alle angezeigt.</p>
    """)


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

    # Create PDFs with control in HTML (buttons on the right)
    pdf_iframes = ""
    for pdf in pdf_files:
        name = pdf.filepath.name
        pdf_url = url_for('static', filename=name)
        filesize = getattr(pdf, "filesize", None)
        filesize_str = human_readable_size(filesize) if filesize is not None else "unknown"
        timestamp = getattr(pdf, "timestamp", None)
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S") if timestamp else "unknown"

        pdf_iframes += f"""
        <div style="display: flex; align-items: center; margin-bottom: 12px; gap:8px; border-bottom:1px solid #eee; padding-bottom:8px;">
        <div style="flex:0 0 360px;">
            <iframe src="{pdf_url}" width="{PDFWIDTH}px" height="{PDFHEIGHT}px" style="border:1px solid #ccc;"></iframe>
        </div>
        <div style="flex:0 1 auto; display:flex; flex-direction:column; gap:6px; padding-left:12px;">
            <div style="font-weight:600;">{name}</div>
            <div style="color:#666;">Size: {filesize_str} · Modified: {timestamp_str} · Pages: {getattr(pdf, 'num_pages', 'unknown')}</div>
        </div>
        <form method="post" style="width: 180px;display: flex; flex-direction: column; gap:6px;  margin-left:12px; padding-left:50px">
            <input type="hidden" name="filename" value="{name}">
            <button name="action" value="up" class="btn">⬆️ Move Up</button>
            <button name="action" value="down" class="btn">⬇️ Move Down</button>
            <button name="action" value="delete" class="btn btn-delete">🗑️ Delete</button>
            <button name="action" value="rotate_cw" class="btn">⟳ Rotate CW</button>
            <button name="action" value="rotate_ccw" class="btn">⟲ Rotate CCW</button>
        """

        if hasattr(pdf, "num_pages") and pdf.num_pages > 1:
            pdf_iframes += f"""<button name="action" value="split_pdf" class="btn">✂️ Split PDF</button>"""
        else:
            pdf_iframes += f"""<button disabled style="margin-top:6px; padding:6px 10px;">✂️ Split PDF</button>"""

        pdf_iframes += f"""
        </form>
    </div>
    """

    return render_template_string(f"""
        <link rel="stylesheet" href="{url_for('static', filename='styles.css')}">
        <h1>PDF Edit</h1>
        {pdf_iframes}
        <p><a href="/">Zurück zur Auswahl</a></p>
    """)


if __name__ == '__main__':
    app.run(debug=True)
