"""Align citations with Chapter 2 in Rigaux, Scholl and Voisard (2002).

The page anchors were checked against the 39-page excerpt of the book,
whose first and last printed folios are 29 and 67 respectively. This script
never reads the unavailable re-uploaded copy of the PDF.
"""
from __future__ import annotations
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'sources'

def update_json(filename: str, replacements: list[tuple[str, str]]):
    path=DIR/filename
    data=json.loads(path.read_text(encoding='utf-8'))
    changes=[]
    for old,new in replacements:
        matching=[]
        already=[]
        for idx,block in enumerate(data):
            for field in ('text','caption'):
                if old in block.get(field,''):
                    matching.append((idx,field))
                if new in block.get(field,''):
                    already.append((idx,field))
        if len(matching)==0 and len(already)==1:
            continue
        if len(matching)!=1:
            raise AssertionError(f'{filename}: expected exactly one match, found {matching} for {old[:65]!r}')
        i,k=matching[0]
        data[i][k]=data[i][k].replace(old,new,1)
        changes.append({'block':i,'field':k,'old':old,'new':new})
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return changes

revision={}
revision['front_matter.json']=update_json('front_matter.json',[
 ('The main source is Chapter 2 of Spatial Databases: With Application to GIS,',
  'The main theoretical source is Chapter 2 “Representation of Spatial Objects” (pp. 29–67) of the book Spatial Databases: With Application to GIS by Rigaux, Scholl and Voisard (2002),'),
])
revision['part1_theory.json']=update_json('part1_theory.json',[
 ('Chapter 2 by Rigaux, Scholl and Voisard lays the foundation for these choices through entity and field models, geometric representations and the structures that organize a collection of objects [1].',
  'Chapter 2 “Representation of Spatial Objects” of the book Spatial Databases: With Application to GIS by Rigaux, Scholl and Voisard lays the foundation for these choices through entity and field models, geometric representation and the organization of object collections [1, Chapter 2, pp. 29–51].'),
 ('Chapter 2 of the source book is the main organizing source, especially Sections 2.1 on spatial models, 2.2 on representation modes, 2.3 on object collections and 2.4 on data exchange [1].',
  'Chapter 2 “Representation of Spatial Objects” of Spatial Databases: With Application to GIS is the main organizing source [1, pp. 29–67]. Section 2.1 “Geographic Space Modeling” distinguishes entity and field models (pp. 31–34); Section 2.2 “Representation Modes” introduces tessellation, vector and half-planes (pp. 35–46); Section 2.3 “Representing the Geometry of a Collection of Objects” presents spaghetti, network and topology (pp. 46–51). Section 2.4 “Spatial Data Formats and Exchange Standards” has the TIGER/Line example (pp. 51–64); Section 2.5 contains the bibliographic notes (pp. 64–67).'),
 ('Geometry does not replace object identity [1, Sec. 2.1], [3].',
  'Geometry does not replace object identity [1, Sec. 2.1.1, pp. 31–33], [3].'),
 ('together with an interpolation rule [1], [3].',
  'together with an interpolation rule [1, Sec. 2.1.2, p. 34], [3].'),
 ('by an irregular triangular mesh or contour lines [1, Sec. 2.2].',
  'by an irregular triangular mesh or contour lines [1, Sec. 2.2.1–2.2.2, pp. 35–42].'),
 ('conceptual frame based on [1]–[3].',
  'conceptual frame based on [1, Sec. 2.1–2.2, pp. 31–42], [2], [3].'),
 ('or a Delaunay triangulation [1], [8].',
  'or a Delaunay triangulation [1, Sec. 2.2.2, pp. 38–42], [8].'),
 ('and edges [1, Sec. 2.2.3].',
  'and edges [1, Sec. 2.2.3, pp. 42–46].'),
 ('Representation basis from [1], [5].',
  'Representation basis from [1, Sec. 2.2.3, pp. 42–46], [5].'),
 ('although each polygon remains individually valid [1, Sec. 2.3.1].',
  'although each polygon remains individually valid [1, Sec. 2.3.1, pp. 47–48].'),
 ('not merely an operation that finds segment intersections [1, Sec. 2.3.2].',
  'not merely an operation that finds segment intersections [1, Sec. 2.3.2, pp. 47–49].'),
 ('and does not by itself guarantee that the data match reality [1, Sec. 2.3.3].',
  'and does not by itself guarantee that the data match reality [1, Sec. 2.3.3, pp. 49–51].'),
 ('Concepts follow [1].',
  'Concepts follow [1, Sec. 2.3, pp. 46–51].'),
 ('The example in Chapter 2 uses TIGER/Line 1998.',
  'The TIGER/Line example in Section 2.4.2 of Chapter 2 of the book uses the 1998 dataset.'),
])
revision['part3_experiments.json']=update_json('part3_experiments.json',[
 ('Three experiments were designed to connect the concepts of Chapter 2 directly with the behavior of modern formats.',
  'Three experiments were designed to connect the concepts of Chapter 2 “Representation of Spatial Objects” [1, pp. 29–67] with the behavior of modern formats.'),
 ('exchanged. Using vector coordinates in common does not make GeoJSON, TopoJSON, KML, MVT and GeoParquet serve the same data contract [1]–[3], [15]–[19].',
  'exchanged. Using vector coordinates in common does not make GeoJSON, TopoJSON, KML, MVT and GeoParquet serve the same data contract [1, Sec. 2.1–2.4, pp. 31–64], [2], [3], [15]–[19].'),
 ('in Chapter 2 still provides the basis for understanding modern technologies.',
  'in Chapter 2 “Representation of Spatial Objects” [1, pp. 31–51] still provides the basis for understanding modern technologies.'),
])

