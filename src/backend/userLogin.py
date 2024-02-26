import boto3
import uuid
import bcrypt
import os
import json
#from dotenv import load_dotenv
from decimal import *
from boto3.dynamodb.conditions import Key, Attr
dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id="AKIA42KZIHZE3NIJXCJ2", #insert YOUR aws access key here
                          aws_secret_access_key="ULV7X90uwRxEu72rf4xDCoXmZXltARqt7TJ9zRkx", #insert YOUR aws sec
                          region_name="us-east-1")
# Global Transaction table variables
transactionID = [] 
userTransactions = []
transactionYear = []
transactionMonth = []
transactionDay = []
transactionTime = []
transactionAmount = []
transactionMerchantID = []
transactionMCC = []
transactionLat = []
transactionLong = []
transactionZipcode = []
items = []

#queries the user table given an email and password and determines if the password is correct - need to add code for cases where email is not found
def query_user_login(email, password):
    table = dynamodb.Table('Users')
    response = table.query(
        IndexName = 'Email-index',
        KeyConditionExpression = Key('Email').eq(email)
    )
    try:
        items = response['Items']
        UserID = items[0]['UserUUID']
        hashed_password = (items[0]['Password'])
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            print(f"Successfully logged into {email}")
            return UserID
        else:
            print("Invalid user login credentials")
            return False
    except IndexError as IE:
          print("Invalid user login credentials")
          return False
    
    
#queries transactions table for all the transactions of a given userID
def get_user_transaction(UserID):
    #attempt at pagination in order to retrieve ALL the transactions from designated user
    gotItems = []
    paginator = dynamodb.meta.client.get_paginator('query')
    for page in paginator.paginate(TableName='Transaction',
                                   IndexName = 'UserUUID-index',
                                   KeyConditionExpression= Key('UserUUID').eq(UserID)):
                                        this_page = page['Items']
                                        for x in range(len(this_page)):
                                            userTransactions.append(this_page[x]['TransactionUUID'])
                                            transactionYear.append(this_page[x]['Year'])
                                            transactionMonth.append(this_page[x]['Month'])
                                            transactionDay.append(this_page[x]['Day'])
                                            transactionTime.append(this_page[x]['Time'])
                                            transactionAmount.append(this_page[x]['Amount'])
                                            transactionMerchantID.append(this_page[x]['MerchantUUID'])
                                            transactionMCC.append(this_page[x]['MCC'])
    #gets merchant information for each merchantID in each transaction                                        
    for x in range(len(transactionMerchantID)):
        table = dynamodb.Table('Merchants')
        response = table.query(
            KeyConditionExpression = Key('MerchantUUID').eq(transactionMerchantID[x])
        )
        items.extend(response['Items'])
    
    #adds each merchant attribute to their respective list
    for x in range(len(items)):
        try:
            transactionLat.append(items[x]['latitude'])
        except KeyError as ke:
            transactionLat.append("N/A")
        
        try:
            transactionLong.append(items[x]['longitude'])
        except KeyError as ke:
            transactionLong.append("N/A")
        
        try:
            transactionZipcode.append(items[x]['zip'])
        except KeyError as ke:
            transactionZipcode.append("N/A")
        
    #formats all transaction data and puts it into output.json
    data_list = []

    for i in range(len(userTransactions)):
        data_dict = {
            "transactionID": userTransactions[i],
            "transactionAmount": transactionAmount[i],
            "transactionDay": transactionDay[i],
            "transactionMonth": transactionMonth[i],
            "transactionYear": transactionYear[i],
            "transactionTime": transactionTime[i],
            "transactionMerchantID": transactionMerchantID[i],
            "transactionMCC": transactionMCC[i],
            "transactionLat": transactionLat[i],
            "transactionLong": transactionLong[i],
            "transactionZipcode": transactionZipcode[i],
        }

        data_list.append(data_dict)

    json_data = json.dumps(data_list, separators=(',', ':'), indent=2)

    with open('output.json', 'w') as json_file:
        json_file.write(json_data)

    
#inserts a new transaction into the transaction table
def insert_transaction(amount, card, time, day, month, year, isFraud, MCC, merchantCity, merchantState, merchantID, chip, userID, zipcode):
    amount = str(amount)
    table = dynamodb.Table('Transaction')
    transactionID = uuid.uuid4()
    transactionID = str(transactionID)
    response = table.put_item(
        Item={
            'TransactionUUID': transactionID,
            'Amount': amount,
            'Card': card,
            'Day': day,
            'Is Fraud?': isFraud,
            'MCC': MCC,
            'Merchant City': merchantCity,
            'Merchant State': merchantState,
            'MerchantUUID': merchantID,
            'Month': month,
            'Time': time,
            'Use Chip': chip,
            'UserUUID': userID,
            'Year': year,
            'Zip': zipcode
        }
    )
    status_code = {"status_code": 200}
    return json.dumps(status_code)


