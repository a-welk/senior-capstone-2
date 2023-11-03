'''
Program is used to add more details to the transactions from Kaggle
The main program adds a few attributes to the transactions have unique identifiers for each transaction they are
    1. Add Card number to each transaction from the provided cards csv by converting it to a json format
    2. Get Person name for each transaction using the user index given  and getting names from csv file
    3. Generating Latitude and Longitude from
'''
import os.path
import pandas as pd
import json
import pgeocode
import numpy as np
from numpy.random import seed
from numpy.random import randint

# Convert cards csv file to json file to be later loaded in as dictionary
class GenerateCardsJson:
    def generateCardsJsonFile(self):
        # Read cards csv
        cardsFIle = pd.read_csv('sd254_cards.csv')
        cards = {}
        # loop through the rows using iterrows()
        for index, row in cardsFIle.iterrows():
            card_number = row['Card Number']
            user = row['User']
            card_index = row['CARD INDEX']
            card_brand = row['Card Brand']
            card_type = row['Card Type']
            expiration_date = row['Expires']
            CVV = row['CVV']
            has_chip = row['Has Chip']
            cards_issued = row['Cards Issued']
            credit_limit = row['Credit Limit']
            date_opened = row['Acct Open Date']
            pin_last_changed_year = row['Year PIN last Changed']
            card_on_dark_web = row['Card on Dark Web']
            cards[f'{user}-{card_index}'] = [user, card_index, card_brand, card_type, card_number, expiration_date, CVV,
                                             has_chip, cards_issued, date_opened, pin_last_changed_year, card_on_dark_web]
        json_file = open("cards.json", "w")
        json.dump(cards, json_file)

#Class to  add card numbers and geo tags (long, lat)
class AddCardNumbers():
    # function for get longitude and latitude data from zip codes
    def get_lat_lon_from_zip(self, zip_code):
        nomi = pgeocode.Nominatim('us')
        query = nomi.query_postal_code(zip_code)
        data = {
            "lat": query["latitude"],
            "lon": query["longitude"]
        }
        return data['lat'], data['lon']
    
    #function to add the card numbers from the user and card csv
    def addCardNumber(self, transactions):
        print("Adding Card Numbers")
        total_rows = len(transactions)
        current_row = 0
        cards_file = open("cards.json", "r")
        cards = json.load(cards_file)
        users_file = pd.read_csv("sd254_users.csv")
        transactions.insert(3, column="Card Number", value=0)
        person_values = []
        latitudeData = []
        longitudeData = []
        transaction_id = []
        card_number_data = []
        transactions.insert(0, column="Transaction ID", value=0)
        transactions.insert(2, column="Person", value=0)
        transactions.insert(14, column="Latitude", value=0)
        transactions.insert(15, column="Longitude", value=0)
        id_count = 0
        # 
        for index, row in transactions.iterrows():
            user = row['User']
            card_index = row['Card']
            card_data = cards.get(f'{user}-{card_index}', 0)
            card_number = 0
            if len(card_data) > 1:
                card_number = card_data[4]
            card_number_data.append(card_number)
            transaction_id.append(id_count)
            id_count += 1
            
            user = row['User']
            person = users_file['Person'].get(user, 0)
            person_values.append(person)
            current_row += 1
            percentage_complete = (current_row / total_rows) * 100
            print(f'\r{percentage_complete:.2f}% complete', end='', flush=True)
            zipcode = row['Zip']
            if pd.notna(zipcode):
                zipcode = int(zipcode)
                AddCoordinatesTransactions = AddCardNumbers()
                longitude, latitude = AddCoordinatesTransactions.get_lat_lon_from_zip(zipcode)
            else:
                longitude = 0
                latitude = 0
            latitudeData.append(latitude)
            longitudeData.append(longitude)
        transactions['Transaction ID'] = transaction_id
        transactions['Person'] = person_values
        transactions['Card Number'] = card_number_data
        transactions['Latitude'] = latitudeData
        transactions['Longitude'] = longitudeData
        print()
        transactions.head()
        return transactions
        #transactions_file = open("Transactions.csv", "w")
        #transactions.to_csv(transactions_file, index=False)

# method to add names to the final csv file of all current mock transactions
    def add_name(self, transactions):
        names = pd.read_csv(self)
        for index, row in transactions.iterrows():
            name = names['Person']
            id = transactions['User']
            transactions['Person'][row] = name[id]
        return transactions

# method to readjust the users and add a bit of variety in the mock dataset from users
    def readjust_users(transactions):
        seed(1)
        for index, row in transactions.iterrows():
            id = randint(0, 1999, 19963) 
            transactions['User'] = id
        return transactions   
        
# method to manipulate the card numbers to match the specific user and indexed card number for each row
    def readjust_card_nums(transactions):
        num = pd.read_csv("sd254_cards.csv")
        j = 'Card'
        # merging of the two data frames on the matching columns 'User' (user id) and 'Card Index' (their 1st, 2nd, 3rd, ... etc. card)
        merged_data = pd.merge(transactions, num, on=['User', 'CARD INDEX'], how='left')
        print(merged_data)
    # Update the 'Card Number' column in 'transactions' with the values from 'card_data' matching the columns that were merged on
        transactions['Card Number'] = merged_data['Card Number_y']
        return transactions
        
#method to readjust the names in the final csv file to match those in the user id column
    def readjust_names(transactions):
        name = pd.read_csv("sd254_users.csv")
        count = 0
        for index, row in transactions.iterrows():
            user_value = row['User']
            print(user_value)
            ro = name.iloc[user_value]
            transactions['Person'][count] = ro['Person']
            count +=1
        return transactions 

# while working to reach the final output I used each method one by one so all the methods are not present in this main method
# I would be happy to hop on a call to discuss what I did to achieve the final csv
if __name__ == "__main__":
    if not(os.path.exists("cards.json")):
        GenerateCardsJsonFile = GenerateCardsJson()
        GenerateCardsJsonFile.generateCardsJsonFile()
    transactions = pd.read_csv("Transactions_final.csv")
    #AddCardNumbersToTable = AddCardNumbers()
    #transactions.rename(columns={'CARD_INDEX': 'CARD INDEX'}, inplace=True)
    transactions = AddCardNumbers.readjust_names(transactions)
    print("Done")
    # AddPersonsNameToTable = AddPersonsName()
    # transactions = AddPersonsNameToTable.addNames(transactions)
    # print("Done Adding Persons Name")
    # AddCoordinatesToTable = AddCoordinates()
    # transactions = AddCoordinatesToTable.main(transactions)
    # print("Done Adding Coordinates")
    transactions.to_csv("Transactions_final.csv", index=False)
    
