import os
import numpy as np
import pandas
import rasterio
from collections import defaultdict


def find_files(viirsdir):
    tifs = {}
    tuples = []
    tiftypes = set()
    for dirpath, dirnames, filenames in os.walk(viirsdir):
        if len(os.path.basename(dirpath)) == 4: # only do YYYYMM directories
            continue
        for filename in filenames:
            if filename[-4:] == '.tgz':
                continue
            parts = filename.split('_')
            tiftype = parts[6].split('.')[1]
            if tiftype not in tifs:
                tifs[tiftype] = {}
            year = int(parts[2][:4])
            if year not in tifs[tiftype]:
                tifs[tiftype][year] = {}
            month = int(parts[2][4:6])
            if month not in tifs[tiftype][year]:
                tifs[tiftype][year][month] = {}
            tile = parts[3]
            tuples.append((year, month, tile, tiftype))
            tifs[tiftype][year][month][tile] = os.path.join(dirpath, filename)
    mi = pandas.MultiIndex.from_tuples(tuples, names=['year', 'month', 'tile', 'kind'])
    s = pandas.Series(index=mi)
    for (year, month, tile, tiftype) in tuples:
        s[year, month, tile, tiftype] = tifs[tiftype][year][month][tile]
    return s.sort_index()


def avg_tiles(source, target, env):
    nmonths = env['nmonths']
    for i in range(nmonths):
        with rasterio.open(str(source[i])) as rast:
            monthavg = rast.read(1)
            meta = rast.meta
            del meta['transform']
        with rasterio.open(str(source[nmonths+i])) as rast:
            monthcount = rast.read(1)
        if i == 0:
            cumcount = monthcount.copy()
            cumsum = monthavg.copy() * cumcount
        else:
            cumsum += monthavg * monthcount
            cumcount += monthcount
    avg = np.zeros_like(cumsum) * np.nan
    avg[cumcount>0] = cumsum[cumcount>0] / cumcount[cumcount>0]
    avg[avg<0] = 0
    avg[np.isnan(avg)] = 0

    with rasterio.open(str(target[0]), 'w', **meta) as out:
        out.write(avg, 1)
    countmeta = meta.copy()
    countmeta['dtype'] = 'uint8'
    with rasterio.open(str(target[1]), 'w', **countmeta) as out:
        out.write(cumcount, 1)
    return 0


def write_grdImport_input(source, target, env):
    with open(str(target[0]), 'w') as fout:
            fout.write(str(env['dataformat']) + '\n')
            fout.write(str(env['nodata']) + '\n')
            fout.write(str(env['listfile']) + '\n')
            fout.write(env['outputfile'] + '\n')
            fout.write(str(env['gridtype']) + '\n')
    return 0


