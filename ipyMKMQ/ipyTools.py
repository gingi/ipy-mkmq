#!/usr/bin/env python

from time import localtime, strftime
from collections import defaultdict
import os, sys, urllib, urllib2, json, pickle, copy
import string, random, re
import rpy2.robjects as ro
import retina, flotplot

# class for ipy lib env
class Ipy(object):
    """Constants for ipy-qmqc library interface"""
    FL_PLOT = None
    RETINA  = None
    DEBUG   = False
    NB_DIR  = None
    LIB_DIR = None
    TMP_DIR = None
    CCH_DIR = None
    IMG_DIR = None
    VALUES  = ['abundance', 'evalue', 'identity', 'length']
    TAX_SET = ['domain', 'phylum', 'class', 'order', 'family', 'genus', 'species']
    ONT_SET = ['level1', 'level2', 'level3', 'function']
    MD_CATS = ['project', 'sample', 'library', 'env_package']
    MATRIX  = { 'annotation': 'organism',
                'level': 'strain',
                'result_type': 'abundance',
                'source': 'M5NR',
                'e_val': 5,
                'ident': 60,
                'alen': 15,
                'filters': [],
                'filter_source': None }
    RETINA_URL = 'http://raw.github.com/MG-RAST/Retina/master/'
    API_URL = 'http://api.metagenomics.anl.gov/api2.cgi/'
    COLORS  = [ "#3366cc",
                "#dc3912",
                "#ff9900",
                "#109618",
                "#990099",
                "#0099c6",
                "#dd4477",
                "#66aa00",
                "#b82e2e",
                "#316395",
                "#994499",
                "#22aa99",
                "#aaaa11",
                "#6633cc",
                "#e67300",
                "#8b0707",
                "#651067",
                "#329262",
                "#5574a6",
                "#3b3eac",
                "#b77322",
                "#16d620",
                "#b91383",
                "#f4359e",
                "#9c5935",
                "#a9c413",
                "#2a778d",
                "#668d1c",
                "#bea413",
                "#0c5922",
                "#743411" ]

def init_ipy(debug=False, nb_dir=None, api_url=None):
    # set pathing
    if nb_dir and os.path.isdir(nb_dir):
        Ipy.NB_DIR = nb_dir
    else:
        Ipy.NB_DIR = os.getcwd()
    Ipy.LIB_DIR = Ipy.NB_DIR+'/lib'
    Ipy.TMP_DIR = Ipy.NB_DIR+'/tmp'
    Ipy.CCH_DIR = Ipy.NB_DIR+'/cache'
    Ipy.IMG_DIR = Ipy.NB_DIR+'/images'
    for d in (Ipy.LIB_DIR, Ipy.TMP_DIR, Ipy.IMG_DIR):
        if not os.path.isdir(d):
            os.mkdir(d)
    # set api
    if api_url is not None:
        Ipy.API_URL = api_url
    # set graphing tools
    Ipy.FL_PLOT = flotplot.FlotPlot()
    Ipy.RETINA  = retina.Retina()
    Ipy.DEBUG   = debug
    # load matR and extras
    ro.r('suppressMessages(library(matR))')
    ro.r('suppressMessages(library(gplots))')
    ro.r('suppressMessages(library(scatterplot3d))')
    # echo
    if Ipy.DEBUG:
        for k in Ipy.__dict__.keys():
            print k, getattr(Ipy, k)

def save_object(obj, name):
    """save some object to python pickle file"""
    fpath = Ipy.CCH_DIR+'/'+name+'.pkl'
    try:
        pickle.dump(obj, open(fpath, 'w'))
    except:
        sys.stderr.write("Error: unable to save '%s' to %s \n"%(obj.defined_name, fpath))
    return fpath

def load_object(name):
    """load object from python pickle file"""
    fpath = Ipy.CCH_DIR+'/'+name+'.pkl'
    if os.path.isfile(fpath):
        return pickle.load(open(fpath, 'r'))
    else:
        sys.stderr.write("can not create from pickeled object, %s does not exist\n"%fpath)
        return None

