import os
import zipfile
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import pandas as pd
import glob
import numpy as np
import matplotlib.pyplot as plt


def download_zipfile(url):
    # Send a request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
    # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        lines_list = soup.get_text().splitlines()
        lines_string = ''.join(lines_list)
        zip_words = re.findall(r'\b\w+\.zip\b', lines_string) #selecting only .zip words 
        lines = ' '.join(zip_words)
        lines = lines.split(" ")

        # Initialize a flag to track downloading
        download = False

        # Iterate through the lines and download the ZIP files within the specified range
        for line in lines:
            if filename in line:   
                download = True
            if download:
                    href = line.split(' ')[-1]
                    if href.endswith('.zip'):
                        file_url = urljoin(url, href)
                        file_name = href.split('/')[-1]

                        # Download the ZIP file to the specified directory
                        file_path = os.path.join(download_dir, file_name)

                        with requests.get(file_url) as response:
                            if response.status_code == 200:
                                with open(file_path, 'wb') as file:
                                    file.write(response.content)
                            break
    else:
        print("Failed to retrieve the page")
        
        
def extract_zip(zip_file_path, extract_to):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to) #extracting the zip file

def extract_nested_zips(directory,csv_dir):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.zip'):
                zip_file_path = os.path.join(root, file)
                extract_to = csv_dir
                os.makedirs(extract_to, exist_ok=True)
                extract_zip(zip_file_path, extract_to)
                extract_nested_zips(extract_to,csv_dir) #calls itself until all the zip files are extracted
                #print("Extraction complete.")

                
                
def statewise_data_process(df):

    #intialising group size as 6 to compute 30min resolution from 5min interval data
    group_size =6 

    num_groups = len(df['RRP']) // group_size #total number of reading per day becomes 48
    tw_avg_values = []  #creating empty list to store time weighted average

    data_array = df['RRP']
    # loop to iterate through the groups
    for i in range(num_groups):
        # Extract a group of values
        group = data_array[i * (group_size) : (i + 1) * (group_size)]

        # Calculate the time-weighted average for the group
        tw_avg = sum((float(value)) for value in group) / group_size

        # Append the result to the list
        tw_avg_values.append(tw_avg)

    #considering the settlement date 5 min intervals to 30 min interval reading    
    interval = [value for i, value in enumerate(vic_df['SETTLEMENTDATE'], start=1) if i % 6 == 0]
        
    resolution_data = pd.DataFrame({'SETTLEMENTDATE':interval, 'RRP in $MWh':tw_avg_values })

    return resolution_data

def plot_vic(df,state):

    #list of percentiles we are calculating
    percentiles = [1, 10, 50, 90, 100]

    #extracting the date of the RRP data 
    date =  df['SETTLEMENTDATE'][0].split(" ")[0]

    #percentile calculation
    percentile_values = np.percentile(df['RRP in $MWh'], percentiles)
    
    plt.figure() #create new plot
    plt.plot(percentiles, percentile_values, marker='o', linestyle='-', color='g')
    # Add labels and title
    
    plt.xlabel('Percentiles (having 24 hrs data of ' + date +')')
    plt.ylabel('RRP in $/MWh')
    plt.title('Percentiles Plot of '+ str(state) +' RRP data',fontweight='bold')
    # Set the background color to white
    plt.gca().set_facecolor('white')
    plt.savefig(str(state)+ '_percentiles_plot.png', facecolor='white')

    
    
if __name__ == "__main__":
    
    # Define the URL
    url = "https://nemweb.com.au/Reports/Archive/DispatchIS_Reports/"

    # Define filename of the particular day of interest
    # please make sure to delete the previously downloaded zip file from url
    filename = "PUBLIC_DISPATCHIS_20221201.zip"

    # Define the directory where you want to save the initial ZIP file
    download_dir = "downloaded_zipfile"
    
    # Create the download directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)
    
    download_zipfile(url)
    
    # Specify the path to your initial zip file
    initial_zip_path =  os.path.join(download_dir, filename)

    # Specify the directory where you want to extract the files
    extraction_directory = './extracted_zipfiles_from_intialZipfile'
    csv_dir = './extracted_csvfiles'
    
    # Extract the initial zip file
    extract_zip(initial_zip_path, extraction_directory)
    
    # Extract nested zip files recursively
    extract_nested_zips(extraction_directory,csv_dir) 
    
    # Get a list of all files in the csv directory 
    all_files = sorted(os.listdir(csv_dir))

    # Initialize an empty DataFrame to store the combined filtered data as our requirement
    complete_df = pd.DataFrame()

    for file_name in all_files:
        #if file_name.endswith('.csv'):
            file_path = os.path.join(csv_dir, file_name)
            columns_to_read = 10
            header_names = ['SETTLEMENTDATE', 'REGIONID', 'RRP']

            # Read the CSV file into a DataFrame with only the specified columns
            df = pd.read_csv(file_path, usecols=range(columns_to_read))

            #read only rows with values 'D' 'DISPATH' 'PRICE
            filtered_df =df[(df["C"]== 'D') & (df["NEMP.WORLD"]=='DISPATCH') & (df["DISPATCHIS"]=='PRICE')]

            #Remove other columns
            columns_to_remove =[0,1,2,3,5,7,8]
            filtered_df = filtered_df.drop(columns = filtered_df.columns[columns_to_remove])
            filtered_df.columns = header_names
            complete_df = complete_df.append(filtered_df,ignore_index=False)

    #extracting RRP vlaues of each states seperately
    vic_df = complete_df[complete_df["REGIONID"]=="VIC1"]
    nsw_df = complete_df[complete_df["REGIONID"]=="NSW1"]
    qld_df = complete_df[complete_df["REGIONID"]=="QLD1"]
    sa_df = complete_df[complete_df["REGIONID"]=="SA1"]
    tas_df = complete_df[complete_df["REGIONID"]=="TAS1"]


    #statewise calculation of time weighted average
    vic = statewise_data_process(vic_df)
    nsw = statewise_data_process(nsw_df)
    qld= statewise_data_process(qld_df)
    sa = statewise_data_process(sa_df)
    tas = statewise_data_process(tas_df)
    
    #plotting all states' percentile graph
    plot_vic(vic, "VIC")
    plot_vic(nsw, "NSW")
    plot_vic(qld, "QLD")
    plot_vic(sa, "SA")
    plot_vic(tas, "TAS")
