import os
import numpy as np
import pandas
import rasterio
import datetime
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


def find_bm_files(viirsdir):
    tifs = defaultdict(dict)
    tuples = []
    for dirpath, dirnames, filenames in os.walk(viirsdir):
        for filename in filenames:
            parts = filename.split('_')
            year, tile = int(parts[1]), parts[2]
            tuples.append((year, tile))
            tifs[year][tile] = os.path.join(dirpath, filename)
    mi = pandas.MultiIndex.from_tuples(tuples, names=['year', 'tile'])
    s = pandas.Series(index=mi)
    for (year, tile) in tuples:
        s[year, tile] = tifs[year][tile]
    return s.sort_index()

def find_dmsp_files(dmspdir):
    tifs = defaultdict(lambda: defaultdict(dict))
    tuples = []
    tiftypes = set()
    for filename in os.listdir(dmspdir):
        parts = filename.split('.')
        if parts[-1] in ['tar', 'gz', 'tfw', 'txt']:
            continue
        sat_year = parts[0]
        sat = sat_year[:3]
        year = int(sat_year[3:])
        tiftype = parts[2]
        if tiftype == 'avg_vis':
            continue
        tuples.append((year, sat, tiftype))
        tifs[year][sat][tiftype] = os.path.join(dmspdir, filename)
    mi = pandas.MultiIndex.from_tuples(tuples, names=['year', 'sat', 'tiftype'])
    s = pandas.Series(index=mi)
    for (year, sat, tiftype) in tuples:
        s[year, sat, tiftype] = tifs[year][sat][tiftype]
    return s.sort_index()

def find_radcal_files(radcaldir):
    #tifs = defaultdict(lambda: defaultdict(dict))
    tifs = defaultdict(dict)
    tuples = []
    for filename in os.listdir(radcaldir):
        _, ext = os.path.splitext(filename)
        if ext != '.tif':
            continue
        # skip duplicate file version with a bit less data (see https://www.ngdc.noaa.gov/eog/dmsp/radcal_readme.txt note 5-3)
        if 'F16_20100111-20101209' in filename:
            continue
        parts = filename.split('_')
        #sat = parts[0]
        date0, date1 = [datetime.datetime.strptime(d, '%Y%m%d') for d in parts[1].split('-')]
        year = (date0 + ((date1 - date0) / 2)).year
        tiftype = filename.split('.')[1]
        #tuples.append((year, sat, tiftype))
        tuples.append((year, tiftype))
        #tifs[year][sat][tiftype] = os.path.join(radcaldir, filename)
        tifs[year][tiftype] = os.path.join(radcaldir, filename)
    #mi = pandas.MultiIndex.from_tuples(tuples, names=['year', 'sat', 'tiftype'])
    mi = pandas.MultiIndex.from_tuples(tuples, names=['year', 'tiftype'])
    s = pandas.Series(index=mi)
    #for (year, sat, tiftype) in tuples:
        #s[year, sat, tiftype] = tifs[year][sat][tiftype]
    for (year, tiftype) in tuples:
        s[year, tiftype] = tifs[year][tiftype]
    return s.sort_index()


def avg_eog_tiles(source, target, env):
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
    assert np.all(cumcount == cumcount.astype(countmeta['dtype']))
    with rasterio.open(str(target[1]), 'w', **countmeta) as out:
        out.write(cumcount.astype(countmeta['dtype']), 1)
    return 0


def avg_dmsp_sats(env, source, target):
    nsats = env['nsats']
    for i in range(nsats):
        with rasterio.open(str(source[i])) as rast:
            satavg = rast.read(1)
            meta = rast.meta
            del meta['transform']
        with rasterio.open(str(source[nsats+i])) as rast:
            satcount = rast.read(1)
        if i == 0:
            cumcount = satcount.copy()
            cumsum = satavg.copy() * cumcount
        else:
            cumsum += satavg * satcount
            cumcount += satcount
    avg = np.zeros_like(cumsum) * np.nan
    avg[cumcount>0] = cumsum[cumcount>0] / cumcount[cumcount>0]
    avg[avg<0] = 0
    avg[np.isnan(avg)] = 0

    meta['dtype'] = 'float64'
    with rasterio.open(str(target[0]), 'w', **meta) as out:
        out.write(avg, 1)
    countmeta = meta.copy()
    countmeta['dtype'] = 'uint8'
    assert np.all(cumcount == cumcount.astype(countmeta['dtype']))
    with rasterio.open(str(target[1]), 'w', **countmeta) as out:
        out.write(cumcount.astype(countmeta['dtype']), 1)
    return 0


# conversion from DN to Radiance. Interannual calibration
def _Rsat(G):
    return 5.3e-6 / (10**(G/20))
def _R(DN, G=55):
    return (DN * _Rsat(G)) / 63
def calibrate_radcal(source, target, env):
    # interannual calibration from https://www.ngdc.noaa.gov/eog/dmsp/radcal_readme.txt (table 3)
    # dn_eq = coef[0] + coef[1] * dn
    coefs = {'F12_19960316-19970212_rad_v4':     (4.336, 0.915),
             'F12_19990119-19991211_rad_v4':     (1.423, 0.780),
             'F12-F15_20000103-20001229_rad_v4': (3.658, 0.710),
             'F14-F15_20021230-20031127_rad_v4': (3.736, 0.797),
             'F14_20040118-20041216_rad_v4':     (1.062, 0.761),
             'F16_20051128-20061224_rad_v4':     (0.000, 1.000), # reference dataset
             #'F16_20100111-20101209_rad_v4':     (2.196, 1.195), # dont use this one, overlap of next but less data
             'F16_20100111-20110731_rad_v4':     (-1.987, 1.246)}
    with rasterio.open(str(source[0])) as rast:
        dn_eq = rast.read(1)
        meta = rast.meta
        del meta['transform']
    # interannual calibrate to match F16_20051128-20061224_rad_v4
    fname = os.path.basename(str(source[0])).split('.')[0]
    dn_calib = coefs[fname][0] + coefs[fname][1] * dn_eq
    # scale from digital number to radiance
    radiance = _R(dn_calib) * 1e9 # scale by 1e9 to match VIIRS scales
    with rasterio.open(str(target[0]), 'w', **meta) as out:
        out.write(radiance, 1)
    return 0


def write_grdImport_input(source, target, env):
    with open(str(target[0]), 'w') as fout:
            fout.write(str(env['dataformat']) + '\n')
            fout.write(str(env['nodata']) + '\n')
            fout.write(str(env['listfile']) + '\n')
            fout.write(env['outputfile'] + '\n')
            fout.write(str(env['gridtype']) + '\n')
    return 0