def google_palette(num):
    if not num:
        return Ipy.COLORS
    num_colors = []
    for i in range(num):
        c_index = i % len(Ipy.COLORS);
        num_colors.append( Ipy.COLORS[c_index] )
    return num_colors

def obj_from_url(url):
    if Ipy.DEBUG:
        sys.stdout.write(url+"\n")
    try:
        req = urllib2.Request(url, headers={'Accept': 'application/json'})
        res = urllib2.urlopen(req)
    except urllib2.HTTPError, error:
        sys.stderr.write("ERROR (%s): %s\n"%(url, error.read()))
        return None
    if not res:
        sys.stderr.write("ERROR (%s): no results returned\n"%url)
        return None
    obj = json.loads(res.read())
    if not obj:
        sys.stderr.write("ERROR (%s): return structure not valid json format\n"%url)
        return None
    if 'ERROR' in obj:
        sys.stderr.write("ERROR (%s): %s"%(url, obj['ERROR']))
        return None
    return obj

def slice_column(matrix, index):
    data = []
    for row in matrix:
        data.append(row[index])
    return data

def toNum(s):
    s = str(s)
    try:
        return int(s)
    except ValueError:
        return float(s)

def matrix_from_file(fname, has_col_names=True, has_row_names=True):
    fhdl = open(fname, 'rU')
    matrix = []
    if has_col_names:
        fhdl.readline()
    for line in fhdl:
        row = line.strip().split("\t")
        if has_row_names:
            row.pop(0)
        matrix.append( map(lambda x: toNum(x), row) )
    fhdl.close()
    return matrix

def ordered_distance_from_file(fname):
    fhdl  = open(fname, 'rU')
    line1 = fhdl.readline()
    line2 = fhdl.readline()
    order_dist  = map(lambda x: toNum(x), line1.strip().split(','))
    dist_matrix = []
    for line in fhdl:
        row = map(lambda x: toNum(x), line.strip().split())
        dist_matrix.append(row)        
    fhdl.close()
    return order_dist, dist_matrix

def sparse_to_dense(sMatrix, rmax, cmax):
    dMatrix = [[0 for i in range(cmax)] for j in range(rmax)]
    for sd in sMatrix:
        r, c, v = sd
        dMatrix[r][c] = v
    return dMatrix

def pyMatrix_to_rMatrix(matrix, rmax, cmax, normalize=0):
    if (not matrix) or (len(matrix) == 0):
        return None
    mList = []
    for i in range(cmax):
        if normalize:
            cList = map(lambda x: float(x[i]), matrix)
        else:
            cList = map(lambda x: int(x[i]), matrix)
        mList.extend(cList)
    if normalize:
        return ro.r.matrix(ro.FloatVector(mList), nrow=rmax)
    else:
        return ro.r.matrix(ro.IntVector(mList), nrow=rmax)

def rMatrix_to_pyMatrix(matrix, rmax, cmax):
    if (not matrix) or (len(matrix) == 0):
        return None
    pyM = [[0 for i in range(cmax)] for j in range(rmax)]
    col = 0
    for i in range(len(matrix)):
        row = i - (rmax * col)
        pyM[row][col] = matrix[i] 
        if row == (rmax-1):
            col += 1
    return pyM

def random_str(size=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for x in range(size))

