import requests 
from bs4 import BeautifulSoup
from psycopg2 import sql, connect
from dotenv import load_dotenv
import os

# Importing all of the models 
from models import Expansion, StageBasicPokemonCard, StageNonBasicPokemonCard, TrainerItemCard, TrainerSupporterOrToolCard, expansions, PokemonType, PokemonAbility, PokemonMove, Card
import models

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

def get_card_health(card_soup: BeautifulSoup):
    card_health = -1
    health_list_unprocessed = [element for element in card_soup.find("p", class_="card-text-title").text.strip().split(" ") if len(element.strip()) > 0]
    if 'HP' in health_list_unprocessed:
        card_health = health_list_unprocessed[-2]

    return card_health

def get_card_type(card_soup: BeautifulSoup):
    type_list_unprocessed = [element for element in card_soup.find("p", class_='card-text-title').text.strip().split(" ") if len(element.strip()) > 0]
    return PokemonType[type_list_unprocessed[-4].upper()].name

def get_card_weakness(card_soup: BeautifulSoup):
    weakness_unprocessed = card_soup.find("p", class_='card-text-wrr').text.strip()
    weakness = [element for element in weakness_unprocessed.split(" ") if len(element) > 0]
    return PokemonType[weakness[1].upper()].name

def get_card_retreat_cost(card_soup: BeautifulSoup):
    retreat_cost_unprocessed = card_soup.find("p", class_='card-text-wrr').text.strip()
    retreat_cost = [element for element in retreat_cost_unprocessed.split(" ") if len(element) > 0]
    return int(retreat_cost[-1])

def get_card_moves(card_soup: BeautifulSoup) -> list[PokemonMove]:
    pokemon_moves = []
    moves_container = card_soup.find_all("div", class_='card-text-attack')
    for container in moves_container:
        moves_info = container.find("p", class_='card-text-attack-info').text.strip()
        # If this cannot be found, then there must be no description for that attack
        moves_description = container.find("p", class_='card-text-attack-effect').text.strip()

        moves_list = [element for element in moves_info.split(" ") if len(element) > 0]
        move_name = ''
        move_damage = 0
        # Need to account for moves that don't have damage
        move_name = " ".join(moves_list[1:len(moves_list) - 1])
        move_damage = 0
        if moves_list[-1].isalpha():
            # This means that the move does not do any damage and the last element is also a part of the move's name
            move_name += " " + moves_list[-1]
        else:
            # This means the last element is the damage
            move_damage = moves_list[-1]

        move = PokemonMove(move_name, move_damage, moves_description)
        pokemon_moves.append(move)
    
    return pokemon_moves
        



def get_card_ability(card_soup: BeautifulSoup):
    try:
        ability_name_unprocessed = card_soup.find("p", class_='card-text-ability-info').text.strip()
        ability_description = card_soup.find("p", class_='card-text-ability-effect').text.strip()
        ability_name = " ".join([element for element in ability_name_unprocessed.split(" ") if len(element.strip()) > 0][1:])
        
        pokemon_ability = PokemonAbility(ability_name, ability_description)

        return pokemon_ability
    except: 
        return None
    
def get_evolves_from(card_soup: BeautifulSoup) -> str:
    return card_soup.find('p', class_='card-text-type').find('a').text

