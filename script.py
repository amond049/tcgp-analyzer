import requests 
from bs4 import BeautifulSoup
import boto3
from psycopg2 import sql, connect
from dotenv import load_dotenv
import os

# Importing all of the models 
from models import Expansion, StageBasicPokemonCard, StageNonBasicPokemonCard, TrainerItemCard, TrainerSupporterOrToolCard, expansions

# TODO: Now that we create the expansion table, we will need to actually write all of the cards to the database, this will require more work and will be done afterwards

# Loading environment variables in the .env file 
load_dotenv()

DATABASE = os.getenv('RDS_DATABASE')
USER = os.getenv('RDS_USER')
PASSWORD = os.getenv('RDS_PASSWORD')
HOSTNAME = os.getenv('RDS_HOSTNAME')

# This is the website where I get all of the information about the game from
EXPANSION_URL = "https://pocket.limitlesstcg.com/cards"

ABILITIES_TABLE = os.getenv("ABILITIES_TABLE")
CARDS_TABLE = os.getenv("CARDS_TABLE")
EXPANSIONS_TABLE = os.getenv("EXPANSIONS_TABLE")
MOVES_TABLE = os.getenv("MOVES_TABLE")

# Creating the database connection
connection = connect(database=DATABASE, user=USER, password=PASSWORD, host=HOSTNAME, port=5432)
cursor = connection.cursor()


def insert_new_cards(expansion_identifier: str, new_promo_cards: bool) -> None:
    # Will need the expansion identifier, and will need to know if it's new promo cards being added 
        # If this is the case, it will be quite simple to get the card number from which we need to start webscraping from 
    # If it's an entirely new expansion, we will have to webscrape the entire set, this will be a time consuming operation! 
    raise NotImplementedError("Still need to implement this method!")

def update_card_count_in_promo(to_update_dictionary: dict[str, int]) -> None:
    for identifier, number_cards in to_update_dictionary.items():
        update_query = sql.SQL("UPDATE {table} SET {assignments} WHERE {field} = %s").format(
            table = sql.Identifier(EXPANSIONS_TABLE),
            assignments = sql.SQL(", ").join(
                sql.SQL("{} = %s").format(sql.Identifier(col))
                for col in ["number_cards"]
            ),
            field = sql.Identifier('expansion_identifier')
        )

        cursor.execute(update_query, (number_cards, identifier))
    
    # Closing the connection to avoid memory leaks
    connection.commit()
    connection.close()

def update_database_with_new_expansion(expansions_in_db: list, expansions: list) -> None:
    # Getting only the expansion identifier from the table as those are unique and will be used to identify 
    # which sets are already in the database
    identifiers_as_list = [expansion[0] for expansion in expansions_in_db]

    for expansion in expansions: 
        if expansion.get_expansion_identifier() not in identifiers_as_list:
            # Creating the row from the new data
            data = {
                "expansion_identifier": expansion.get_expansion_identifier(),
                "expansion_name": expansion.get_name(),
                "release_date": expansion.get_release_date(),
                "number_cards": expansion.get_number_cards()
            }

            # Creating the insert query
            insert_query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({values})").format(
                table=sql.Identifier(EXPANSIONS_TABLE),
                fields=sql.SQL(", ").join(map(sql.Identifier, data.keys())),
                values=sql.SQL(", ").join(sql.Placeholder() * len(data))
            )

            # Executing the query
            cursor.execute(insert_query, tuple(data.values()))

            # TODO: Will need a function call here to load the new cards from the new expansions in the database
    
    # Closing the connection to avoid memory leaks
    connection.commit()
    connection.close()


def check_for_updates(expansions: list) -> None:
    # Compare the list of expansions with that of the results retrieved from the database
    retrieve_expansion_query = sql.SQL("SELECT {field} FROM {table}").format(
        field=sql.SQL(', ').join([
            sql.Identifier('expansion_identifier'),
            sql.Identifier('expansion_name'),
            sql.Identifier('number_cards'),
            sql.Identifier('release_date'),
        ]),
        table=sql.Identifier(EXPANSIONS_TABLE))
    
    cursor.execute(retrieve_expansion_query)

    expansion_results = cursor.fetchall()
    
    # The expansion_results is a list of items
    if len(expansion_results) != len(expansions):
        # This means there's a new expansion that was webscraped that is not in the database, need an update
        print("A new expansion has been released, need to update the database")
        update_database_with_new_expansion(expansion_results, expansions)
    else:
        print("All expansions already exist in the database, checking if any new promo cards have been released")
        # All promos have an expansion identifier of the form P-, need to get the number of cards for each set and then compare them with the webscraped data
        promos_from_db = {f"{expansion[0]}" : expansion[2] for expansion in expansion_results if expansion[0].startswith('P-')}
        # We now have all the promo expansions as well as the number of cards, now we need to get the webscraped promo information
        promos_from_webscrape = {f"{expansion.get_expansion_identifier()}": expansion.get_number_cards() for expansion in expansions if expansion.get_expansion_identifier().startswith('P-')}

        if promos_from_db != promos_from_webscrape:
            print("There are new promo cards that have been released, need to update")
            to_update = {}
            for identifier, number_cards in promos_from_webscrape.items():
                if promos_from_db.get(identifier) != number_cards:
                    to_update[identifier] = number_cards

            update_card_count_in_promo(to_update)
        else:
            print("All cards are up to date, exiting the program")
            connection.commit()
            connection.close()

# The table containing all of the information has a class of data-table-sets-table striped
def load_expansions() -> list:
    expansion_page = requests.get(EXPANSION_URL)

    expansion_soup = BeautifulSoup(expansion_page.content, "html.parser")

    # Luckily for me, all of the expansions are in a table that are the same format for every row
    expansions_table = expansion_soup.find("table", class_="data-table sets-table striped")
    rows = expansions_table.find_all("a")

    total_expansions = []

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
        total_expansions.append(expansion)

    return total_expansions



expansions = load_expansions()
check_for_updates(expansions)