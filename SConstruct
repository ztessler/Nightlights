# vim: fileencoding=UTF-8
# vim: filetype=python

### TO RUN:
#

import os
import sys
import hashlib
import subprocess
import lib

SetOption('max_drift', 1)

env = Environment(ENV = {'PATH' : os.environ['PATH'],
                         'GDAL_DATA': os.environ['GDAL_DATA'],
                         })
env.Decider('MD5-timestamp')

def myCommand(target, source, action, **kwargs):
    '''
    env.Command wrapper that forces env override arguments to be sconsign
    signature database. Wraps all extra kwargs in env.Value nodes and adds
    them to the source list, after the existing sources. Changing the extra
    arguments will cause the target to be rebuilt, as long as the data's string
    representation changes.
    '''
    def hash(v):
        # if this is changed then all targets with env overrides will be rebuilt
        return hashlib.md5(repr(v).encode('utf-8')).hexdigest()
    if not isinstance(source, list):
        source = [source]
    if None in source:
        source.remove(None)
    kwargs['nsources'] = len(source)
    source.extend([env.Value('{}={}'.format(k,hash(v))) for k,v in kwargs.items()])
    return env.Command(target=target, source=source, action=action, **kwargs)



STNres = os.environ.get('STNres', '06min')
STNval = int(STNres[:-3])
STNunits = STNres[-3:]
if STNunits == 'min':
    res = STNval / 60
elif STNunits == 'sec':
    res = STNval / 3600
else:
    raise NotImplementedError

work = 'work'
output = 'output'
RGISlocal = '../WBM/RGISlocal'

# VIIRS data download and untar with get_VIIRS_data.sh
#   get month list
viirsdir = '/Users/ecr/ztessler/data/Nightlights/VIIRS'
viirsproc = '/Users/ecr/ztessler/data/Nightlights/processed/VIIRS'
tifs = lib.find_files(viirsdir)

# compute annual composite tiles
years = sorted(set(tifs.index.get_level_values('year')))
tiles = sorted(set(tifs.index.get_level_values('tile')))
#for year in [2014,2015]:
for year in years:
    annualtiles = []
    for tile in tiles:
        avgs = tifs.loc[year, :, tile, 'avg'].tolist()
        count = tifs.loc[year, :, tile, 'cf'].tolist()
        annualtile = os.path.join(viirsproc, 'annual', str(year), 'viirs_nightlights_{0}_{1}.tif'.format(year, tile))
        annualcounts = os.path.join(viirsproc, 'annual', str(year), 'viirs_nightlights_counts_{0}_{1}.tif'.format(year, tile))
        env.Command(
                source=avgs+count,
                target=[annualtile, annualcounts],
                action=lib.avg_tiles,
                nmonths=len(avgs))
        annualtiles.append(annualtile)

    annual = os.path.join(viirsproc, 'annual', str(year), 'viirs_nightlights_{0}.tif'.format(year))
    env.Command(
            source=annualtiles,
            target=annual,
            action='gdal_merge.py -o $TARGET -of GTiff -v $SOURCES')

    downscale = os.path.join(work, 'viirs_{0}_{1}.tif'.format(year, STNres))
    env.Command(
            source=annual,
            target=downscale,
            action='gdalwarp -of GTiff -tr {0} {0} -te -180 -65 180 75 -tap -r average $SOURCE $TARGET'.format(res))

    ascgrid = downscale.replace('tif', 'asc')
    env.Command(
            source=downscale,
            target=ascgrid,
            action='gdal_translate -of AAIGrid $SOURCE $TARGET')

    grdImport_input = os.path.join(work, 'grdImport_input_{0}_{1}.txt'.format(year, STNres))
    rgis0 = ascgrid.replace('asc', '0.gdbc')
    rgis1 = ascgrid.replace('asc', '1.gdbc')
    myCommand(
            source=None,
            target=grdImport_input,
            action=lib.write_grdImport_input,
            dataformat=3,
            nodata=-9999,
            listfile=0,
            outputfile=rgis0,
            gridtype=1)
    env.Command(
            source=[ascgrid, grdImport_input],
            target=[rgis0, rgis1],
            action=['grdImport -b ${SOURCES[0]} < ${SOURCES[1]}',
                    'setHeader -u Nightlights -t Nightlights -d Global ${TARGETS[0]} ${TARGETS[1]}'])

    rgis = os.path.join(output, 'Global_Nightlights_VIIRS_{0}_aTS{1}.gdbc'.format(STNres, year))
    env.Command(
            source=rgis1,
            target=rgis,
            action='grdDateLayers -y {0} -e year -s blue-to-red $SOURCE $TARGET'.format(year))

    RGISlocal_gdbc = os.path.join(RGISlocal, 'Global/Nightlights/VIIRS/{0}/Annual'.format(STNres), os.path.basename(rgis))
    final = env.Command(
            source=rgis,
            target=RGISlocal_gdbc,
            action='cp $SOURCE $TARGET')
    env.Default(final)



# DMSP-OLS
