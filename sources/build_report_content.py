from pathlib import Path
import json, re

BASE = Path(__file__).resolve().parents[1]
SRC = BASE / 'sources'
RESULTS = BASE / 'experiments/results'
e1 = json.loads((RESULTS/'e1_topology.json').read_text(encoding='utf-8'))
e2 = json.loads((RESULTS/'e2_summary.json').read_text(encoding='utf-8'))
e3 = json.loads((RESULTS/'e3_summary.json').read_text(encoding='utf-8'))
env = json.loads((RESULTS/'environment.json').read_text(encoding='utf-8'))

blocks = []
def h(text, level=1): blocks.append(dict(type='heading', level=level, text=text))
def p(text): blocks.append(dict(type='paragraph', text=text))
def table(caption, headers, rows, widths=None):
    b=dict(type='table',caption=caption,headers=headers,rows=rows)
    if widths: b['widths']=widths
    blocks.append(b)
def fig(file,caption,width=6.55): blocks.append(dict(type='figure',file=file,width=width,caption=caption))
def eq(tex,label,note): blocks.append(dict(type='equation',tex=tex,label=label,note=note))
def code(caption,lines): blocks.append(dict(type='code',caption=caption,lines=lines))
def num(x, nd=0): return f'{x:,.{nd}f}'
def prof(x): return x.replace('GeoParquet-', 'GeoParquet ')

h('5 Experimental Method')
p('Three experiments were designed to connect the concepts of Chapter 2 directly with the behavior of modern formats. E1 examines shared boundaries and consistency during updates. E2 compares the size and processing time of a complete object collection whose geometry is preserved. E3 examines tile-based delivery and the quantization error of MVT. Separating the three problems avoids comparing a complete dataset with a set of display fragments and then treating them as equivalent products.')
p('These are actual runs on synthetic data, in the computing environment used to prepare the report, on November 2, 2026. Data, code, configuration, logs and per-repetition results are stored in the reproduction package. The figures are not field measurements, are not taken from the cited papers, and are not yet considered results the group ran on its own machine. The method draws on how [10] identifies processing pipelines and how [11], [12] separate data loading from display; the design here has its own scale and scope.')
h('Data and runtime environment',2)
p('The data consist of two-dimensional polygon partitions in the longitude range 105.75–105.87 and latitude range 20.95–21.07, in OGC:CRS84. The three scales are 100 objects on a 10 × 10 grid, 1,000 objects on a 25 × 40 grid and 10,000 objects on a 100 × 100 grid. Each ring has 17 coordinate pairs, including the closing point. An object has two integer attributes: a unique id, and class, the remainder of the sum of the row and column indices divided by 5. Geometry is created before the timed interval.')
p('Each interior grid edge has four segments and a zigzag offset of 6% of the cell size; two adjacent polygons use exactly the same coordinate sequence, reversed when necessary. This design preserves shared boundaries and reduces the risk of confusing arc sharing with the removal of collinear vertices. The outer boundary remains straight, so the effect of removing collinear vertices is not fully eliminated. Coordinates are rounded to 12 decimal places to make the data deterministic; this figure does not describe real-world survey precision.')
p('The run used Python 3.12.14 on Linux x86_64. The host reports an AMD EPYC 9V74 CPU, but the environment was granted only a quota equivalent to 8 CPUs and a memory limit of 8 GiB; this is not to be read as a test using all 80 cores named by the CPU. The main libraries are Shapely 2.2.0, GEOS 3.14.1, GeoPandas 1.2.0, PyArrow 26.0.0, topojson 2.2, mapbox-vector-tile 2.2.0, pyproj 3.8.0 and PROJ 9.8.1. The file environment.json records all versions and the start and end times in UTC.')
h('E1 Shared boundaries, gaps and updates',2)
p('Experiment E1 uses two adjacent polygons in four scenarios. First, the two boundaries match exactly. Second, polygon B is shifted by 10⁻⁶ degrees of longitude in the direction that creates a gap. Third, a single mid-boundary vertex of A alone is moved by a further 10⁻⁴ degrees in GeoJSON. Fourth, the same position is moved on the arc referenced by both A and B in TopoJSON. The two endpoints connecting to other arcs stay fixed. TopoJSON quantization and simplification are both disabled.')
p('The TopoJSON library may remove collinear vertices in the two rectangles. Therefore, before the edit, the code reinserts the intermediate vertices on the arc so that both update methods act on the same position. The touch relation is checked on the original geometry; illustrative distance, length and area are computed after projecting to UTM 48N, EPSG:32648. The metrics are the number of shared arcs, validity, touching, distance and overlap area. The test covers only this specific operation and does not assume that every arc edit is valid.')
h('E2 Size and processing of the complete dataset',2)
table('Table 4 Encoding configurations in experiment E2',
      ['Configuration','Encoding and attributes','Control settings'],[
      ['GeoJSON','Compact UTF-8 FeatureCollection; numeric id and class','Round-trip floating-point coordinates; no simplification'],
      ['TopoJSON','Shared arcs; id and class attributes','prequantize, topoquantize, presimplify, toposimplify disabled'],
      ['KML','Polygon; Schema and int SimpleField for both attributes','No altitude; clampToGround; round-trip floating-point'],
      ['GeoParquet NONE','WKB; schema 1.1.0; no column compression codec','No index written; row group 1,000'],
      ['GeoParquet ZSTD','Same data and schema as NONE; ZSTD codec','Only the codec setting changes; geometry unchanged']
      ],[0.22,0.38,0.40])
