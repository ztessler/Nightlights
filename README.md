## Pre-processing Nighttime lights data

This repo contains code to scale and normalize nighttime lights data from multiple sensors or
datasets. Processes data for use in RGIS hydrological model, which uses a particular raster format.
Needs GHAAS and RGIS code installed. Alternatively, edit SConstruct file to not run RGIS commands and
leave processed data in AsciiGrid format, or use GDAL to convert to another raster format.

Processing code runs as an SCons build. `SConstruct` contains code to define a computational graph
with input dependencies for each output file. Run with `scons` to read/execute SConstruct file, which then
calls shell commands or functions in `lib.py`.

First download data using `get_*.py` scripts.

Edit hard-coded data directory paths in SConstruct. Then
run with `scons $STNres` where `STNres` is resolution of STN digital river network for final
output.

## Sensors:

### DMSP-OLS
* And older data set, but available for a relatively long time frame (1992-2013)
* Calibration is uneven, varies between sensor (flew on multiple satellites), and there is drift
over sensor lifetime
* Sensor saturation challenges

### DMSP-OLS Radiance Calibrated
* Apply limited radiance calibration data.
* Not available for full DMSP-OLS data set

### VIIRS
* Higher resolution that DMSP-OLS, radiance calibrated
* Data comes from the Earth Observations Group at NOAA/NCEI
* Monthly composites available from 2012-2018
* Annual composites under development
* Cleaned, but still substaintial noise/erros from sun, moon glint, clouds,...

### VIIRS Black Marble VNP46
* Roman et al., 2018, Remote Sens of Envi.
* More complete cleaning, best product in terms of data quality, currently available only for 2012
and 2016
* More soon, to be available on LADAAC