def sub_biom(b, text):
    str_re = re.compile(text, re.IGNORECASE)
    sBiom = { "generated_by": b['generated_by'],
               "matrix_type": 'dense',
               "date": strftime("%Y-%m-%dT%H:%M:%S", localtime()),
               "data": [],
               "rows": [],
               "matrix_element_value": b['matrix_element_value'],
               "matrix_element_type": b['matrix_element_type'],
               "format_url": "http://biom-format.org",
               "format": "Biological Observation Matrix 1.0",
               "columns": b['columns'],
               "id": b['id']+'_sub_'+text,
               "type": b['type'],
               "shape": [] }
    hier = ''
    if b['type'].startswith('Taxon'):
        hier = 'taxonomy'
    elif b['type'].startswith('Function'):
        hier = 'ontology'
    seen = set()
    matrix = b['data'] if b['matrix_type'] == 'dense' else sparse_to_dense(b['data'], b['shape'][0], b['shape'][1])
    for r, row in enumerate(b['rows']):
        name = None
        if row['metadata'] and hier and (hier in row['metadata']) and str_re.search(row['metadata'][hier][-1]):
            name = row['metadata'][hier][-1]
        elif str_re.search(row['id']):
            name = row['id']
        if (name is not None) and (name not in seen):
            sBiom['data'].append(matrix[r])
            sBiom['rows'].append(row)
            seen.add(name)
    sBiom['shape'] = [len(sBiom['rows']), b['shape'][1]]
    return biom_remove_empty(sBiom)

def merge_cols(b, merge_set):
    """input: biom object, merge_set -> { merge_name_1 : [list of col ids], merge_name_2 : [list of col ids], ... }"""
    if not (merge_set and (len(merge_set) > 0)):
        sys.stderr.write("No merge set inputted\n")
        return None
    new_data = []
    new_cols = []
    seen = []
    # create new col set / test for duplicate merge ids
    for name, ids in merge_set.iteritems():
        if [i for i in ids if i in seen]:
            sys.stderr.write("Can not merge same column in more than 1 group\n")
            return None
        seen.extend(ids)
        new_cols.append({'id': name, 'name': name, 'metadata': {'components': ids}})
    # add singlets
    for c in b['columns']:
        if c['id'] not in seen:
            new_cols.append(c)
    # merge cols in data
    for row in b['data']:
        row_map = dict([(x['id'], 0) for x in new_cols])
        new_row = []
        for c, col in enumerate(b['columns']):
            if col['id'] in new_cols:
                row_map[col['id']] = row[c]
            else:
                for name, ids in merge_set.iteritems():
                    if col['id'] in ids:
                        row_map[name] += row[c]
                        break
        # re-order row
        for col in new_cols:
            new_row.append( row_map[col['id']] )
        new_data.append(new_row)
    new_b = copy.deepcopy(b)
    new_b['columns'] = new_cols
    new_b['data'] = new_data
    return new_b

def merge_biom(b1, b2):
    if b1 and b2 and (b1['type'] == b2['type']) and (b1['matrix_type'] == b2['matrix_type']) and (b1['matrix_element_type'] == b2['matrix_element_type']) and (b1['matrix_element_value'] == b2['matrix_element_value']):
        mBiom = { "generated_by": b1['generated_by'],
                   "matrix_type": 'dense',
                   "date": strftime("%Y-%m-%dT%H:%M:%S", localtime()),
                   "data": [],
                   "rows": [],
                   "matrix_element_value": b1['matrix_element_value'],
                   "matrix_element_type": b1['matrix_element_type'],
                   "format_url": "http://biom-format.org",
                   "format": "Biological Observation Matrix 1.0",
                   "columns": [],
                   "id": b1['id']+'_'+b2['id'],
                   "type": b1['type'],
                   "shape": [] }
        cols, rows = merge_matrix_info(b1['columns'], b2['columns'], b1['rows'], b2['rows'])
        merge_func = merge_sparse if b1['matrix_type'] == 'sparse' else merge_dense
        mCol, mRow, mData = merge_func([b1['data'], b2['data']], cols, rows)
        mBiom['columns']  = mCol
        mBiom['rows']     = mRow
        mBiom['data']     = mData
        mBiom['shape']    = [ len(mRow), len(mCol) ]
        return biom_remove_empty(mBiom)
    else:
        sys.stderr.write("The inputed biom objects are not compatable for merging\n")
        return None