p('The configurations are based on specifications [15]–[19]. Raw files are measured in bytes. A separate size measurement compresses each whole file with gzip level 6 and mtime set to 0. External gzip and ZSTD inside Parquet are two different mechanisms: the GeoParquet ZSTD file in the “file” column is already compressed internally; its gzip column is an additional compression reported for transparency, not a deployment recommendation.')
p('The read path of every configuration ends in the same form of result: a complete list of records holding id as int, class as int, and a constructed Shapely geometry. Thus no configuration reads only metadata while another must build all geometry. However, the readers differ: KML uses lxml, GeoParquet uses GeoPandas/PyArrow, and TopoJSON uses the Polygon decoder shipped with the experiment code. The measured times reflect these specific pipelines, including library costs.')
p('Each configuration has one correctness-check pass and one untimed warm-up pass, followed by five measurements. The order of configurations is shuffled within each repetition using seed 20261102. The clock is time.perf_counter_ns; garbage collection is invoked outside the timed interval. Write time covers building the target structure, encoding, writing and closing the file, but no fsync, so it does not represent durable write latency to the device. Read time covers opening the file, reading, decoding and creating geometry.')
p('The operating system cache is warm and is not cleared; each read follows a write of the same configuration. The report uses the median and Q1–Q3 range of the five runs as descriptive statistics and performs no significance testing. E2 produces 75 measurement rows, corresponding to three scales × five configurations × five repetitions; each row holds both write and read times. The costs of generating data and checking results are outside the timed interval.')
p('Post-read checks cover the object count, unique and matching ids, correct attribute values and integer types, valid and non-empty geometry, topological equality, maximum Hausdorff distance and area deviation. Hausdorff uses the discrete GEOS/Shapely measure without added densification. The check threshold is set at 10⁻¹² degrees; the report presents the measured deviation rather than substituting the threshold for it. “Lossless” in E2 means only that the geometric point set and the checked attributes are preserved; it does not require preserving vertex order or the number of collinear vertices.')
h('E3 Vector Tiles by zoom level and viewport',2)
p('E3 uses 10,000 objects, projected to EPSG:3857, with the XYZ scheme, extent 4096 and buffer 0, at zoom levels 11, 13 and 15. This is the configuration of the test, not a set of coordinate systems or parameters mandated by MVT [18]. No line simplification is applied. Polygons are clipped at tile boundaries; only Polygon or MultiPolygon fragments with positive area are kept, then quantized to the nearest integer grid and encoded with mapbox-vector-tile.')
p('The viewport lies at the center of the domain, one quarter of the domain width and one quarter of its height, so its area is one sixteenth. A tile is selected when it intersects the viewport; all objects in a selected tile are read. Therefore the number of ids received can exceed the number of objects that actually intersect the viewport. The report separates the number of tiles, the number of geometry fragments and the number of unique ids. The gzip total is obtained by compressing each tile and summing the bytes, not by compressing the whole directory as one stream.')
p('After decoding, coordinates are mapped through a global integer grid before conversion to floating point, so that the same node in two adjacent tiles has the same numeric value. Fragments with the same id are merged to check geometry, attributes and error against the source. Hausdorff error is measured in meters in the Mercator coordinate system; it is not to be interpreted directly as distance on the ground. The area difference ratio is defined per object as follows.')
eq(r'E_A=\frac{\sum_{i=1}^{n}\operatorname{area}(P_i\triangle\widehat{P}_i)}{\sum_{i=1}^{n}\operatorname{area}(P_i)}\times100\%', '5',
   'Pᵢ is the source polygon and P̂ᵢ the polygon after merging fragments; △ is the symmetric difference. Area is computed in EPSG:3857. A region reassigned between two objects may contribute to the numerator of both; this is not the difference between the outlines of the union of the whole map.')
