# CrowdsourcingDataset-Amgadetal2019

Use this to download all elements of the dataset described in: 

***_Amgad M, Elfandy H, ..., Gutman DA, Cooper LAD. Structured crowdsourcing enables convolutional segmentation of histology images. Bioinformatics. 2019. doi: 10.1093/bioinformatics/btz083_***

This data can be visualized in a public instance of the DSA at https://goo.gl/cNM4EL. Mask images derived from this data are used in training and validation are available at: 

https://figshare.com/articles/Structured_Crowdsourcing_Enables_Convolutional_Segmentation_of_Histology_Images/7193138

Masks are automatically downloaded by this script for convenience.

This script will download the whole-slide images (WSI), annotation JSON files (coordinates), as well the masks and corresponding RGB images. 

Steps are as follows:

**Step 1: Instal requirements**
  
  `pip install girder_client girder-client wget pillow`

**Step 2: Set download path**
  
  Simply edit the variable SAVEPATH at the top of the download_crowdsource_dataset.py script
  The default behavior is to create directories in the save folder where this repo is located.

**Step 3: Run the download script**
  
  `python download_crowdsource_dataset.py`
  
  The script will create the following sub-directories: 
  
    |_ wsis : where whole-slide images will be saved  
    |_ annotations : where JSON annotations will be saves for each slide
    |_ masks : where the ground truth masks to use for training and validation are saved
    |_ images: where RGB images corresponding to masks are saved
    |_ logs : in case anythign goes wrong

**Step 4: Run the auto-generated WSI script**

  Run the batch or shell script from the command line using the following command:
  
  On Windows:
    `./wsis/download_wsis.bat`
    
  On Mac or Linux:
    `bash ./wsis/download_wsis.sh`
  
  to download the full whole-slide images.
  
-------------------------------------------------

**IMPORTANT NOTE: How to use masks**

- Each mask is a .png image, where pixel values encode region class membership. The meaning of ground truth encoded can be found at the file gtruth_codes.tsv found in the same directory.

- The name of each mask encodes all necessary information to extract the corresponding RGB images from TCGA slides. For convenience, RGBs are also downloaded using the code used here. 

- **[CRITICAL] -** Please be aware that zero pixels represent regions outside the region of interest (“don’t care” class) and should be assigned zero-weight during model training; they do **NOT** represent an “other” class.

- The masks and RGB images here are at **base (scan) magnification**. For most slides, this is 40x, for others it is 20x. For convenience the file `slide_magnifications_Amgadetal2019.csv` included here contains the magnifications for all slides. IF you want to use the masks to train models at a particular magnification, use resizing. For example, say the mask is at 40x and you want to train at 20x, use something like:

```python
from skimage.transform import resize
f = 40. / 20.
new_shape = [int(j/f) for j in mask.shape]
resized_mask = resize(
    mask, output_shape=new_shape, order=0, preserve_range=True)
```
Do the same for the RGB images of course.
