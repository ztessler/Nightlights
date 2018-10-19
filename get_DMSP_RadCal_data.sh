SAVEDIR="/Users/ecr/ztessler/data/Nightlights/DMSP_RadCal"

SERVER="https://data.ngdc.noaa.gov"
BASEDIR="instruments/remote-sensing/passive/spectrometers-radiometers/imaging/ols/composites/fg/"
PATTERN_TAR="F*_rad_v4.geotiff.tgz"

wget -e robots=off -r --no-parent -nc -nH --cut-dirs=8 -P $SAVEDIR -A $PATTERN_TAR ${SERVER}/${BASEDIR}

find ${SAVEDIR} -name "${PATTERN_TAR}" -execdir tar -xf {} \;

