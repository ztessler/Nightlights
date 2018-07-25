# vim: fileencoding=UTF-8
# vim: filetype=python

### TO RUN:
#

import os
import sys
import subprocess
import lib

SetOption('max_drift', 1)

env = Environment(ENV = {'PATH' : os.environ['PATH'],
                         'GDAL_DATA': os.environ['GDAL_DATA'],
                         })
env.Decider('MD5-timestamp')

work = 'work'
output = 'output'
data = 'data'

# VIIRS data download and untar with get_VIIRS_data.sh
#   get month list
viirsdir = '/Users/ecr/ztessler/data/Nightlights/VIIRS'
viirsproc = '/Users/ecr/ztessler/data/Nightlights/processed/VIIRS'
tifs = lib.find_files(viirsdir)

# compute annual composite tiles
years = sorted(set(tifs.index.get_level_values('year')))
tiles = sorted(set(tifs.index.get_level_values('tile')))
for year in years:
    for tile in tiles:
        avgs = tifs.loc[year, :, tile, 'avg'].tolist()
        count = tifs.loc[year, :, tile, 'cf'].tolist()
        composite = os.path.join(viirsproc, 'annual', str(year), 'viirs_nightlights_{0}_{1}.tif'.format(year, tile))
        comp = env.Command(
                source=avgs+count,
                target=composite,
                action=lib.avg_tiles,
                nmonths=len(avgs))
        env.Default(comp)


# DMSP-OLS
