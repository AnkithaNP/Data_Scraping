# Data Scraping Task 

The Python script WEM_Data_scraping.py illustrates the process of obtaining wholesale energy market data from the following website https://nemweb.com.au/Reports/Archive/DispatchIS_Reports/. It also shows how to preprocess the data and visualise the wholesale energy prices for every state under the NEM (national electricity market).

## Explaination about the Script

With all of the comments and code lines provided, the script is self-explanatory.

>  ### Define filename of the particular day of interest 
In main function we can define the specific file name which you want to be downloaded and extracted in further steps. I have taken the file for the day of December 1, 2022. 

>filename = "PUBLIC_DISPATCHIS_20221201.zip"



The tasks performed along with their functions built in the script  are

- Downloding zip file from url -> def download_zipfile(url)

- Extractig the zip files recursively -> def extract_nested_zips(directory,csv_dir)

-  Preprocessing the data to filter the time weighted average of RRP of each state -> def statewise_data_process(df)

- plotting the percentile graph for each state -> def plot_vic(vic,state)

## Packages to be installed 


The packages that are needed to be installed are os, zipline, requests, bs4, urllib, re, pandas, glob, numpy, matplotlib. 

Follow the syntax to install the package 

> pip install *package_name*

## command to run the Script

To run the script follow the below command:
> python3 WEM_Data_scraping.py

> ## Expected output

* The creation of directories for downloaded, extracted files in the current working directory

* The percentile plots are saved in the current working directory with the distinguishable name for each states. 