def get_card_info_as_tuple(card: Card):
    # These are guaranteed to exist for every single card
    card_name = card.get_name()
    card_rarity = card.get_rarity()
    card_image = card.get_card_image()
    card_is_promo = card.get_is_promo()
    card_illustrator = card.get_illustrator()
    card_expansion = card.get_expansion()
    card_expansion_number = card.get_expansion_number()

    # These are the more troublesome properties that some cards may have!
    card_health = card_pokemon_type = card_stage = card_weakness = card_evolves_from = card_description = card_is_supporter = card_move_1 = card_move_2 = card_ability = None

    try:
        card_health = card.get_health()
    except:
        # This means that the card does not have a health value
        pass
    try:
        card_pokemon_type = card.get_type()
    except:
        # This means that the card does not have a type
        pass
    try:
        card_stage = card.get_stage()
    except:
        # This means the card does not have a stage
        pass
    try:
        card_weakness = card.get_weakness()
    except:
        # This means the card type does not have weaknesses
        pass
    try:
        card_evolves_from = card.get_evolves_from()
    except:
        # This means that this card type does not have a pre-evolution
        pass
    try:
        card_description = card.get_description()
    except:
        # This means that the card does not have a description
        pass
    try:
        card_is_supporter = card.get_is_supporter()
    except:
        # This means the card is not a supporter 
        pass
    try:
        card_moves = card.get_moves()
        card_move_1, card_move_2 = card_moves[0], None if len(card_moves) == 1 else card_moves[0], card_moves[1]
    except:
        # This means that the card does not have any moves
        pass
    try:
        card_ability = card.get_ability()
    except:
        # This means that the card does not have an ability
        pass

    
    if card_ability:
        # Will need to check if the ability already exists in the database
        ability_exists_check_query = sql.SQL('SELECT {field} FROM {table} WHERE {name_column} = %s AND {description_column} = %s').format(
            field = sql.Identifier('id'),
            table = sql.Identifier(ABILITIES_TABLE),
            name_column = sql.Identifier('ability_name'),
            description_column = sql.Identifier('description')
        )

        cursor.execute(ability_exists_check_query, (card_ability.get_name(), card_ability.get_description()))

        # This will print if the ability of the card already exists in the database
        exists = cursor.fetchone()
        
        if not exists:
            data = {
                "ability_name": card_ability.get_name(),
                "description": card_ability.get_description()
            }

            # Need to create a new move, and then assign the ID
            ability_create_query = sql.SQL('INSERT INTO {table} ({fields}) VALUES ({values}) RETURNING id').format(
                table = sql.Identifier(ABILITIES_TABLE),
                fields = sql.SQL(', ').join([
                    sql.Identifier('ability_name'),
                    sql.Identifier('description'),
                ]),
                values = sql.SQL(", ").join(sql.Placeholder() * len(data))
            )

            cursor.execute(ability_create_query, tuple(data.values()))
            card_ability = cursor.fetchone()[0]
            print(card_ability)
        else:
            print("The ability already exists in the database")
            card_ability = exists[0]
            print(card_ability)
    if card_move_1:
        pass
    if card_move_2:
        pass

    data_for_cards = (card_name, card_health, card_pokemon_type, card_stage, card_weakness, card_rarity, card_image, card_is_promo, card_evolves_from, card_illustrator, card_description, card_is_supporter, card_expansion, card_expansion_number)

    