p('Decoding time has one warm-up and five measured repetitions, covering local file reads, Protocol Buffers decoding, Shapely geometry creation and coordinate conversion. Tile build time is measured only once as an operational log entry and is not used as stable comparative evidence. E3 does not measure the network, HTTP, browsers, map drawing or user interaction. Because of clipping and quantization, MVT is evaluated separately rather than placed in the E2 tables as an equivalent complete copy.')

h('6 Experimental Results')
h('E1 Boundary sharing supports updates but does not repair data',2)
table('Table 5 Results of the four shared-boundary scenarios',
 ['Scenario','Shared arcs','Relation after processing','Main quantity'],[
 ['Exactly matching boundary','1 of 3 arcs','The two polygons touch; both valid','Distance 0 m; overlap 0 m²'],
 ['10⁻⁶ degree gap','0 of 2 arcs','Not touching; both valid','Gap of 0.103930 m remains'],
 ['Edit A alone in GeoJSON','Stored separately','Overlapping; each polygon valid','Overlap area 2,875.871 m²'],
 ['Edit shared arc in TopoJSON','1 of 3 arcs','Still touching; both valid','Overlap area 0 m²']
 ],[0.29,0.15,0.29,0.27])
p('With matching input boundaries, TopoJSON creates one shared arc referenced by both polygons; the touch relation holds after reading back. With an input gap of about 0.104 m, converting to TopoJSON neither creates a shared arc nor removes the gap. This result refutes the reading that the name “topology” by itself guarantees correct data: the storage structure and the process of checking and repairing are separate tasks.')
p('The independent edit creates an overlap although both polygons remain individually valid. Therefore an is_valid check per object is not enough to guarantee a non-overlapping partition. The shared-arc edit keeps the two boundaries coincident, with no overlap in this case. The observed benefit comes from both objects referencing the same boundary data; checks for self-intersection, ring inversion or collision with other edges are still needed after more complex edits.')
h('E2 Size and speed depend on configuration and scale',2)
p('All 15 combinations of scale and configuration retain every object, id and class; all geometry read back is valid, non-empty and topologically equal to the source. The largest measured Hausdorff distance is 0 degrees. The largest relative area deviation of TopoJSON is approximately 2.26 × 10⁻¹⁶, consistent with the effect of floating-point arithmetic; the other configurations have a value of 0 in this measurement set. This is the condition for comparing performance on the same geometric information.')
big=[r for r in e2 if r['n']==10000]
table('Table 6 Size and median time with 10,000 polygons',
 ['Configuration','File bytes','Gzip6 bytes','Write ms','Read ms'],
 [[prof(r['profile']),num(r['raw_bytes']),num(r['gzip6_bytes']),num(r['write_ms']['median'],3),num(r['read_ms']['median'],3)] for r in big],
 [0.27,0.19,0.19,0.18,0.17])
p('Tables 5–10 and Figures 4–5 come from the run accompanying the report. The “file” column of GeoParquet ZSTD already includes column compression. The values in Table 6 are medians of five measurements, not the time of one repetition chosen for illustration.')
table('Table 7 Q1 to Q3 range of times at 10,000 polygons',
 ['Configuration','Write Q1–Q3 ms','Read Q1–Q3 ms'],
 [[prof(r['profile']),num(r['write_ms']['q1'],3)+'–'+num(r['write_ms']['q3'],3),num(r['read_ms']['q1'],3)+'–'+num(r['read_ms']['q3'],3)] for r in big],
 [0.34,0.33,0.33])
