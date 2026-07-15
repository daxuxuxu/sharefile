import sys
from docx import Document
from docx.oxml.ns import qn

doc = Document(r"C:\Users\xuchen12\mindmap_overseas\source.docx")

body = doc.element.body
for child in body.iterchildren():
    tag = child.tag.split('}')[-1]
    if tag == 'p':
        # find paragraph object
        text = ''.join(node.text or '' for node in child.iter(qn('w:t')))
        # style
        pPr = child.find(qn('w:pPr'))
        style = ''
        ilvl = ''
        numId = ''
        if pPr is not None:
            ps = pPr.find(qn('w:pStyle'))
            if ps is not None:
                style = ps.get(qn('w:val'))
            numPr = pPr.find(qn('w:numPr'))
            if numPr is not None:
                il = numPr.find(qn('w:ilvl'))
                ni = numPr.find(qn('w:numId'))
                if il is not None: ilvl = il.get(qn('w:val'))
                if ni is not None: numId = ni.get(qn('w:val'))
        if text.strip():
            print(f"[P style={style!r} ilvl={ilvl} numId={numId}] {text}")
    elif tag == 'tbl':
        print("=== TABLE ===")
        for row in child.iter(qn('w:tr')):
            cells = []
            for tc in row.iter(qn('w:tc')):
                ctext = ''.join(node.text or '' for node in tc.iter(qn('w:t')))
                cells.append(ctext)
            print(" | ".join(cells))
        print("=== END TABLE ===")
