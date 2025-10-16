from flask import Flask, render_template_string, url_for, request, redirect
import os

app = Flask(__name__)

def get_pdf_files():
    static_folder = os.path.join(app.root_path, 'static')
    pdf_files = [f for f in os.listdir(static_folder) if f.lower().endswith('.pdf')]
    pdf_files.sort()  # Ensure consistent order
    return pdf_files

@app.route('/')
def home():
    return render_template_string(f"""
        <h1>PDF Viewer</h1>
        <form action="/pdf-editor" method="get">
            <button type="submit">Dateien zusammenfügen</button>
        </form>""")

@app.route('/pdf-editor', methods=['GET', 'POST'])
def pdf_editor():
    order_file = os.path.join(app.root_path, 'static', 'order.txt')
    pdf_files = get_pdf_files()

    # Load or initialize order
    if os.path.exists(order_file):
        with open(order_file, 'r') as f:
            ordered = [line.strip() for line in f if line.strip() in pdf_files]
        # Add new files if any
        for f in pdf_files:
            if f not in ordered:
                ordered.append(f)
        pdf_files = ordered
    else:
        with open(order_file, 'w') as f:
            for pdf in pdf_files:
                f.write(pdf + '\n')

    # Handle requests from buttons
    if request.method == 'POST':
        action = request.form.get('action')
        filename = request.form.get('filename')
        idx = pdf_files.index(filename)
        if action == 'up' and idx > 0:
            pdf_files[idx], pdf_files[idx-1] = pdf_files[idx-1], pdf_files[idx]
        elif action == 'down' and idx < len(pdf_files) - 1:
            pdf_files[idx], pdf_files[idx+1] = pdf_files[idx+1], pdf_files[idx]
        # Save new order
        with open(order_file, 'w') as f:
            for pdf in pdf_files:
                f.write(pdf + '\n')
        return redirect('/pdf-editor')

    # Create PDFs with control in HTML
    pdf_iframes = ""
    for pdf in pdf_files:
        pdf_url = url_for('static', filename=pdf)
        pdf_iframes += f"""
        <div style="display: flex; align-items: center; margin-bottom: 30px;">
            <iframe src="{pdf_url}" width="350px" height="500px" style="border:1px solid #ccc;"></iframe>
            <form method="post" style="display: flex; flex-direction: column; margin-left: 20px;">
                <input type="hidden" name="filename" value="{pdf}">
                <button name="action" value="up" style="margin-bottom: 10px;">⬆️ Move Up</button>
                <button name="action" value="down" style="margin-bottom: 10px;">⬇️ Move Down</button>
                <button style="margin-bottom: 10px;" disabled>🗑️ Delete</button>
                <button style="margin-bottom: 10px;" disabled>⟳ Rotate CW</button>
                <button disabled>⟲ Rotate CCW</button>
            </form>
        </div>
        """
    return render_template_string(f"""
        <h1>PDF Dokumente</h1>
        {pdf_iframes}
    """)

if __name__ == '__main__':
    app.run(debug=True)
