from flask import Flask, render_template, send_file, redirect
from PyPDF2 import PdfFileWriter, PdfFileReader
from os import makedirs
from os.path import isfile
from glob import glob

app = Flask(__name__)

def get_saved_page(which):
    """Retrieve the last visited page of a pdf"""
    if not isfile('pdfs/{}.saved'.format(which)):
        set_saved_page(which, 0)
        return 0
    with open('pdfs/{}.saved'.format(which), 'r') as f:
        return int(f.read())

def set_saved_page(which, page):
    """Set the last visited page of a pdf"""
    if not isfile('pdfs/{}.saved'.format(which)):
        open('pdfs/{}.saved'.format(which), 'a').close()
    with open('pdfs/{}.saved'.format(which), 'w') as f:
        f.write(str(page))


@app.route('/pdf/<which>/<page>')
def serve_pdf(which, page):
    """Serve a page of a pdf file"""
    return send_file('pdfs/{}.pages/{}.pdf'.format(which, page))

@app.route('/<which>')
@app.route('/<which>/<page>')
def pdf(which, page=None):
    """Create a page of a pdf and display it"""
    if page is None:
        page = get_saved_page(which)
    page = int(page)
    if page < 0:
        return redirect('{}/{}'.format(which, 0))
    if not isfile('pdfs/{}.pages/{}.pdf'.format(which, page)):
        makedirs('pdfs/{}.pages'.format(which), exist_ok=True)
        pdfout = PdfFileWriter()
        with open('pdfs/{}'.format(which), 'rb') as fin:
            pdfin = PdfFileReader(fin)
            if pdfin.isEncrypted:
                pdfin.decrypt('')
            pdfout.addPage(pdfin.getPage(page))
            with open('pdfs/{}.pages/{}.pdf'.format(which, page), 'wb') as fout:
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
