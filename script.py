import requests 
from bs4 import BeautifulSoup
import boto3

# Importing all of the models 
from models import Expansion, StageBasicPokemonCard, StageNonBasicPokemonCard, TrainerItemCard, TrainerSupporterOrToolCard


# TODO: Create the table in RDS that will store all of the information
# TODO: Actually create the script that will webscrape and then write the information to the database