p('At 10,000 objects, TopoJSON reduces file size by 33.70% and gzipped size by 18.29% compared with GeoJSON. The structure has 20,196 arcs, of which 19,800 are shared, with 99,796 coordinate pairs in the arcs; GeoJSON holds 170,000 ring coordinate pairs. The byte reduction does not equal the reduction in coordinates, because of arc indexes, JSON structure and attributes. Some collinear vertices on the outer boundary may be removed without changing the geometry; hence not all of the saving is attributed to arc sharing.')
p('Smaller size does not come with shorter write time. Building and writing TopoJSON takes a median of 5,313.076 ms, against 321.825 ms for GeoJSON in this pipeline. The raw KML file is larger than GeoJSON, but after gzip the two sizes are close: 546,117 and 538,339 bytes. Looking only at the raw file overlooks how well repeated text structures compress.')
profiles=[r['profile'] for r in big]
table('Table 8 Median read time by data scale',
 ['Configuration','100 objects ms','1,000 objects ms','10,000 objects ms'],
 [[prof(pr)]+[num(next(r for r in e2 if r['n']==n and r['profile']==pr)['read_ms']['median'],3) for n in (100,1000,10000)] for pr in profiles],
 [0.29,0.23,0.24,0.24])
p('GeoParquet ZSTD reads 10,000 objects in 50.761 ms, below the 323.879 ms of GeoJSON in the measured environment. However, with 100 objects, GeoJSON needs only 2.774 ms while GeoParquet ZSTD needs 35.265 ms. The reversal is consistent with the costs of opening, interpreting metadata and creating intermediate structures possibly dominating small datasets. The 1,000-object result further shows that an exact crossover threshold should not be inferred from only three scale points. Further measurement is meaningful only once the data type and pipeline of a specific application are defined.')
fig('figures/fig04_results_e2.png','Figure 4 Size at 10,000 objects and read time by scale. The time chart uses the median and Q1–Q3 range of five repetitions; log scales are marked on the axes. Source: experiment E2.')
h('E3 Small tiles reduce over-fetching but increase the full-domain tile count',2)
table('Table 9 MVT tile counts and data volume by viewport',
 ['Zoom','Full-domain and viewport tiles','Full-domain gzip bytes','Viewport gzip bytes','IDs received in viewport tiles'],
 [[str(r['zoom']),f"{r['tile_count_all']} / {r['tile_count_view']}",num(r['gzip6_bytes_all']),num(r['gzip6_bytes_view']),num(r['unique_source_ids_view'])] for r in e3],
 [0.09,0.24,0.22,0.22,0.23])
p('The viewport actually intersects only 676 source objects. All three zoom levels retrieve these 676 ids, but the number of ids in the tiles to be read is 9,100, 5,175 and 1,295 respectively. The reason is that a tile can extend far beyond the viewport. Hence a viewport covering one sixteenth of the area does not mean reading only one sixteenth of the bytes. The number of fragments in the viewport tiles is larger still than the number of ids because an object may cross a tile boundary: 9,191, 5,320 and 1,520 fragments respectively.')
p('Going from zoom 11 to 15, the full-domain tile count rises from 4 to 156 and the full-domain gzip total rises from 128,913 to 311,855 bytes. Meanwhile, the gzip needed for the viewport falls from 114,625 to 35,424 bytes. These two quantities reflect two different goals: storing or reading the whole map, and retrieving only the area being viewed. For a specific viewport, many small tiles can reduce over-fetching, but this alone says nothing about connection costs or interaction latency.')
table('Table 10 MVT error and viewport decoding time',
 ['Zoom','Grid step m Mercator','Max Hausdorff m Mercator','Area difference %','Median decoding ms'],
 [[str(r['zoom']),num(r['grid_unit_mercator_m'],6),num(r['max_hausdorff_mercator_m'],6),num(100*r['relative_symmetric_difference_area'],6),num(r['decode_view_ms']['median'],3)] for r in e3],
 [0.09,0.22,0.25,0.21,0.23])
