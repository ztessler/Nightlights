# vim: fileencoding=UTF-8
# vim: filetype=python

### TO RUN:
#

### NOTES
# Preprocesses nighttime-lights data. multiple sources:
#   - DMSP-OLS
#       older, lower res, but available back many years
#   - VIIRS, processed data from Earth Observations Group at NOAA/NCEI
#       Monthly composites available from 2012-2018
#       Annual composites still being developed
#       Cleaned, but still substaintial noise/errors from sun/moon glint, clouds, ...
#   - VIIRS, Black Marble VNP46, Roman et al., 2018, Remote Sens of Envi.
#       More complete cleaning, best product, currently available for 2012 and 2016
#       more soon (early 2019), will be on LADAAC
# Prefer data in this order:
#   VIIRS BlackMarble
#   VIIRS EOG
#   DMSP-OLS

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

# DMSP-OLS data download with get_DMSP_OLS_data.sh
#   some years have multiple satellies, average them
#   get year, instrument list
dmspdir = '/Users/ecr/ztessler/data/Nightlights/DMSP_OLS'
dmspproc = '/Users/ecr/ztessler/data/Nightlights/processed/DMSP_OLS'
dmsptifs = lib.find_dmsp_files(dmspdir)
#dmsp_years = range(1992, 2013+1)[:1]
dmsp_years = sorted(set(dmsptifs.index.get_level_values('year')))

# DMSP-OLS data is not calibrated to radiance. see Hsu 2015 Remote Sensing for approximate calibrations
# DMSP Radiance Calibrated product is available from NOAA, though they warn the calibration is
# approximate due to sensor drift. Data need to be adjust interannually for comparison, then
# converted to radiance. Get data with get_DMSP_RadCal_data.sh
radcaldir = '/Users/ecr/ztessler/data/Nightlights/DMSP_RadCal'
radcalproc = '/Users/ecr/ztessler/data/Nightlights/processed/DMSP_RadCal'
radcaltifs = lib.find_radcal_files(radcaldir)
radcal_years = sorted(set(radcaltifs.index.get_level_values('year')))


# VIIRS EOG data download and untar with get_VIIRS_eog_data.sh
#   get month list
eogdir = '/Users/ecr/ztessler/data/Nightlights/VIIRS_EOG'
eogproc = '/Users/ecr/ztessler/data/Nightlights/processed/VIIRS_EOG'
eogtifs = lib.find_files(eogdir)
#eog_years = range(2012, 2018+1)[1:2]
eog_years = sorted(set(eogtifs.index.get_level_values('year')))

# VIIRS Black Marble data download with get_VIIRS_blackmarble_data.sh
# black marble version is processed to remove far more sources of noise, including moonglint, clouds, ...
# better source, but not all years available yet (just 2012 and 2016)
#   get month list
bmdir = '/Users/ecr/ztessler/data/Nightlights/VIIRS_BlackMarble'
bmproc = '/Users/ecr/ztessler/data/Nightlights/processed/VIIRS_BlackMarble'
bmtifs = lib.find_bm_files(bmdir)
#bm_years = [2012, 2016][:1]
bm_years = sorted(set(bmtifs.index.get_level_values('year')))

# overwrite dict values to prefer bm, then eog, then dmsp
years = {}
for source, sourceyears in [
                            #('dmsp', dmsp_years),
                            ('radcal', radcal_years),
                            #('eog', eog_years),
                            #('bm', bm_years),
                            ]:
    for year in sourceyears:
        years[year] = source
startyear = min(years)
endyear = max(years)

for year, source in years.items():
    if source == 'bm':
        bmannualtiles = bmtifs[year].tolist()
        annual = os.path.join(bmproc, str(year), 'viirs_bm_nightlights_{0}.tif'.format(year))
        env.Command(
                source=bmannualtiles,
                target=annual,
                action=['gdal_merge.py -o ${TARGET}.3bands -of GTiff -v $SOURCES',
                        'gdal_translate -b 1 ${TARGET}.3bands $TARGET']) # merge, then just take first band (rgb are all the same)

    elif source == 'eog':
        # compute eog annual composite tiles
        tiles = sorted(set(eogtifs[year].index.get_level_values('tile')))
        eogannualtiles = []
        for tile in tiles:
            avgs = eogtifs.loc[year, :, tile, 'avg'].tolist()
            count = eogtifs.loc[year, :, tile, 'cf'].tolist()
            annualtile = os.path.join(eogproc, str(year), 'viirs_eog_nightlights_{0}_{1}.tif'.format(year, tile))
            annualcounts = os.path.join(eogproc, str(year), 'viirs_eog_nightlights_counts_{0}_{1}.tif'.format(year, tile))
            env.Command(
                    source=avgs+count,
                    target=[annualtile, annualcounts],
                    action=lib.avg_eog_tiles,
                    nmonths=len(avgs))
            eogannualtiles.append(annualtile)

        annual = os.path.join(eogproc, str(year), 'viirs_eog_nightlights_{0}.tif'.format(year))
        env.Command(
                source=eogannualtiles,
                target=annual,
                action='gdal_merge.py -o $TARGET -of GTiff -v $SOURCES')

    elif source == 'radcal':
        # already annual global raster, but need to calibrate it
        annual = os.path.join(radcalproc, str(year), 'dmsp_radcal_nightlights_{0}.tif'.format(year))
        env.Command(
                source=radcaltifs[year, 'avg_vis'],
                target=annual,
                action=lib.calibrate_radcal)
        pass
    elif source == 'dmsp':
        # compute dmsp annual composite if more than one satellite for this year
        avgs = dmsptifs.loc[year, :, 'stable_lights'].tolist()
        count = dmsptifs.loc[year, :, 'cf_cvg'].tolist()
        annual = os.path.join(dmspproc, str(year), 'dmsp_ols_nightlights_{0}.tif'.format(year))
        annualcounts = os.path.join(dmspproc, str(year), 'dmsp_ols_nightlights_counts_{0}.tif'.format(year))
        env.Command(
                source=avgs+count,
                target=[annual, annualcounts],
                action=lib.avg_dmsp_sats,
                nsats=len(avgs))

    downscale = os.path.join(work, 'nightlights_{0}_{1}.tif'.format(year, STNres))
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

    rgis = os.path.join(output, 'Global_Nightlights_DMSPorVIIRS_{0}_aTS{1}.gdbc'.format(STNres, year))
    env.Command(
            source=rgis1,
            target=rgis,
            action='grdDateLayers -y {0} -e year -s blue-to-red $SOURCE $TARGET'.format(year))

    RGISlocal_gdbc = os.path.join(RGISlocal, 'Global/Nightlights/DMSPorVIIRS/{0}/Annual'.format(STNres), os.path.basename(rgis))
    final = env.Command(
            source=rgis,
            target=RGISlocal_gdbc,
            action='cp $SOURCE $TARGET')
    env.Default(final)

### For now, just use DMSP_RadCal
### later, when black marble radiance calibrated data is available, do adjustments to match timeseries
### as:
# interpolate data to missing years within each data source

# extrapolate (constant) data to get overlap between dmsp_radcap and viirs

# adjust nightlights data from dmsp_radcal to match global means from viirs for years they overlap
#   compute global mean radiance, scale dmsp_radcal to match viirs
#   apply scaling factor to all dmsp_radcal years


