SAVEDIR="/Users/ecr/ztessler/data/Nightlights/DMSP_OLS"

SERVER="https://ngdc.noaa.gov"
BASEDIR="eog/data/web_data/v4composites/"
PATTERN="F*.v4.tar"

wget -e robots=off -r --no-parent -nc -nH --cut-dirs=4 -P $SAVEDIR -A $PATTERN ${SERVER}/${BASEDIR}

# find all *.tar, and in parallel untar then (if not already (-k)). need to use subshell (sh -c '') so dirname command sub isn't evaluated just once at very beginning, but rather for each filename
find ${SAVEDIR} -name "${PATTERN}" -execdir tar -xkf {} \;