def webscrape_new_cards(expansion_identifier: str, card_number):
    card_page = requests.get(f"{EXPANSION_URL}/{expansion_identifier}/{card_number}")
    card_soup = BeautifulSoup(card_page.content, "html.parser")

    # Some information that we know all cards to have, then we will delve into the specific card types

    # The card name 
    card_name = card_soup.find("span", class_="card-text-name").text

    # Determine if the card is a promo card
    card_is_promo = expansion_identifier.startswith('P-')

    # The card's rarity
    rarity_container = card_soup.find("div", class_='prints-current-details')

    rarity_text_unprocessed = rarity_container.find("span", class_='text-lg').find_next('span').text
    rarity_text_list = [element for element in rarity_text_unprocessed.split("\n") if len(element.strip()) > 0]
    rarity_string = rarity_text_list[0].strip().split(" ")
    card_rarity = 0

    try:
        # For some reason, the promos have no rarity, thus trying to print the second index will throw an index out of bounds exception
        card_rarity = len(rarity_string[2]) if card_is_promo else 0
    except:
        print("Dealing with a promo card, has no rating!")

    # The card's image
    card_image_container = card_soup.find("div", class_='card-image')
    card_image = card_image_container.find("img", class_='card shadow resp-w')['src']
        
    # The card's illustrator
    card_illustrator_container = card_soup.find("div", class_='card-text-section card-text-artist')
    card_illustrator = card_illustrator_container.find("a").text.strip()

    # Remember, this is a foreign key to the expansion_table!
    card_expansion = expansion_identifier
    card_expansion_number = card_number


    # At this point, all of the information that every card has has been retrieved, now it's a matter of creating the right object depending on the card type
    card_type = [element.strip() for element in card_soup.find("p", class_='card-text-type').text.strip().split(" ") if len(element) > 0]
    
    # This will contain all of the new cards that need to be added to the database
    new_entries = []

    if card_type[0] == 'Trainer':
        # Getting the description
        card_description = card_soup.find("div", class_='card-text-section').find_next('div').text.strip()
            
        # This means it's a trainer card, which means it could be an item, tool or supporter card
        if card_type[-1] == 'Item':
            # We need the health and the description (in the case of a fossil)
            # Fossil check
            card_health = get_card_health(card_soup)

            # Creating the object that represents an item card 
            trainer_item_card = TrainerItemCard(card_name, card_rarity, card_image, card_is_promo, card_illustrator, card_description, card_expansion, card_expansion_number, card_health)
            new_entries.append(trainer_item_card)
            # TODO: Will need to write this information to the database
        elif card_type[-1] == 'Supporter':
            is_supporter = True 
            trainer_supporter_card = TrainerSupporterOrToolCard(card_name, card_rarity, card_image, card_is_promo, card_illustrator, card_description, is_supporter, card_expansion, card_expansion_number)
            new_entries.append(trainer_supporter_card)
            # TODO Will need to write this information to the database
        elif card_type[-1] == 'Tool':
            is_supporter = False
            trainer_tool_card = TrainerSupporterOrToolCard(card_name, card_rarity, card_image, card_is_promo, card_illustrator, card_description, is_supporter, card_expansion, card_expansion_number)
            new_entries.append(trainer_tool_card)
            # TODO: Will need to write this information to the database

    else:
        pokemon_card_health = get_card_health(card_soup)
        pokemon_card_type = get_card_type(card_soup)
        pokemon_card_weakness = get_card_weakness(card_soup)
        pokemon_card_retreat_cost = get_card_retreat_cost(card_soup)
        # This will need to be written to a separate table
        pokemon_card_moves = get_card_moves(card_soup)
        # This will also need to be written to a separate table
        pokemon_card_ability = get_card_ability(card_soup)

        # This means it's either a basic, stage 1 or 2 pokemon
        if card_type[2] == 'Basic':
            # This means we are dealing with a basic pokemon                    
            stage_basic_pokemon = StageBasicPokemonCard(card_name, pokemon_card_health, pokemon_card_type, pokemon_card_weakness, pokemon_card_retreat_cost, card_rarity, pokemon_card_moves, pokemon_card_ability, card_image, card_is_promo, card_illustrator, card_expansion, card_expansion_number)
            # TODO: Need to write this information to the database
            new_entries.append(stage_basic_pokemon)
        else:
            card_pre_evolution = get_evolves_from(card_soup)

            # This means we are dealing with a stage 1 or 2 pokemon
            if card_type[3] == '1':
                stage_non_basic_pokemon = StageNonBasicPokemonCard(card_name, pokemon_card_health, pokemon_card_type, pokemon_card_weakness, pokemon_card_retreat_cost, card_rarity, pokemon_card_moves, pokemon_card_ability, card_image, card_is_promo, card_illustrator, 1, card_pre_evolution, card_expansion, card_expansion_number)
                # TODO: Will need to write this information to the database, I wonder if I can use a bulk insert operation?
                new_entries.append(stage_non_basic_pokemon)
            elif card_type[3] == '2':
                stage_non_basic_pokemon = StageNonBasicPokemonCard(card_name, pokemon_card_health, pokemon_card_type, pokemon_card_weakness, pokemon_card_retreat_cost, card_rarity, pokemon_card_moves, pokemon_card_ability, card_image, card_is_promo, card_illustrator, 2, card_pre_evolution, card_expansion, card_expansion_number)
                # TODO: Will need to write this information to the database
                new_entries.append(stage_non_basic_pokemon)

    for card in new_entries:
        get_card_info_as_tuple(card)


def insert_new_cards(expansion_identifier: str, number_cards: int, new_promo_cards: bool) -> None:
    # Will need the expansion identifier, and will need to know if it's new promo cards being added 
        # If this is the case, it will be quite simple to get the card number from which we need to start webscraping from 
    # If it's an entirely new expansion, we will have to webscrape the entire set, this will be a time consuming operation! 
    if not new_promo_cards:
        # This means it's an entirely new expansion that needs to be added
        # Time to do some more webscraping
        for card_number in range(1, number_cards + 1):
            webscrape_new_cards(expansion_identifier, card_number)
    else:
        # Will need to get the current number of cards in the database for the promo missing cards
        promo_card_count_query = sql.SQL("SELECT {field} FROM {table} WHERE {expansion_identifier} = %s").format(
            field = sql.Identifier('number_cards'),
            table = sql.Identifier(EXPANSIONS_TABLE),
            expansion_identifier = sql.Identifier('expansion_identifier')
        )

        cursor.execute(promo_card_count_query, (expansion_identifier,))

        most_recent_number_cards = cursor.fetchall()

        # We know the numbers to be mismatched, so now we need to webscrape the missing cards
        for card_number in range(most_recent_number_cards[0][0] + 1, number_cards + 1):
            webscrape_new_cards(expansion_identifier, card_number)


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
        insert_new_cards(identifier, number_cards, True)
        # TODO: Will need a method call to add the new cards in the promo to the set
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
            insert_new_cards(expansion.get_expansion_identifier(), expansion.get_number_cards(), False)
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



#expansions = load_expansions()
#check_for_updates(expansions)


# Testing
insert_new_cards('A2', 207, False)
connection.commit()
connection.close()
#insert_new_cards('P-A', 117, True)