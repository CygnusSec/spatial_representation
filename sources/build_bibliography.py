from pathlib import Path
import re,json
BASE=Path(__file__).resolve().parents[1]
source_bib=BASE/'report_references.bib'
if not source_bib.exists():source_bib=BASE.parent/'bibliography/group1_chapter2_references.bib'
raw=source_bib.read_text()
entries={}
for typ,key,body in re.findall(r'@(\w+)\{([^,]+),\n(.*?)\n\}',raw,re.S):
    f={k:v for k,v in re.findall(r'^\s+(\w+)\s*=\s*\{(.*)\},?$',body,re.M)}
    f.update(type=typ,key=key,archive_id=key[:3])
    entries[key[:3]]=f
ids=['R01','R02']+[f'R{i:02}' for i in range(6,25)]
out=[]
for n,rid in enumerate(ids,1):
    e=entries[rid]
    authors=e['author'].strip('{}').replace(' and ','; ')
    text=authors+'. '+e['title']+'. '
    if e['type']=='inbook':
        text=authors+'. “'+e['title']+'”. Chapter '+e.get('chapter','2')+' in '+e['booktitle']+'. '+e['publisher']+', '+e['year']+', pp. '+e.get('pages','29--67').replace('--','–')+' (printed page numbers of the book).'
    elif e['type']=='book':
        if 'edition' in e:text+='Edition '+e['edition']+'. '
        text+=e['publisher']+', '+e['year']+'.'
        if rid=='R01':text+=' Chapter 2, pp. 29–67 by printed page numbers; the excerpt provided by the student has 39 PDF pages.'
        if rid=='R02':text+=' Checked against the open-access chapter on spatial concepts.'
    elif e['type']=='article':
        text+=e['journal']+', '+e['year']+', '+e.get('volume','')
        if e.get('number'):text+='('+e['number']+')'
        text+=', '+e.get('pages','').replace('--','–')+'.'
    elif e['type']=='inproceedings':
        text+=e['booktitle']+', '+e['year']
        if e.get('volume'):text+=', vol. '+e['volume']
        text+=', pp. '+e['pages'].replace('--','–')+'.'
    else:
        if e.get('number'):text+='Document '+e['number']+'. '
        if rid=='R17':text+='Version 1.2.1. '
        if rid=='R21':text+='Version 2.1. '
        if rid=='R22':text+='Version 1.1.0. '
        if rid=='R23':text+='Version 1.0. '
        if e.get('year'):text+=e['year']+'.'
        else:text+='No publication year assigned because the source does not state one.'
    url='https://doi.org/'+e['doi'] if e.get('doi') else e['url']
    if rid=='R24':
        text+=' The official technical contents page was used; this does not claim access to the complete technical PDF.'
    if e['type'] in ('manual','techreport') or rid=='R02':
        text+=' Accessed November 2, 2026.'
    out.append(dict(number=n,archive_id=rid,key=e['key'],title=e['title'],text=text,url=url,original=e))
out.append(dict(number=22,archive_id='R25',key='R25_CensusProducts',title='TIGER Data Products Guide',
  text='U.S. Census Bureau. TIGER Data Products Guide. Official guide page for TIGER products. Accessed November 2, 2026.',
  url='https://www.census.gov/programs-surveys/geography/guidance/tiger-data-products-guide.html'))
(BASE/'sources/bibliography_report.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
selected=[]
for m in re.finditer(r'@(\w+)\{([^,]+),\n(.*?)\n\}',raw,re.S):
    if m.group(2)[:3] in ids:selected.append(m.group(0))
selected.append('@manual{R25_CensusProducts,\n  author = {{U.S. Census Bureau}},\n  title = {TIGER Data Products Guide},\n  url = {https://www.census.gov/programs-surveys/geography/guidance/tiger-data-products-guide.html},\n  urldate = {2026-11-02},\n}')
(BASE/'report_references.bib').write_text('% 22 sources cited in the report. Numbering order is in sources/bibliography_report.json.\n\n'+'\n\n'.join(selected)+'\n')
print('Bibliography:',len(out),'entries')
