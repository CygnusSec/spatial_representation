"""Build the report using editable Word text, tables, and OMML equations.
Requires Python 3, python-docx, lxml and a pandoc executable.
"""
from pathlib import Path
from copy import deepcopy
import json, subprocess, tempfile, zipfile, re, os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE
from lxml import etree

BASE=Path(__file__).resolve().parent
SRC=BASE/'sources'
OUT=BASE/'Spatial_Object_Representation_Report.docx'
PARTS=['front_matter.json','part1_theory.json','part2_formats.json','part3_experiments.json']
content=[]
for n in PARTS:content.extend(json.loads((SRC/n).read_text()))
# Keep the first large illustration after the raster explanation so the
# preceding page is not left half empty by an indivisible figure.
first_figure=next(b for b in content if b['type']=='figure' and b['caption'].startswith('Figure 1 '))
content.remove(first_figure)
vector_index=next(i for i,b in enumerate(content) if b.get('text')=='Vector representation and surfaces with TIN')
content.insert(vector_index,first_figure)
refs=json.loads((SRC/'bibliography_report.json').read_text())
content.append(dict(type='heading',level=1,text='References',page_break=True))
for r in refs:content.append(dict(type='reference',**r))
content.extend(json.loads((SRC/'appendices.json').read_text()))
for b in content:
    if b['type']=='heading': b['text']=b['text'].replace(':','')
    if b.get('caption','').startswith('Table 10 '):
        b['caption']='Table 10 Full-domain geometric error and viewport decoding time of MVT'
(SRC/'report_content_complete.json').write_text(json.dumps(content,ensure_ascii=False,indent=2))

