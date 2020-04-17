APIURL = 'https://demo.kitware.com/histomicstk/api/v1/'
# apiKey = None  # interactive login
apiKey = 'n0Kp1ez8YOnOiWNoACryzeBlIzbUDW3iOD2DmPLI'

source_folder_id = '5bbdeba3e629140048d017bb'

SAVEPATH = './'
ROIBOUNDSPATH = './meta/roiBounds.csv'

# Set either MPP or MAG.
# If both are None, base (scan) magnification is used.

# Microns-per-pixel -- best use this
# MPP of 0.23 is "standardized" at 40x using original Aperio scanners
# MPP = None
MPP = 0.23

# If you prefer to use whatever magnification is reported
MAG = None
# MAG = 40.0

# What things to download? -- comment out whet you dont want
PIPELINE = (
    'images',
    'masks',
    'annotations',
#    'wsis'
)

# if you only want to download data for specific slides
# SLIDES_TO_KEEP = None
SLIDES_TO_KEEP = ['TCGA-BH-A1FC', 'TCGA-A8-A07C', 'TCGA-A1-A0SK']
