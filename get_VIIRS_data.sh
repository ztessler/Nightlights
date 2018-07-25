SAVEDIR="/Users/ecr/ztessler/data/Nightlights/VIIRS"

SERVER="https://data.ngdc.noaa.gov"
BASEDIR="instruments/remote-sensing/passive/spectrometers-radiometers/imaging/viirs/dnb_composites/v10/"
PATTERN="SVDNB_npp_*-*_*_vcmcfg_v10_*.tgz"

wget -r --no-parent -nc -nH --cut-dirs=8 -P $SAVEDIR -A $PATTERN ${SERVER}/${BASEDIR}

# find all *.tgz, and in parallel untar then (if not already (-k)). need to use subshell (sh -c '') so dirname command sub isn't evaluated just once at very beginning, but rather for each filename
find ${SAVEDIR} -name "${PATTERN}" -print0 | xargs -I{} -0 -P 16  sh -c 'tar -xzkf {} -C $(dirname {})'