p('All 10,000 ids are recovered from the full-domain tiles, attributes match and the merged polygons are valid. Even so, the geometry has changed through quantization. Discrete Hausdorff falls from 3.371148 m Mercator at zoom 11 to 0.209441 m at zoom 15; the area difference ratio of Equation 5 falls from 2.711787% to 0.174150%. This illustrates that validity and id preservation are not the same as keeping the geometry unchanged.')
p('The viewport decoding time has a Q1–Q3 range of 659.707–751.373 ms at zoom 11; 386.291–390.163 ms at zoom 13; and 85.931–89.362 ms at zoom 15. Fewer fragments to read is consistent with lower decoding time. These times cannot be used to conclude directly about drawing speed or the advantage of a web library; those quantities require a separate measurement design as in [11], [12].')
fig('figures/fig05_results_mvt.png','Figure 5 MVT shows the trade-off between size by read domain and quantization error. The error is a discrete measure in the Mercator system; the area ratio follows Equation 5. Source: experiment E3.')

h('7 Discussion and Limitations')
h('From model to usage decision',2)
p('The first question is answered by distinguishing three layers. The entity or field model determines what counts as the object of study. Raster, vector, TIN or half-planes determine how geometry or spatial values are described. Spaghetti, network and topology determine how relations among components are organized. Formats then specify how these are encoded and exchanged. Using vector coordinates in common does not make GeoJSON, TopoJSON, KML, MVT and GeoParquet serve the same data contract [1]–[3], [15]–[19].')
p('The second question must be assessed by the invariants to be kept. When managing boundaries, the invariant may be that a shared edge has a single update source and that the partition has no gaps or overlaps. When exchanging records, the invariants are id, attributes, geometry type and CRS. When displaying by tile, the contract may accept clipping, reduced detail and quantization at a suitable error level. The conditions to keep must be stated before conversion and exactly those conditions checked afterward, rather than only checking that the file opens.')
table('Table 11 Suggested choices by task and conditions to check',
 ['Task','Option worth considering','Conditions to check'],[
 ['Exchanging objects through services or processing small sets','GeoJSON','Longitude-latitude order, null values, digit count, attribute preservation'],
 ['Sharing the boundaries of a partition','TopoJSON or a database with topology','Noding, coincident boundaries, shared arcs, validity after edits'],
 ['Exchanging data with presentation on a map or globe','KML or KMZ','Attribute types, altitudeMode, height system and software support'],
 ['Displaying maps by viewport and at many zoom levels','Vector Tiles with tiling rules and a delivery service','CRS, extent, buffer, geometry loss, cross-tile ids and over-fetching'],
 ['Batch analysis of geographic tables or access to some columns','GeoParquet','Schema version, CRS, codec, row group, metadata and reader capability']
 ],[0.29,0.33,0.38])
p('Table 11 is a conditional interpretation of the specifications and experiments, not a ranking of formats. A system may store an analytical dataset in GeoParquet, export GeoJSON for exchange, build MVT for display and maintain topology in the source database. In that case, consistency among the products depends on the data generation process, source versions and post-conversion checks; it is not guaranteed merely because all the products carry coordinates [14]–[20].')
h('Critique of easily mistaken interpretations',2)
p('A file with coordinate fields does not prove it is a geometric data source able to replace the original. MVT shows this clearly: all ids and attributes can remain intact while the boundaries have been quantized. Conversely, TopoJSON in E2 may change how arcs are divided or drop collinear vertices while remaining topologically equal with a Hausdorff distance of 0. Identity of coordinate sequences must be separated from equality of geometry.')
p('A smaller file does not automatically lead to faster operations either. E2 shows that building TopoJSON is costly, and E3 shows that decoding includes fragment handling and coordinate conversion. The results of Wachs and Tzirita Zacharatou [10] also place data loading in the context of a specific reader, scale and geometry. This report adds a small reproducible check; it does not replicate that study\'s design or confirm a ranking for all of its workloads.')
p('A format with bbox metadata does not necessarily have a complete spatial index. With GeoParquet, skipping row groups through metadata or statistics also depends on data layout and the reader [19]. E2 reads all data and does not measure bbox queries, column selection, peak memory or scanning from object storage. Hence the speed results here are not sufficient to confirm pruning effectiveness or cloud query costs.')
h('Limitations and future work',2)
p('The largest limitation is synthetic data with a regular structure, few attributes and many shared boundaries. It is useful for isolating the arc-sharing mechanism, but may favor compression more than point data, lines, polygons with many holes, complex administrative boundaries or long string attributes. Three scales up to only 10,000 objects do not represent national data. Measurement with a warm cache, no fsync and no isolation from host noise also limits how the times can be interpreted.')
p('In addition, the formats use different implementations, and the TopoJSON decoder in the test package serves only the generated Polygon case. It is not a conformance test suite for the full specification. The experiments do not cover 3D data, a time axis, null geometry, nested attributes, curves, geodetic error or complete metadata preservation for every format. Five repetitions support only descriptive statistics; they do not demonstrate statistically significant differences in other deployment environments.')
p('The next step should add a real dataset that is permitted for use, and publish its source, geometry types, CRS and processing steps. With boundary data, holes, multipart polygons, gaps and overlaps can also be tested; for map services, HTTP, memory and display time should be measured in the same application. When testing GeoParquet at large scale, full reads, column selection and spatial queries should be separated, with codec and row group layout recorded. These extensions answer new questions rather than prolonging the current measurement without changing its goal.')

