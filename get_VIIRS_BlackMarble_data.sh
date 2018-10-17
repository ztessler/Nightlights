SAVEDIR="/Users/ecr/ztessler/data/Nightlights/VIIRS_BlackMarble"

SERVER="https://www.nasa.gov"
BASEDIR="specials/blackmarble/YYYY/tiles/georeferrenced"
FILENAME="BlackMarble_YYYY_TT_geo_gray.tif"

for YEAR in 2012 2016
do
    for TILE in A1 A2 B1 B2 C1 C2 D1 D2
    do
        _BASEDIR=${BASEDIR//YYYY/$YEAR}
        _FILENAME=${FILENAME//YYYY/$YEAR}
        _FILENAME=${_FILENAME//TT/$TILE}
        wget -nc -P ${SAVEDIR}/$YEAR ${SERVER}/${_BASEDIR}/${_FILENAME}
    done
done

