from flask import Flask, render_template, send_file, redirect
from PyPDF2 import PdfFileWriter, PdfFileReader
from os import makedirs
from os.path import isfile
from glob import glob

app = Flask(__name__)

def build_path(which, mod=None, page=None):
    return 'pdfs/{}{}{}'.format(which,
                                '.{}'.format(mod) if mod is not None else '',
                                '/{}.pdf'.format(page) if page is not None else '')

def get_saved_page(which):
    """Retrieve the last visited page of a pdf"""
    saved_path = build_path(which, 'saved')
    if not isfile(saved_path):
        set_saved_page(which, 0)
        return 0
    with open(saved_path, 'r') as f:
        return int(f.read())

def set_saved_page(which, page):
    """Set the last visited page of a pdf"""
    saved_path = build_path(which, 'saved')
    if not isfile(saved_path):
        open(saved_path, 'a').close()
    with open(saved_path, 'w') as f:
        f.write(str(page))


@app.route('/pdf/<which>/<page>')
def serve_pdf(which, page):
    """Serve a page of a pdf file"""
    return send_file(build_path(which, 'pages', page))

@app.route('/<which>')
@app.route('/<which>/<page>')
def pdf(which, page=None):
    """Create a page of a pdf and display it"""
    if page is None:
        page = get_saved_page(which)
    if page == 'all':
        return send_file(build_path(which))
    page = int(page)
    pdf_path = build_path(which)
    page_directory = build_path(which, 'pages')
    page_path = build_path(which, 'pages', page)
    if page < 0:
        return redirect('{}/{}'.format(which, 0))
    if not isfile(page_path):
        makedirs(page_directory, exist_ok=True)
        pdfout = PdfFileWriter()
        with open(pdf_path, 'rb') as fin:
            pdfin = PdfFileReader(fin)
            if pdfin.isEncrypted:
                pdfin.decrypt('')
            pdfout.addPage(pdfin.getPage(page))
            with open(page_path, 'wb') as fout:
                pdfout.write(fout)
    set_saved_page(which, page)
    return render_template('index.html', which=which, page=page)

@app.route('/')
def contents():
    """List all available pdfs"""
    contents = list(map(lambda x: {'href': x.split('/')[1], 'name': ' '.join(x.split('/')[1].split('.')[0:-1])}, glob('pdfs/*.pdf')))
    return render_template('contents.html', contents=contents)

if __name__ == '__main__':
    app.run()
