import requests 
from bs4 import BeautifulSoup
import boto3
import psycopg2
from dotenv import load_dotenv
import os

# Importing all of the models 
from models import Expansion, StageBasicPokemonCard, StageNonBasicPokemonCard, TrainerItemCard, TrainerSupporterOrToolCard, expansions

# TODO: Create the table in RDS that will store all of the information
# TODO: Actually create the script that will webscrape and then write the information to the database

# Loading environment variables in the .env file 
load_dotenv()

DATABASE = os.getenv('RDS_DATABASE')
USER = os.getenv('RDS_USER')
PASSWORD = os.getenv('RDS_PASSWORD')
HOSTNAME = os.getenv('RDS_HOSTNAME')

# This is the website where I get all of the information about the game from
EXPANSION_URL = "https://pocket.limitlesstcg.com/cards"

ABILITIES_TABLE = "abilities"
CARDS_TABLE = "cards"
EXPANSIONS_TABLE = "expansion_table"
MOVES_TABLE = "moves"

# Creating the database connection
connection = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOSTNAME, port=5432)
cursor = connection.cursor()


'''
cursor.execute("SELECT * FROM public.abilities;")

record = cursor.fetchall()

print("Data from the database: ", record)
'''

def check_for_updates():
    # TODO: Implement 
    # TODO: Create a check for updates method that will do this exact procedure!


    pass

# The table containing all of the information has a class of data-table-sets-table striped
def load_expansions():
    expansion_page = requests.get(EXPANSION_URL)

    expansion_soup = BeautifulSoup(expansion_page.content, "html.parser")

    # Luckily for me, all of the expansions are in a table that are the same format for every row
    expansions_table = expansion_soup.find("table", class_="data-table sets-table striped")
    rows = expansions_table.find_all("a")

    for row in range(int(len(rows) / 3)):
        set_name = ""
        set_release_date = "" 
        set_number_cards = -1
        set_expansion_identifier = ""

        current_row = 3 * row
        release_date_row = current_row + 1
        number_of_cards_row = current_row + 2

        row_array = rows[current_row].text.split("\n")

        for element in row_array:
            element = element.strip()
            if len(element) > 0:
                element = element.replace("\n", "")
                if element in expansions.keys():
                    # This means it's the expansion identifier 
                    set_expansion_identifier = element.strip()
                else:
                    # This means it's the pack's name 
                    set_name = element.strip()
        
        # For some reason, the source that I am using does not have a release date for the promo packs, if that is the case, just use the release date of the pack that comes right after it
        set_release_date = rows[release_date_row].text if len(rows[release_date_row]) > 0 else rows[release_date_row - 3].text 
        set_number_cards = int(rows[number_of_cards_row].text)

        expansion = Expansion(set_name, set_release_date, set_number_cards, set_expansion_identifier)

        # TODO: Since the promos are constantly updating depending on what expansion we are on, we will require a method that will compare the number of cards retrieved 
        # from the webscrape and compare it to the number stored in the database at the time. If they differ, then we know there are new cards in the promo set!
       


load_expansions()