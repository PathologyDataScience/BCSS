# CrowdsourcingDataset-Amgadetal2019

Use this to download all elements of the dataset described in: 

```
Amgad M, Elfandy H, ..., Gutman DA, Cooper LAD. Structured crowdsourcing enables convolutional segmentation of histology images. Bioinformatics. 2019. doi: 10.1093/bioinformatics/btz083
```

This will download the whole-slide images (WSI), annotation JSON files (coordinates), as well the masks. Steps are as follows:

**Step 1: Instal requirements**
  
  `pip install girder_client wget`
  
**Step 2: Create a free account on the HistomicsTK Kitware instance**
  
  The process takes only one minute. You go to:
  http://demo.kitware.com/histomicstk/histomicstk
  Then click 'register' on the top right corner and fill in the details.

**Step 3: Set download path**
  
  Simply edit the variable SAVEPATH at the top of the download_crowdsource_dataset.py script
  The default behavior is to create directories in the save folder where this repo is located.

**Step 4: Run the download script**
  
  `python download_crowdsource_dataset.py`
  
  The script will create the following sub-directories: 
    |_ wsis : where whole-slide images will be saved
    |_ annotations : where JSON annotations will be saves for each slide
    |_ masks : where the ground truth masks to use for training and validation are saved
    |_ logs : in case anythign goes wrong

**Step 5: Run the auto-generated WSI script**

  Run the batch or shell script from the command line using the following command:
  
  On Windows:
    `./wsis/download_wsis.bat`
  On Mac or Linux:
    `bash ./wsis/download_wsis.sh`
  
  to download the full whole-slide images.
