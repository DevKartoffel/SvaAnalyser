import csv 
import json 

def csv_to_json(csvFilePath):
    jsonArray = []
      
    #read csv file
    with open(csvFilePath, encoding='utf-8') as csvf: 
        #load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(csvf) 

        #convert each csv row into python dict
        for row in csvReader: 
            #add this python dict to json array
            jsonArray.append(row)
    
    return jsonArray

def get_saved_data(file_path):

    # Read settings
    with open(file_path, 'r') as f:
        data = json.load(f)
        return data