def merge_matrix_info(c1, c2, r1, r2):
    ## merge columns, skip duplicate
    cm = {}
    for i, c in enumerate(c1):
        cm[ c['id'] ] = [0, i, c]
    for i, c in enumerate(c2):
        if c['id'] in cm:
            continue
        cm[ c['id'] ] = [1, i, c]
    ## merge rows
    rm = defaultdict(list)
    for i, r in enumerate(r1):
        rm[ r['id'] ].append( [0, i, r] )
    for i, r in enumerate(r2):
        rm[ r['id'] ].append( [1, i, r] )
    return cm.values(), rm.values()

def merge_sparse(data, cols, rows):
    for i in range(len(data)):
        data[i] = sparse_to_dense(data[i], len(rows), len(cols))
    return merge_dense(data, cols, rows)
    
def merge_dense(data, cols, rows):
    cm = map(lambda x: x[2], cols)
    rm = map(lambda x: x[0][2], rows)
    mm = [[0 for i in range(len(cols))] for j in range(len(rows))]
    for i, rset in enumerate(rows):
        for r in rset:
            for j, c in enumerate(cols):
                if r[0] == c[0]:
                    mm[i][j] += data[ r[0] ][ r[1] ][ c[1] ]
    return cm, rm, mm

def biom_remove_empty(b):
    vRows = []
    vCols = []
    if b['matrix_type'] == 'sparse':
        b['data'] = sparse_to_dense(b['data'], b['shape'][0], b['shape'][1])
        b['matrix_type'] = 'dense'
    for i, r in enumerate(b['rows']):
        row = b['data'][i]
        if sum(row) > 0:
            vRows.append(i)
    for j, c in enumerate(b['columns']):
        col = map(lambda x: x[j], b['data'])
        if sum(col) > 0:
            vCols.append(j)
    if len(vRows) < len(b['rows']):
        sub_rows = []
        sub_data = []
        for r in vRows:
            sub_rows.append(b['rows'][r])
            sub_data.append(b['data'][r])
        b['rows'] = sub_rows
        b['data'] = sub_data
    if len(vRows) < len(b['columns']):
        sub_cols = []
        sub_data = []
        for c in vCols:
            sub_cols.append(b['columns'][c])
        for row in b['data']:
            sub_row = []
            for c in vCols:
                sub_row.append(row[c])
            sub_data.append(sub_row)
        b['columns'] = sub_cols
        b['data'] = sub_data
    return b

def get_hierarchy(htype='taxonomy', level='species', parent=None):
    if htype == 'organism':
        htype = 'taxonomy'
    if htype == 'function':
        htype = 'ontology'
    params = [('min_level', level)]
    if parent is not None:
        params.append(('parent_name', parent))
    return obj_from_url(Ipy.API_URL+'m5nr/'+htype+'?'+urllib.urlencode(params, True))

def get_taxonomy(level='species', parent=None):
    return get_hierarchy(htype='taxonomy', level=level, parent=parent)

def get_ontology(level='function', parent=None):
    return get_hierarchy(htype='ontology', level=level, parent=parent)

def parent_level(level, htype='taxonomy'):
    if htype == 'organism':
        htype = 'taxonomy'
    hierarchy = Ipy.TAX_SET if htype == 'taxonomy' else Ipy.ONT_SET
    try:
        index = hierarchy.index(level)
    except (ValueError, AttributeError):
        return None
    if index == 0:
        return None
    return hierarchy[index-1]

def child_level(level, htype='taxonomy'):
    if htype == 'organism':
        htype = 'taxonomy'
    hierarchy = Ipy.TAX_SET if htype == 'taxonomy' else Ipy.ONT_SET
    try:
        index = hierarchy.index(level)
    except (ValueError, AttributeError):
        return None
    if index == (len(hierarchy)-1):
        return None
    return hierarchy[index+1]