# Pandoc provides a well-tested LaTeX to native OMML conversion path.
equations=[b for b in content if b['type']=='equation']
with tempfile.TemporaryDirectory(prefix='spatial-report-math-') as tmp:
    md=Path(tmp)/'equations.md'; dx=Path(tmp)/'equations.docx'
    md.write_text('\n\n'.join('$$\n'+b['tex']+'\n$$' for b in equations))
    subprocess.run(['pandoc',str(md),'-o',str(dx)],check=True)
    with zipfile.ZipFile(dx) as z:root=etree.fromstring(z.read('word/document.xml'))
    ns={'m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
    math_nodes=root.findall('.//m:oMath',ns)
    assert len(math_nodes)==len(equations),(len(math_nodes),len(equations))
    maths={b['label']:deepcopy(node) for b,node in zip(equations,math_nodes)}

doc=Document()
sec=doc.sections[0]
sec.page_width=Inches(8.5);sec.page_height=Inches(11)
sec.top_margin=Inches(.75);sec.bottom_margin=Inches(.75)
sec.left_margin=Inches(.85);sec.right_margin=Inches(.85)
sec.header_distance=Inches(.30);sec.footer_distance=Inches(.32)
sec.different_first_page_header_footer=False
doc.settings.odd_and_even_pages_header_footer=False
WIDTH=6.8
doc.core_properties.title='Representation of Spatial Objects'
doc.core_properties.subject='Spatial Databases — Group 1 — Chapter 2'
doc.core_properties.author='Group 1'
doc.core_properties.keywords='GIS, spatial representation, topology, GeoJSON, TopoJSON, KML, MVT, GeoParquet'

def setfont(style,name,size,bold=False):
    style.font.name=name;style.font.size=Pt(size);style.font.bold=bold
    style.font.color.rgb=RGBColor(0,0,0)
    rp=style.element.get_or_add_rPr()
    ff=rp.find(qn('w:rFonts'))
    if ff is None:ff=OxmlElement('w:rFonts');rp.append(ff)
    for attr in list(ff.attrib):
        if 'theme' in attr.lower():del ff.attrib[attr]
    for a in ['ascii','hAnsi','eastAsia','cs']:ff.set(qn('w:'+a),name)
    for under in list(rp.findall(qn('w:u'))):rp.remove(under)
    lang=OxmlElement('w:lang');lang.set(qn('w:val'),'en-US');rp.append(lang)

setfont(doc.styles['Normal'],'Liberation Serif',12)
nf=doc.styles['Normal'].paragraph_format
nf.space_after=Pt(6);nf.line_spacing=1.12;nf.widow_control=True
nf.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
for name,size in [('Title',22),('Subtitle',13),('Heading 1',16),('Heading 2',13),('Heading 3',12)]:
    setfont(doc.styles[name],'Liberation Serif',size,name!='Subtitle')
    pf=doc.styles[name].paragraph_format
    pf.space_before=Pt(13 if name.startswith('Heading') else 0)
    pf.space_after=Pt(6);pf.keep_with_next=True
    pf.alignment=WD_ALIGN_PARAGRAPH.LEFT
    if name.startswith('Heading'):pf.line_spacing=1.05
setfont(doc.styles['Caption'],'Liberation Serif',10.5)
# The distributed Word template has a blue bottom border on Title. Remove it.
for style in doc.styles:
    pp=style.element.find(qn('w:pPr'))
    if pp is not None:
        for border in list(pp.findall(qn('w:pBdr'))):pp.remove(border)
cf=doc.styles['Caption'].paragraph_format
cf.space_before=Pt(4);cf.space_after=Pt(7);cf.line_spacing=1.02
cf.alignment=WD_ALIGN_PARAGRAPH.LEFT
cf.keep_together=True
for name,size,font in [('Report Code',9.2,'DejaVu Sans Mono'),('Report Reference',10.7,'Liberation Serif'),('Report Metadata',10.5,'Liberation Sans')]:
    s=doc.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
    s.base_style=doc.styles['Normal'];setfont(s,font,size)
    s.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT
    s.paragraph_format.line_spacing=1.05
doc.styles['Report Code'].paragraph_format.left_indent=Inches(.12)
doc.styles['Report Code'].paragraph_format.space_after=Pt(0)
doc.styles['Report Reference'].paragraph_format.left_indent=Inches(.28)
doc.styles['Report Reference'].paragraph_format.first_line_indent=Inches(-.28)
doc.styles['Report Reference'].paragraph_format.keep_together=True
doc.styles['Report Reference'].paragraph_format.space_after=Pt(6)

# Plain running header and page numbers.
hp=sec.header.paragraphs[0];hp.text='REPRESENTATION OF SPATIAL OBJECTS'
hp.alignment=WD_ALIGN_PARAGRAPH.LEFT
for r in hp.runs:r.font.name='Liberation Sans';r.font.size=Pt(8);r.font.color.rgb=RGBColor(0,0,0)
fp=sec.footer.paragraphs[0];fp.alignment=WD_ALIGN_PARAGRAPH.RIGHT
r=fp.add_run('Group 1  •  ');r.font.size=Pt(9)
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');fp._p.append(fld)

def paragraph(text,style=None):
    p=doc.add_paragraph(text,style=style)
    return p
def caption(text,keep_next=False):
    p=paragraph(text,'Caption');p.paragraph_format.keep_with_next=keep_next
    p.runs[0].bold=True
    return p
def no_split(row):
    pr=row._tr.get_or_add_trPr();pr.append(OxmlElement('w:cantSplit'))
def table(block):
    caption(block['caption'],True)
    heads=block['headers'];rows=block['rows']
    widths=block.get('widths',[1/len(heads)]*len(heads))
    tab=doc.add_table(rows=1,cols=len(heads));tab.alignment=WD_TABLE_ALIGNMENT.CENTER
    tab.autofit=False
    pr=tab._tbl.tblPr
    borders=OxmlElement('w:tblBorders')
    for n in ['top','left','bottom','right','insideH','insideV']:
        e=OxmlElement('w:'+n);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
    pr.append(borders)
    mar=OxmlElement('w:tblCellMar')
    for k,v in [('top',75),('bottom',75),('left',85),('right',85)]:
        e=OxmlElement('w:'+k);e.set(qn('w:w'),str(v));e.set(qn('w:type'),'dxa');mar.append(e)
    pr.append(mar)
    for c,w in zip(tab.columns,widths):c.width=Inches(WIDTH*w)
    for idx,data in enumerate([heads]+rows):
        row=tab.rows[0] if idx==0 else tab.add_row()
        no_split(row)
        if idx==0:
            row._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
        for col,(cell,txt,w) in enumerate(zip(row.cells,data,widths)):
            cell.width=Inches(WIDTH*w);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p=cell.paragraphs[0];p.paragraph_format.space_after=Pt(0)
            p.paragraph_format.space_before=Pt(0);p.paragraph_format.line_spacing=1.05
            p.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.keep_together=True
            if block['caption'].startswith('Table 5 '):
                p.paragraph_format.keep_with_next=idx<len(rows)
            r=p.add_run(str(txt));r.font.name='Liberation Sans';r.font.size=Pt(10.4);r.bold=idx==0
            if idx==0:
                sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'F1F1F1');cell._tc.get_or_add_tcPr().append(sh)
    paragraph('').paragraph_format.space_after=Pt(0)