#inserts new users into Users table
def insert_user(address, apartment, birthMonth, birthYear, city, age, email, FICOscore, gender, lat, long, numCards, password, perCapitaIncome, name, retirementAge, state, debt, annualIncome, zipcode):
    table = dynamodb.Table('Users')
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    userID = uuid.uuid4()
    userID = str(userID)
    response = table.put_item(
        Item={
            'UserUUID': userID,
            'Password': password,
            'Address': address,
            'Apartment': apartment,
            'Birth Month': birthMonth,
            'Birth Year': birthYear,
            'City': city,
            'Current Age': age,
            'Email': email,
            'FICO Score': FICOscore,
            'Gender': gender,
            'Latitude': lat,
            'Longitude': long,
            'Nume Credit Cards': numCards,
            'Per Capita Income - Zipcode': perCapitaIncome,
            'Person': name,
            'Retirement Age': retirementAge,
            'State': state,
            'Total Debt': debt,
            'Yearly Income - Person': annualIncome,
            'Zipcode': zipcode
        }
    )

def insert_user_onboarding(name, email, password, age, retirement_age, annual_income, zipcode, budget, budget_choice):
    table = dynamodb.Table('Users')
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    userID = str(uuid.uuid4())
    response = table.put_item(
         Item={
              'UserUUID': userID,
              'Person': name,
              'Email': email,
              'Password': password,
              'Current Age': age,
              'Retirement Age': retirement_age,
              'Yearly Income - Person': annual_income,
              'Zipcode': zipcode,
              'Budget': budget,
              'Budget Choice': budget_choice
         }
    )

def insert_merchant(latitude, longitude, zipcode):
    table = dynamodb.Table('Merchants')
    merchantUUID = uuid.uuid4()
    merchantUUID = str(merchantUUID)
    response = table.put_item(
        Item={
            'MerchantUUID': merchantUUID,
            'latitude': latitude,
            'longitude': longitude,
            'zip': zipcode
          }
    )

def insert_card(date_open, brand, card_index, card_number, dark_web, type, cards_issued, credit_limit, CVV, expiration, has_chip, UserUUID, pin_last_changed):
      table = dynamodb.Table('Cards')
      cardUUID = str(uuid.uuid4())
      response = table.put_item(
            Item={
               'CardUUID': cardUUID,
               'Acct Open Date': date_open,
               'Card Brand': brand,
               'CARD INDEX': card_index,
               'Card Number': card_number,
               'Card on Dark Web': dark_web,
               'Card Type': type,
               'Cards Issued': cards_issued,
               'Credit Limit': credit_limit,
               'CVV': CVV,
               'Expires': expiration,
               'Has Chip': has_chip,
               'USERUUID': UserUUID,
               'Year PIN last Changed': pin_last_changed
            }
      )

def get_user_cards(UserID):
     table = dynamodb.Table('Cards')
     response = table.query(
          IndexName = 'USERUUID-index',
          KeyConditionExpression = Key('USERUUID').eq(UserID)
     )
     items = response['Items']
     print(items)

def update_user_password(UserID, password):
     password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
     table = dynamodb.Table('Users')
     response = table.update_item(
          Key={'UserUUID': UserID},
          UpdateExpression = "set #password = :n",
          ExpressionAttributeNames={
               "#password": "Password"
          },
          ExpressionAttributeValues={
               ":n": password
          }
     )

def update_user_income(UserID, income):
     table = dynamodb.Table('Users')
     response = table.update_item(
          Key={'UserUUID': UserID},
          UpdateExpression = "set #income = :n",
          ExpressionAttributeNames={
               "#income": "Yearly Income - Person"
          },
          ExpressionAttributeValues={
               ":n": income
          }
     )
     status_code = {"status_code": 200}
     return (json.dumps(status_code))

def update_user_budget_option(UserID, budget_choice):
     table = dynamodb.Table('Users')
     response = table.update_item(
          Key={'UserUUID': UserID},
          UpdateExpression = "set #budget_choice = :n",
          ExpressionAttributeNames={
               "#budget_choice": "Budget Choice"
          },
          ExpressionAttributeValues={
               ":n": budget_choice
          }
     )


"""
STILL NEED FUNCTIONS FOR:
    update functions for each attribute in user?
    get card information? what for?
    get specific merchant info?
        
STILL NEED TO:
    add exception handling
    recreate users table with preferences?
    """

def main():
    UserID = query_user_login("gunter.welk@gmail.com", "guntersnewpassword!") #just a sample login
    #UserID = query_user_login("vanessa.anderson@gmail.com", "VanessaAnderson123")
    #get_user_cards(str(UserID))
    #update_user_password("7d49c831-ff33-49bd-9afd-2d061c61ea25", "guntersnewpassword!")
    print(update_user_income("7d49c831-ff33-49bd-9afd-2d061c61ea25", "69000"))
    #get_user_transaction("85d0f024-bbac-411b-b0fb-69bbe3682cf2")
    #insert_transaction(420.69, 0, "3:32", 22, 11, 2021, "No", 5541, "Richmond", "VA", '2e62a0d3-ac63-4077-8784-7dda1c678927', "Chip Transaction", 'b84d7a7e-e05e-4505-870d-d6d229f9d6b0', 23220)
    #insert_user("1411 Grove Ave", "11", "August", "2001", "Richmond", 22, "welka@vcu.edu", 750, "male", "37.54873869465798", "37.54873869465798, -77.45798251781274", 
                #2, "AlexWelk123", 10000, "Alex Welk", 70, "VA", 0, 10000, 23220)
    #insert_user_onboarding("gunter.welk@gmail.com", "gunterthecat!", 10, 19, 6900, 23220, 50000, "50-30-20")

    
    
if __name__=="__main__":
    main()