h('8 Conclusion')
p('Representing spatial objects is a chain of related decisions: choosing an entity or field model, choosing a geometric representation, organizing relations, then choosing a format and delivery path. The knowledge of raster, vector, half-planes, spaghetti, network and topology in Chapter 2 still provides the basis for understanding modern technologies. TIGER/Line illustrates the value of combining geometry and relations, and shows the need to distinguish a source database from the products exported from it.')
p('The three experiments show that arc sharing supports consistent boundary editing but does not by itself fix gaps; that size and speed depend on scale, codec and pipeline; and that tiling helps reduce the data needed for a viewport but comes with clipping, quantization and over-fetching costs. Accordingly, selection criteria should start from the information to be preserved and the operations to be performed. The package of code, data and per-repetition results allows these conclusions to be checked and rerun with other data, software or environments.')

(SRC/'part3_experiments.json').write_text(json.dumps(blocks,ensure_ascii=False,indent=2),encoding='utf-8')

# Correct the general algorithm without confusing rings or complementary faces.
part1=json.loads((SRC/'part1_theory.json').read_text(encoding='utf-8'))
for b in part1:
    if b.get('caption','').startswith('Algorithm 2'):
        b['lines']=[
            'BUILD_SHARED_EDGES(polygons)',
            '    E <- empty dictionary',
            '    for each face f in polygons',
            '        for each ring r of f',
            '            for each oriented segment u -> v of r',
            '                reject zero-length segment',
            '                key <- (min_lex(u,v), max_lex(u,v))',
            '                if key not in E: E[key] <- empty edge',
            '                side <- LEFT if (u,v)==key else RIGHT',
            '                if E[key][side] assigned: reject conflict',
            '                E[key][side] <- f',
            '                append oriented reference to ring r',
            '    return E and references for each ring']
    if b.get('text','').startswith('DCEL in the paper'):
        b['text']='DCEL in the paper by Muller and Preparata organizes information through the fields V1, V2 for the two endpoints, F1, F2 for the two faces adjacent to the edge, and P1, P2 for links to the next edge around the two vertices [9, Sec. 2]. The explanation using two oppositely directed half-edges with origin, twin, next, prev and face links is a common implementation variant for understanding traversal. The field list of this variant should not be taken as a verbatim description of DCEL in the 1978 paper. Realms further raises the issue of a finite and consistent shared geometric domain; merely rounding coordinates is not equivalent to building a Realm [6].'
    if b.get('caption','').startswith('Figure 1 '):
        b['caption']='Figure 1 Panels a–c represent the same synthetic field through a function, a raster and a linearly interpolated TIN; panel d illustrates a separate set of entities. Original figure with illustrative data; conceptual frame based on [1]–[3].'
(SRC/'part1_theory.json').write_text(json.dumps(part1,ensure_ascii=False,indent=2),encoding='utf-8')

front=[
 dict(type='title',text='Representation of Spatial Objects'),
 dict(type='subtitle',text='A scientific report on the theoretical foundations and an experimental study of modern formats'),
 dict(type='metadata',text='Spatial Databases  |  Group 1  |  Chapter 2  |  November 2, 2026'),
 dict(type='heading',level=2,text='Abstract'),
 dict(type='paragraph',text='This report systematizes how spatial objects are represented, from entity and field models to raster, vector, half-planes, and spaghetti, network and topological structures. The main source is Chapter 2 of Spatial Databases: With Application to GIS, checked against original works, TIGER/Line and the GeoJSON, TopoJSON, KML, Vector Tiles and GeoParquet specifications. Three experiments were run on synthetic data: shared boundaries and updates; complete processing of 100–10,000 polygons; and MVT delivery by zoom level. At 10,000 polygons, TopoJSON reduces file size by 33.70% compared with GeoJSON but has a higher build cost. GeoParquet ZSTD reads faster than GeoJSON at this scale, while the order reverses at 100 objects. MVT reduces the data needed for a viewport as zoom increases, while exhibiting measured quantization error. The results show that the choice must be tied to the information to be preserved, the scale and the task. The measurements are descriptive statistics of the published pipelines, not a universal ranking of formats. Code, data and per-repetition results are provided for reproduction.'),
 dict(type='keywords',text='Keywords  spatial representation; entity and field models; topology; GeoJSON; TopoJSON; KML; vector tiles; GeoParquet.')]