path=DIR/'bibliography_report.json'
references=json.loads(path.read_text(encoding='utf-8'))
assert len(references)==22 and references[0]['number']==1 and references[0]['archive_id']=='R01'
ref=references[0]
ref['key']='R01_Rigaux2002_Ch2'
ref['title']='Representation of Spatial Objects'
ref['book_title']='Spatial Databases: With Application to GIS'
ref['chapter']='2'
ref['pages']='29–67'
ref['text']='Rigaux, Philippe; Scholl, Michel; Voisard, Agnès. “Representation of Spatial Objects”. Chapter 2 in Spatial Databases: With Application to GIS. Morgan Kaufmann, 2002, pp. 29–67 (printed page numbers of the book).'
path.write_text(json.dumps(references,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Use an inbook record in the accompanying report-specific BibTeX, not in the
# archived bibliography of all previously searched books and papers.
bib=ROOT/'report_references.bib'
content=bib.read_text(encoding='utf-8') if bib.exists() else None
chapter='''@inbook{R01_Rigaux2002_Ch2,
  author = {Rigaux, Philippe and Scholl, Michel and Voisard, Agnès},
  title = {Representation of Spatial Objects},
  booktitle = {Spatial Databases: With Application to GIS},
  chapter = {2},
  pages = {29--67},
  year = {2002},
  publisher = {Morgan Kaufmann},
  isbn = {9781558605886},
  doi = {10.1016/B978-1-55860-588-6.X5000-3},
  url = {https://www.sciencedirect.com/book/monograph/9781558605886/spatial-databases},
  urldate = {2026-11-03}
}'''
if content is None:
    pass  # The optional BibTeX file is absent; bibliography_report.json is the source of record.
elif '@book{R01_Rigaux2002,' in content:
    start=content.index('@book{R01_Rigaux2002,')
    end=content.index('\n\n@',start)
    bib.write_text(content[:start]+chapter+content[end:],encoding='utf-8')
else:
    assert '@inbook{R01_Rigaux2002_Ch2,' in content

audit={
 'source':'Chapter 2 excerpt available from the previous pass: upload/page59-97.pdf',
 'source_does_not_include':'The re-uploaded file page59-97(1).pdf is currently inaccessible; this file is not used.',
 'book':'Rigaux, Scholl and Voisard (2002), Spatial Databases: With Application to GIS',
 'chapter':'Chapter 2, Representation of Spatial Objects',
 'printed_pages':'29–67',
 'verified_structure':[
  {'section':'2.1 Geographic Space Modeling','printed_pages':'31–34'},
  {'section':'2.1.1 Entity-Based Models','printed_pages':'31–33'},
  {'section':'2.1.2 Field-Based Models','printed_pages':'34'},
  {'section':'2.2.1 Tessellation','printed_pages':'35–37'},
  {'section':'2.2.2 Vector Mode','printed_pages':'38–42'},
  {'section':'2.2.3 Half-Plane Representation','printed_pages':'42–46'},
  {'section':'2.3.1 Spaghetti Model','printed_pages':'47–48'},
  {'section':'2.3.2 Network Model','printed_pages':'47–49'},
  {'section':'2.3.3 Topological Model','printed_pages':'49–51'},
  {'section':'2.4.2 The TIGER/Line Format','printed_pages':'54–61'},
  {'section':'2.5 Bibliographic Notes','printed_pages':'64–67'},
 ],
 'changes':revision,
 'bibliography_record':'[1] is a cited chapter within the authored book, not a standalone book title.',
 'unchanged_references':'[2]–[22] preserved; no renumbering.',
}
(DIR/'chapter2_citation_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Changes:', {key:len(val) for key,val in revision.items()})
print('Bibliography 1:',ref['text'])