def hyperlink(p,text,url):
    h=OxmlElement('w:hyperlink')
    rel=p.part.relate_to(url,'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',is_external=True)
    h.set(qn('r:id'),rel)
    rr=OxmlElement('w:r');rp=OxmlElement('w:rPr')
    co=OxmlElement('w:color');co.set(qn('w:val'),'000000');rp.append(co)
    rr.append(rp);tt=OxmlElement('w:t');tt.text=text;rr.append(tt);h.append(rr);p._p.append(h)

for b in content:
    typ=b['type']
    if typ=='title':
        p=paragraph(b['text'],'Title');p.paragraph_format.space_after=Pt(5)
    elif typ=='subtitle':
        p=paragraph(b['text'],'Subtitle');p.paragraph_format.space_after=Pt(8)
    elif typ=='metadata':
        p=paragraph(b['text'],'Report Metadata');p.paragraph_format.space_after=Pt(13)
    elif typ=='heading':
        p=paragraph(b['text'],'Heading '+str(b['level']))
        if b.get('page_break') or b['text'].startswith('Appendix '):p.paragraph_format.page_break_before=True
    elif typ in ['paragraph','keywords']:
        p=paragraph(b['text'])
        if typ=='keywords':
            for r in p.runs:r.italic=True;r.font.size=Pt(11)
    elif typ=='equation':
        et=doc.add_table(rows=1,cols=2);et.autofit=False
        et.alignment=WD_TABLE_ALIGNMENT.CENTER
        et.columns[0].width=Inches(6.2);et.columns[1].width=Inches(.6)
        et.rows[0].cells[0].width=Inches(6.2);et.rows[0].cells[1].width=Inches(.6)
        border=OxmlElement('w:tblBorders')
        for side in ['top','bottom','left','right','insideH','insideV']:
            e=OxmlElement('w:'+side);e.set(qn('w:val'),'nil');border.append(e)
        et._tbl.tblPr.append(border);no_split(et.rows[0])
        for cell in et.rows[0].cells:
            cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cp=cell.paragraphs[0];cp.paragraph_format.space_after=Pt(3)
            cp.paragraph_format.keep_with_next=True
        p=et.cell(0,0).paragraphs[0];p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        p._p.append(deepcopy(maths[b['label']]))
        lp=et.cell(0,1).paragraphs[0];lp.alignment=WD_ALIGN_PARAGRAPH.RIGHT
        lp.add_run('('+b['label']+')')
        note=b['note'].replace('a_i','aᵢ').replace('b_i','bᵢ').replace('c_i','cᵢ').replace('x_p','xₚ').replace('y_p','yₚ').replace('d_i','dᵢ')
        n=paragraph(note);n.paragraph_format.space_after=Pt(8)
        for r in n.runs:r.font.size=Pt(11)
    elif typ=='code':
        caption(b['caption'],True)
        for i,line in enumerate(b['lines']):
            p=paragraph(line,'Report Code');p.paragraph_format.keep_with_next=i<len(b['lines'])-1
            p.paragraph_format.keep_together=True
        doc.paragraphs[-1].paragraph_format.space_after=Pt(8)
    elif typ=='figure':
        p=paragraph('');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next=True;p.paragraph_format.space_before=Pt(5);p.paragraph_format.space_after=Pt(0)
        figure_path=BASE/b['file']
        if not figure_path.exists():figure_path=BASE/'figures'/Path(b['file']).name
        image=p.add_run().add_picture(str(figure_path),width=Inches(b.get('width',6.55)))
        image._inline.docPr.set('descr',b['caption'])
        caption(b['caption'])
    elif typ=='table':table(b)
    elif typ=='reference':
        p=paragraph('['+str(b['number'])+'] '+b['text']+' ','Report Reference')
        hyperlink(p,b['url'],b['url'])
    else:raise ValueError(typ)

doc.save(OUT)
print(str(OUT))
print('Blocks',len(content),'tables',len(doc.tables),'figures',len(doc.inline_shapes),'references',len(refs),'native equations',len(maths))