(SRC/'front_matter.json').write_text(json.dumps(front,ensure_ascii=False,indent=2),encoding='utf-8')

appendix=[]
blocks=appendix
h('Appendix A Reproduction guide')
p('Extract the package Spatial_Representation_Sources_and_Data.zip. The experiments directory holds run_experiments.py, requirements.txt, README.md and the results of the run used in the report. No GIS service account is needed to run the synthetic dataset. Install the dependencies in a separate Python environment, then run from the experiments directory with the commands below.')
code('Commands to rerun the experiments',[
 'python3 -m venv .venv',
 'source .venv/bin/activate',
 'python -m pip install -r requirements.txt',
 'python run_experiments.py --output results_reproduced --repeats 5'])
p('On Windows, use the corresponding activation command .venv\\Scripts\\activate. Do not overwrite the original results directory if comparison is intended. Geometry and configuration are generated deterministically; times may vary with the machine, library versions and system load. When reporting a new run, keep the environment.json file and the measurement rows of that run, rather than replacing only the summary figures in the tables.')
p('The file e1_topology.json holds the four shared-boundary scenarios; e2_raw_timings.csv holds 75 write and read repetitions, and e3_raw_timings.csv holds 15 full-domain and viewport decoding repetitions. The e2_summary and e3_summary files come in both CSV and JSON. The results/data directory holds the actual files of each format and the PBF tiles. Detailed geometry checks and metadata fields are kept in JSON; CSV serves filtering and tabulation.')
p('The code theory_examples.py in the root directory checks the three states of half-plane classification, the invariance under multiplying the coefficients by the same positive number, and the edge table of the two squares. The run accompanying the report achieved 60 invariance comparisons, obtaining 6 vertices, 7 edges, left face A and right face B on the shared edge; with the outer face, V − E + F equals 2. The files figures/draw_theory_figures.py and figures/draw_result_figures.py rebuild the diagrams and charts.')
p('The sources directory stores the structured content, citation list and DOCX build program. The report\'s reference numbers are mapped in bibliography_report.json; these numbers should not be equated with the R codes of the previously downloaded reference PDF package. Rebuilding the DOCX/PDF requires additional publishing tools, separate from the GIS dependencies used to run the experiments.')
h('Appendix B Mapping to the evaluation criteria')
table('Table 12 Content addressing the provided evaluation framework',
 ['Criterion','Evidence in the report','Maximum points per the assignment'],[
 ['Core theory','Section 3; three original figures; two pieces of pseudocode; correctness conditions and verified examples','3.0'],
 ['Updates and experiments','Sections 4–7; five formats; three experiments actually run; code and raw data','3.0'],
 ['Scientific structure','Abstract, research questions, related work, method, results, discussion, conclusion','2.0'],
 ['References','Original book, original papers and official specifications; numbered citations with DOI or URL','1.0'],
 ['Timeliness','Submission dates of the outline, report and revised version must be checked against the instructor\'s deadlines','1.0']
 ],[0.24,0.59,0.17])
p('The mapping table only points to evidence and the assignment\'s maximum points; it does not self-grade or confirm on-time submission. Before submitting, the group must add member information according to the class template, check the page and deadline requirements, and rerun the experiments in the group\'s environment if the instructor requires direct evidence of installation and execution.')
(SRC/'appendices.json').write_text(json.dumps(appendix,ensure_ascii=False,indent=2),encoding='utf-8')

print('Created',len(json.loads((SRC/'part3_experiments.json').read_text(encoding='utf-8'))),'experiment/discussion blocks;',len(appendix),'appendix blocks')
