import os
import csv
import re
import win32com.client


#Open csv file for OM Submittal Log
with open ("OM Submittal Log CSV.csv") as csvf:
    csvreader = csv.reader(csvf, delimiter = ',')
    entity = []
    filenames = []
    division = []
    contract = []
    category = []
    flag = []
    
    #Iterate past header in csv
    next(csvreader)
    for row in csvreader:       
        
        #Get only values in column for filenames and split files separated by ; into their own entries.
        rowAdded = row[4].split(';')     
        print(rowAdded)
        for entry in rowAdded:    
            #Add individual filenames to their own list.         
            filenames.append(entry.strip())
        
        #Get and store the columns as lists, all empty strings are kept to make lists comparable by same index. Note filenames can have a longer length than other columns.
        entity.append(row[0].strip())            
        division.append(row[1].strip())         
        contract.append(row[2].strip()) 
        category.append(row[3].strip()) 
        flag.append(row[5].strip()) 
        
    
    #Create paths for tagged items. Create shortcuts to sourcefiles.
    counter2 = 0
    for b in filenames:
        #Don't run 
        if counter2<len(division)-1:
            if division[counter2]:
                #print ('Untagged')
                pass
            else:
                #Create path if it doesn't exist for tagged items.
                if not os.path.exists(f'C:/Users/tshen/Desktop/Python Code/Library/{entity[counter2]}'):
                    os.mkdir(f'C:/Users/tshen/Desktop/Python Code/Library/{entity[counter2]}')
                    #print('Made Path')
                #Create shortcut if it doesn't exist for tagged items.
                if b:
                    path = f'C:/Users/tshen/Desktop/Python Code/Library/{entity[counter2]}/{b}.lnk'
                    target = f'C:/Users/tshen/Desktop/Python Code/OM Sourcefiles/{b}' 
                    icon = f'C:/Users/tshen/Desktop/Python Code/OM Sourcefiles/{b}' 
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shortcut = shell.CreateShortCut(path)
                    shortcut.Targetpath = target
                    shortcut.IconLocation = icon
                    shortcut.save()
                    #print('Made Shortcut')
        counter2 +=1
            
  
        
#Create new dummy pdf files in current directories. For use with this program. Note the extension, it doesn't 
    
    #Remove extension from filenames list.
    # fileStrip = []
    # counter = 0
    # for a in filenames:
    #     #Find coordinates of extension using Regex
    #     if filenames[counter]:
    #         extcoords = re.search(r'\.[a-z]{3}$',filenames[counter]).span()
    #         #Remove the extension and re-append into new list.
    #         fileStrip.append(filenames[counter][0:extcoords[0]-extcoords[1]])
    #     else:
    #         fileStrip.append(filenames[counter])
    #     counter +=1    


    # for z in fileStrip: 
    #     with open(f'{z}.pdf',"w") as f:
    #         print('Made File')
    
         
        
            

    