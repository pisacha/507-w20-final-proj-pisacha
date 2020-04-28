##############################################
########   Name: Pisacha Wichianchan   #######
########   Uniqname: pisacha           #######
##############################################

##############################################
############## import libraries ##############
##############################################
from bs4 import BeautifulSoup
import requests
import json
import time # need this in order to sleep()
import random
import webbrowser # open URLs in a web browser
import sys # to use sys.exit()
import sqlite3
from prettytable import PrettyTable
import plotly.graph_objs as go
import numpy as np


##############################################
############## global variables ##############
##############################################
BASE_URL = 'https://livingwage.mit.edu'
LOCATIONS_PATH = '/states/26/locations'
MICHIGAN_URL = BASE_URL + LOCATIONS_PATH

CACHE_FILENAME = 'living_wage_cache.json'
CACHE_DICT = {}

DB_NAME = 'living_wage.sqlite'

FIPS_AREA_LIST = []


##############################################
############# classes & objects ##############
##############################################
class Area:
    '''either a county or a metropolitan statistical area (MSA) in Michigan

    Instance Attributes
    -------------------
    name: string
        the name of a area (e.g. 'Washtenaw County' or 'Ann Arbor')

    area_type: string
        the category of the area (e.g. 'County' or 'MSA')
    '''
    def __init__(self, name, area_type):
        self.name = name
        self.area_type = area_type


    def info(self):
        ''' Get the name and category of a specific area in Michigan
        and returned in a formatted string.

        Parameters
        ----------
        none

        Returns
        -------
        str
            Information about a specific area in a formatted string.
        '''
        return (f"{self.name} (Type: {self.area_type})")


##############################################
################# instances ##################
##############################################
def get_area_instance(specific_location_url):
    ''' Make an instances from the area URL.
    
    Parameters
    ----------
    specific_location_url: string
        Thr URL for a county or an MSA in the Michigan page of 
        the MIT Living Wage website, 
        i.e. https://livingwage.mit.edu/states/26/locations
    
    Returns
    -------
    instance
        an area instance
    '''
    url_text = make_request_with_cache(specific_location_url, CACHE_DICT)
    soup = BeautifulSoup(url_text, 'html.parser')

    pre_names = soup.find('div', class_="container")
    names = pre_names.find('h1')
    for name in names:
        clean_name_1 = name.strip()
        clean_name_2 = clean_name_1.replace('Living Wage Calculation for ', '')
        clean_name_3 = clean_name_2.replace(', Michigan', '').replace(', MI', '')

    area_type = ''
    if 'county' in clean_name_2.lower():
        area_type = "County"
    else:
        area_type = "MSA"

    area_without_info_function = Area(name = clean_name_3, area_type = area_type)
    return area_without_info_function


def get_areas_for_state(specific_location_url):
    ''' Make a list of area instances from a state URL.
    
    Parameters
    ----------
    specific_location_url: string
        Thr URL for a county or an MSA in the Michigan page of 
        the MIT Living Wage website, 
        i.e. https://livingwage.mit.edu/states/26/locations
    
    Returns
    -------
    list
        a list of area instances
    '''
    combined_url_dict = build_combined_dict()

    area_instances = []
    for area_name, area_url in combined_url_dict.items():
        area_instances.append(get_area_instance(area_url))
    return area_instances


##############################################
################ scrape urls #################
##############################################
def build_county_url_dict():
    ''' Make a dictionary that maps county name to county page url from 
    the state-specific page (e.g. Michigan) of the MIT Living Wage website

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a county name and value is the url
        e.g. {'washtenaw':'https://livingwage.mit.edu/counties/26161', ...}
    '''
    county_url_dict = {}

    ## Make the soup for the Michigan page
    url_text = make_request_with_cache(MICHIGAN_URL, CACHE_DICT)
    soup = BeautifulSoup(url_text, 'html.parser')

    ## For each county listed
    county_listing_grandparent = soup.find('div', class_='container')
    county_listing_parent = county_listing_grandparent.find('div', class_='counties list-unstyled')
    county_listing_uls = county_listing_parent.find_all('ul', recursive=False)

    for county_listing_ul in county_listing_uls:
        ## extract the county details URL
        county_link_tags = county_listing_ul.find_all('a')
        for county_link_tag in county_link_tags:
            lowercase_county = county_link_tag.text.strip().lower()
            county_details_path = county_link_tag['href']
            county_details_url = BASE_URL + county_details_path
            # print(county_details_url) ## sanity check -- test then delete
            if lowercase_county not in county_url_dict.keys():
            # if the county is not in the dictionary
                county_url_dict[lowercase_county] = county_details_url

    return county_url_dict


def build_msa_url_dict():
    ''' Make a dictionary that maps metropolitan statistical area (MSA) name to MSA page 
    url from the state-specific page (e.g. Michigan) of the MIT Living Wage website

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is an MSA name and value is the url
        e.g. {'ann arbor, mi': 'https://livingwage.mit.edu/metros/11460', ...} 
    '''
    msa_url_dict = {}

    ## Make the soup for the Michigan page
    url_text = make_request_with_cache(MICHIGAN_URL, CACHE_DICT)
    soup = BeautifulSoup(url_text, 'html.parser')

    ## For each MSA listed
    msa_listing_grandparent = soup.find('div', class_='container')
    msa_listing_parent = msa_listing_grandparent.find('div', class_='metros list-unstyled')
    msa_listing_uls = msa_listing_parent.find_all('ul', recursive=False)

    for msa_listing_ul in msa_listing_uls:
        ## extract the MSA details URL
        msa_link_tags = msa_listing_ul.find_all('a')
        for msa_link_tag in msa_link_tags:
            lowercase_msa = msa_link_tag.text.strip().lower()
            msa_details_path = msa_link_tag['href']
            msa_details_url = BASE_URL + msa_details_path
            # print(msa_details_url) ## sanity check -- test then delete
            if lowercase_msa not in msa_url_dict.keys():
            # if the county is not in the dictionary
                msa_url_dict[lowercase_msa] = msa_details_url

    return msa_url_dict


def build_combined_dict():
    ''' Make a dictionary that maps names of counties and metropolitan statistical areas (MSAs) 
    to respective county or MSA page url from the state-specific page (e.g. Michigan) of the 
    MIT Living Wage website

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a location name (either county or MSA) and value is the url
        e.g. {'washtenaw':'https://livingwage.mit.edu/counties/26161', ...,
        'ann arbor, mi': 'https://livingwage.mit.edu/metros/11460', ...} 
    '''
    combined_url_dict = {}

    county_url_dict = build_county_url_dict()
    msa_url_dict = build_msa_url_dict()

    ## https://www.geeksforgeeks.org/python-merging-two-dictionaries/
    combined_url_dict.update(county_url_dict)
    combined_url_dict.update(msa_url_dict)
    
    return combined_url_dict


##############################################
########## scrape data from tables ###########
##############################################
def scrape_wages_tables(specific_location_url):
    '''Scrapes wage data for each family composition in a certain county or MSA

    Parameters
    ----------
    specific_location_url: string
        Thr URL for a county or an MSA in the Michigan page of 
        the MIT Living Wage website, 
        i.e. https://livingwage.mit.edu/states/26/locations

    Returns
    -------
    nested dict
        key is the number of adults 
            (i.e. 'one adult', 'two adults (one working)', 'two adults (both working))
        value is number of children
            (i.e. '0 children', '1 child', '2 children', '3 children')
        nested key is type of wage
            (i.e. 'living wage', 'poverty wage', 'minimum wage')
        nested value is wage values
            (e.g. '$39.05', '$12.38', '$9.45')
    '''
    ################ Make the soup for location page ################
    ######## e.g. https://livingwage.mit.edu/counties/26161 #########
    ######### e.g. https://livingwage.mit.edu/metros/11460 ##########
    url_text = make_request_with_cache(specific_location_url, CACHE_DICT)
    soup = BeautifulSoup(url_text, 'html.parser')

    ################ Number of adults list ################
    ## Would have been easier to type, but let's scrape for practice
    household_composition_list = []
    HC_grandparents = soup.find('thead')
    HC_parents = HC_grandparents.find('tr')
    HCs = HC_parents.find_all('th', recursive=False)

    for HC in HCs:
        clean_HC_1 = HC.text.strip().lower()
        clean_HC_2 = clean_HC_1.split('(')
        clean_HC_3 = " (".join(clean_HC_2)
        household_composition_list.append(clean_HC_3)
        ## Output: ['', '1 adult', '2 adults (1 working)', '2 adults (both working)']
    clean_composition_list = household_composition_list[1:]
    ## Output: [1 adult', '2 adults (1 working)', '2 adults (both working)']

    ################ Number of children list ################
    ## Now that I am confident in scraping, let's just type out the list since it's simpler
    count_of_children_list = ['0 children', '1 child', '2 children', '3 children']

    ################ Living wage lists ################
    living_wage_list = []
    wage_grandparents = soup.find('tbody')
    LW_parents = wage_grandparents.find('tr', class_="odd results")
    LWs = LW_parents.find_all('td', recursive=False)

    for LW in LWs:
        clean_LW1 = LW.text.strip().lower()
        clean_LW2 = clean_LW1.split('$')[-1]
        living_wage_list.append(clean_LW2)
    temp_living_wage_list = living_wage_list[1:]

    clean_living_wage_list = []
    for each_item in temp_living_wage_list:
        each_item = float(each_item)
        clean_living_wage_list.append(each_item)

    living_wage__1_adult_list = clean_living_wage_list[0:4]
    living_wage_2_adults_1_working_list = clean_living_wage_list[4:8]
    living_wage_2_adults_both_working_list = clean_living_wage_list[8:]

    ################ Poverty wage lists ################
    poverty_wage_list = []
    wage_grandparents = soup.find('tbody')
    PovWage_parents = wage_grandparents.find('tr', class_="even")
    PovWages = PovWage_parents.find_all('td', recursive=False)

    for PovWage in PovWages:
        clean_PovWage1 = PovWage.text.strip().lower()
        clean_PovWage2 = clean_PovWage1.split('$')[-1]
        poverty_wage_list.append(clean_PovWage2)
    temp_poverty_wage_list = poverty_wage_list[1:]

    clean_poverty_wage_list = []
    for each_item in temp_poverty_wage_list:
        each_item = float(each_item)
        clean_poverty_wage_list.append(each_item)

    poverty_wage_1_adult_list = clean_poverty_wage_list[0:4]
    poverty_wage_2_adults_1_working_list = clean_poverty_wage_list[4:8]
    poverty_wage_2_adults_both_working_list = clean_poverty_wage_list[8:]


    ################ Minimum wage list ################
    minimum_wage_list = []
    wage_grandparents = soup.find('tbody')
    LW_parents = wage_grandparents.find('tr', class_="odd") 
    ## multiple 'tr' and 'odd'/'odd results'
    MinWage_parents = LW_parents.find_next_siblings('tr', class_="odd")

    for MinWage_parent in MinWage_parents:
        MinWages = MinWage_parent.find_all('td', class_="red", recursive=False)

        for MinWage in MinWages:
            clean_MinWage1 = MinWage.text.strip().lower()
            clean_MinWage2 = clean_MinWage1.split('$')[-1]
            # print(clean_MinWage) #sanity check -- comment out later
            minimum_wage_list.append(clean_MinWage2)
            ## no need to separate into different adult compositions, because minimum wage is the same for all

    clean_minimum_wage_list = []
    for each_item in minimum_wage_list:
        each_item = float(each_item)
        clean_minimum_wage_list.append(each_item)


    ############### Put scraped data (currently in lists) ###############
    ##################### into a  nested dictionary #####################
    one_adult_dict = {}
    for i in range(len(count_of_children_list)):
        one_adult_dict[count_of_children_list[i]] = {
            'living wage': living_wage__1_adult_list[i],
            'poverty wage': poverty_wage_1_adult_list[i],
            'minimum wage': clean_minimum_wage_list[i]
        }
    # print("one_adult_dict")
    # print(one_adult_dict)

    two_adults_one_working_dict = {}
    for i in range(len(count_of_children_list)):
        two_adults_one_working_dict[count_of_children_list[i]] = {
            'living wage': living_wage_2_adults_1_working_list[i],
            'poverty wage': poverty_wage_2_adults_1_working_list[i],
            'minimum wage': clean_minimum_wage_list[i]
        }
    # print("two_adults_one_working_dict")
    # print(two_adults_one_working_dict)

    two_adults_both_working_dict = {}
    for i in range(len(count_of_children_list)):
        two_adults_both_working_dict[count_of_children_list[i]] = {
            'living wage': living_wage_2_adults_both_working_list[i],
            'poverty wage': poverty_wage_2_adults_both_working_list[i],
            'minimum wage': clean_minimum_wage_list[i]
        }
    # print("two_adults_both_working_dict")
    # print(two_adults_both_working_dict)

    ## How to insert a dictionary in another dictionary in Python (how to merge two dictionaries)
    ## https://code-maven.com/how-to-insert-a-dictionary-in-another-dictionary-in-python
    wages_dict = {}
    wages_dict['one adult'] = one_adult_dict
    wages_dict['two adults (one working)'] = two_adults_one_working_dict
    wages_dict['two adults (both working)'] = two_adults_both_working_dict

    return wages_dict


def match_location_names_to_wages_dict():
    '''Scrapes wage data for each family composition in all counties and MSAs in a state
    and add the name of each county or MSA as the main key

    Parameters
    ----------
    None

    Returns
    -------
    nested dict
        main key is the area (either county or MSA)
        values of each main key are as follows:
            nested key no. 1 is the number of adults 
                (i.e. 'one adult', 'two adults (one working)', 'two adults (both working))
            nested value no. 1 is number of children
                (i.e. '0 children', '1 child', '2 children', '3 children')
            nested key no. 2 is type of wage
                (i.e. 'living wage', 'poverty wage', 'minimum wage')
            nested value no. 2 is wage values
                (e.g. '$39.05', '$12.38', '$9.45')
    '''
    ## add area names to complete the dictionary
    combined_url_dict = build_combined_dict()

    complete_wages_dict = {}
    for k, v in combined_url_dict.items():
        temp_dict = scrape_wages_tables(v)
        complete_wages_dict[k] = temp_dict
    return complete_wages_dict


def scrape_expenses_tables(specific_location_url):
    '''Scrapes expenses data for each family composition in a certain county or MSA

    Parameters
    ----------
    specific_location_url: string
        Thr URL for a county or an MSA in https://livingwage.mit.edu/

    Returns
    -------
    nested dict????????
        key is the number of adults 
            (i.e. 'one adult', 'two adults (one working)', 'two adults (both working))
        value is number of children
            (i.e. '0 children', '1 child', '2 children', '3 children')
        nested key is type of wage
            (i.e. 'living wage', 'poverty wage', 'minimum wage')
        nested value is wage values
            (e.g. '$39.05', '$12.38', '$9.45')
    '''
    ################ Make the soup for location page ################
    url_text = make_request_with_cache(specific_location_url, CACHE_DICT)
    soup = BeautifulSoup(url_text, 'html.parser')

    ################ Number of adults list ################
    household_composition_list = ['1 adult', '2 adults (1 working)', '2 adults (both working)']

    ################ Number of children list ################
    count_of_children_list = ['0 children', '1 child', '2 children', '3 children']

    ################ Living wage lists ################
    required_income_before_tax_list = []
    expenses_grandparents = soup.find('table', class_='results_table table-striped expense_table')
    expenses_parents = expenses_grandparents.find('tr', class_="odd") ## multiple 'tr' and 'odd'/'odd results'
    expenses_parents = expenses_parents.find_next_siblings('tr', class_="odd")

    for expenses_parent in expenses_parents:
        expenses = expenses_parent.find_all('td', recursive=False)
        for expense in expenses:
            clean_expenses1 = expense.text.strip().lower()
            clean_expenses2 = clean_expenses1.split('$')[-1]
            required_income_before_tax_list.append(clean_expenses2)
    temp_required_income_before_tax_list = required_income_before_tax_list[-12:]

    clean_required_income_before_tax_list = []
    for temp_required_income in temp_required_income_before_tax_list:
        each_item = "".join(temp_required_income.split(','))
        each_item = float(each_item)
        clean_required_income_before_tax_list.append(each_item)

    expenses_1_adult_list = clean_required_income_before_tax_list[:4]
    expenses_2_adults_1_working_list = clean_required_income_before_tax_list[4:8]
    expenses_2_adults_both_working_list = clean_required_income_before_tax_list[8:]

    ############### Put scraped data (currently in a list) ###############
    ######################### into a  dictionary #########################
    one_adult_dict = {}
    for i in range(len(count_of_children_list)):
        one_adult_dict[count_of_children_list[i]] = {
            'required annual income before taxes': expenses_1_adult_list[i]
        }
    # print("one_adult_dict")
    # print(one_adult_dict)

    two_adults_one_working_dict = {}
    for i in range(len(count_of_children_list)):
        two_adults_one_working_dict[count_of_children_list[i]] = {
            'required annual income before taxes': expenses_2_adults_1_working_list[i]
        }
    # print("two_adults_one_working_dict")
    # print(two_adults_one_working_dict)

    two_adults_both_working_dict = {}
    for i in range(len(count_of_children_list)):
        two_adults_both_working_dict[count_of_children_list[i]] = {
            'required annual income before taxes': expenses_2_adults_both_working_list[i]
        }
    # print("two_adults_both_working_dict")
    # print(two_adults_both_working_dict)

    ## How to insert a dictionary in another dictionary in Python (how to merge two dictionaries)
    ## https://code-maven.com/how-to-insert-a-dictionary-in-another-dictionary-in-python
    expenses_dict = {}
    expenses_dict['one adult'] = one_adult_dict
    expenses_dict['two adults (one working)'] = two_adults_one_working_dict
    expenses_dict['two adults (both working)'] = two_adults_both_working_dict

    return expenses_dict


def match_location_names_to_expenses_dict():
    '''Scrapes expense data for each family composition in all counties and MSAs in a state
    and add the name of each county or MSA as the main key

    Parameters
    ----------
    None

    Returns
    -------
    nested dict
        main key is the area (either county or MSA)
        values of each main key are as follows:
            nested key no. 1 is the number of adults 
                (i.e. 'one adult', 'two adults (one working)', 'two adults (both working))
            nested value no. 1 is number of children
                (i.e. '0 children', '1 child', '2 children', '3 children')
            nested key no. 2 is required annual income before taxes'
            nested value no. 2 is expense values, e.g. '$80,850'
    '''
    ## add area names to complete the dictionary
    combined_url_dict = build_combined_dict()

    complete_expenses_dict = {}
    for k, v in combined_url_dict.items():
        temp_dict = scrape_expenses_tables(v)
        complete_expenses_dict[k] = temp_dict
    return complete_expenses_dict


###############################################
############# populating database #############
###############################################
def create_db():
    ''' Create a SQL database if it doesn't already exist and populate data in the tables.
    If the database already exists, the function writes over the existing data.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    None
    '''
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    drop_areas_sql = 'DROP TABLE IF EXISTS "Areas"'
    drop_wages_sql = 'DROP TABLE IF EXISTS "Wages"'
    drop_expenses_sql = 'DROP TABLE IF EXISTS "Expenses"'

    create_areas_sql = '''
        CREATE TABLE IF NOT EXISTS "Areas" (
            "Id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "State" TEXT NOT NULL,
            "Area Type" TEXT NOT NULL,
            "Area" TEXT NOT NULL
        )
    '''

    create_wages_sql = '''
        CREATE TABLE IF NOT EXISTS "Wages" (
            "Id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "Area" TEXT NOT NULL,
            "Number of Adults" TEXT NOT NULL,
            "Number of Children" INTEGER NOT NULL,
            "Living Wage" REAL NOT NULL,
            "Poverty Wage" REAL NOT NULL,
            "Minimum Wage" REAL NOT NULL
        )
    '''

    create_expenses_sql = '''
        CREATE TABLE IF NOT EXISTS "Expenses" (
            "Id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "Area" TEXT NOT NULL,
            "Number of Adults" TEXT NOT NULL,
            "Number of Children" INTEGER NOT NULL,
            "Required Annual Income Before Taxes" REAL NOT NULL
        )
    '''

    cur.execute(drop_areas_sql)
    cur.execute(drop_wages_sql)
    cur.execute(drop_expenses_sql)
    cur.execute(create_areas_sql)
    cur.execute(create_wages_sql)
    cur.execute(create_expenses_sql)
    conn.commit()
    conn.close()


def load_areas():
    '''
    docstring
    '''
    areas = match_location_names_to_expenses_dict()
    combined_url_dict = build_combined_dict()

    insert_areas_sql = '''
        INSERT INTO Areas
        VALUES (NULL, ?, ?, ?)
    '''

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    for area in areas.keys():
        area_type = "" ## empty string 
        if ('county') in area:
           area_type = 'county'
        elif (', mi') in area:
           area_type = 'MSA'
        
        cur.execute(insert_areas_sql,
            [
                'MI',
                area_type,
                area
            ]
        )
    conn.commit()
    conn.close()


def load_wages():
    '''
    docstring
    '''
    wages = match_location_names_to_wages_dict()

    insert_wages_sql = '''
        INSERT INTO Wages
        VALUES (NULL, ?, ?, ?, ?, ?, ?)
    '''

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    for area_name, adults_dict in wages.items():
        for number_of_adults, children_dict in adults_dict.items():
            for number_of_children, wages_dict in children_dict.items():
                cur.execute(insert_wages_sql,
                    [
                        area_name,
                        number_of_adults,
                        int(number_of_children.split()[0]), 
                        wages_dict['living wage'],
                        wages_dict['poverty wage'],
                        wages_dict['minimum wage']
                    ]
                )
    conn.commit()
    conn.close()


def load_expenses():
    '''
    docstring
    '''
    expenses = match_location_names_to_expenses_dict()

    insert_expenses_sql = '''
        INSERT INTO Expenses
        VALUES (NULL, ?, ?, ?, ?)
    '''

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    for area_name, adults_dict in expenses.items():
        for number_of_adults, children_dict in adults_dict.items():
            for number_of_children, expenses_dict in children_dict.items():
                cur.execute(insert_expenses_sql,
                    [
                        area_name,
                        number_of_adults,
                        int(number_of_children.split()[0]), 
                        expenses_dict['required annual income before taxes']
                    ]
                )
    conn.commit()
    conn.close()


##############################################
########### interact with database ###########
##############################################
def access_sql_table(area_name, sql_table):
    '''
    Parameters
    ----------
    String
    '''
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    query = f'''
        SELECT *
        FROM {sql_table}
        WHERE {sql_table}.Area = "{area_name}"
        GROUP BY Id
        ORDER BY Id DESC
        '''
    result = cur.execute(query).fetchall()
    conn.close()
    return result


def access_columns(sql_table):
    '''
    docstring
    '''
    conn = sqlite3.connect(DB_NAME)
    cur = conn.execute(f'SELECT * FROM {sql_table}')
    field_names = list(map(lambda x: x[0], cur.description))
    field_names = [description[0] for description in cur.description]
    return field_names


def pretty_print_query(raw_query_result):
    ''' Pretty prints raw query result
    
    Parameters
    ----------
    list 
        a list of tuples that represent raw query result
    
    Returns
    -------
    None
        a python output in the form of a formatted table 
    '''
    ## Resource: http://zetcode.com/python/prettytable/
    pretty_table = PrettyTable()

    pretty_table.field_names = access_columns("Wages")

    pretty_table.header = True
    for row in raw_query_result:
        table = pretty_table.add_row(row)
    
    print(pretty_table)


def avg_living_wage(area_name):
    '''
    Parameters
    ----------
    String
    '''
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    query = f'''
        SELECT AVG([Living Wage])
        FROM Wages
        WHERE Wages.Area = "{area_name}"
        '''
    result = cur.execute(query).fetchone()
    conn.close()
    return result


def extract_one_adult_expenses(area_name):
    '''
    Parameters
    ----------
    String
    '''
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    query = f'''
        SELECT [Number of Adults], [Number of Children], [Required Annual Income Before Taxes]
        FROM Expenses
        WHERE Expenses.Area = "{area_name}"
        '''
    result = cur.execute(query).fetchall()

    one_adult_result = result[0:4]
    clean_one_adult_list = []
    for one_adult_tup in one_adult_result:
        clean_one_adult_list.append(one_adult_tup[-1])
    clean_one_adult_tup = tuple(clean_one_adult_list)

    conn.close()

    return clean_one_adult_tup


def extract_two_adults_one_working_expenses(area_name):
    '''
    Parameters
    ----------
    String
    '''
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    query = f'''
        SELECT [Number of Adults], [Number of Children], [Required Annual Income Before Taxes]
        FROM Expenses
        WHERE Expenses.Area = "{area_name}"
        '''
    result = cur.execute(query).fetchall()

    two_adults_one_working_result = result[4:8]
    clean_two_adults_one_working_list = []
    for two_adults_one_working_tup in two_adults_one_working_result:
        clean_two_adults_one_working_list.append(two_adults_one_working_tup[-1])
    clean_two_adults_one_working_tup = tuple(clean_two_adults_one_working_list)

    conn.close()

    return clean_two_adults_one_working_tup


def extract_two_adults_both_working_expenses(area_name):
    '''
    Parameters
    ----------
    String
    '''
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    query = f'''
        SELECT [Number of Adults], [Number of Children], [Required Annual Income Before Taxes]
        FROM Expenses
        WHERE Expenses.Area = "{area_name}"
        '''
    result = cur.execute(query).fetchall()

    two_adults_both_working_result = result[8:]
    clean_two_adults_both_working_list = []
    for two_adults_both_working_tup in two_adults_both_working_result:
        clean_two_adults_both_working_list.append(two_adults_both_working_tup[-1])
    clean_two_adults_both_working_tup = tuple(clean_two_adults_both_working_list)

    conn.close()

    return(clean_two_adults_both_working_tup)


##############################################
################### plotly ###################
##############################################
def plot_avg_gap(area_name):
    ''' Display the gap between the average living wage of a chosen area
    and the minimum wage of Michigan
    '''
    # wages = access_columns("Wages")[-3:]
    ## ['Living Wage', 'Poverty Wage', 'Minimum Wage']

    # expenses = access_columns("Expenses")[-1]
    ## Required Annual Income Before Taxes

    wage_types = ['Average Living Wage', 'Minimum Wage']

    avg_living_wage_tup = avg_living_wage(area_name)
    avg_living_wage_list = list(avg_living_wage_tup)
    avg_living_wage_in_area = avg_living_wage_list[0]

    wage_values = [round(avg_living_wage_in_area, 2), 9.45]
    gap = round((wage_values[0] - 9.45), 2)

    bar_data = go.Bar(x=wage_types, 
        y=wage_values,
        marker_color='#72B7B2',
        hovertemplate='$%{y:.2f}<extra></extra>', 
        showlegend=False)

    basic_layout = go.Layout(title=f"Average Living Wage in {area_name.title()} vs. State Minimum Wage",
        xaxis_title = "Types of Wages",
        yaxis_title = "US Dollars",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="#7f7f7f"
        ),
        margin_b=125, #increase the bottom margin to have space for caption
        annotations=[dict(xref='paper',
            yref='paper',
            x=0.5,
            y=-0.25,
            showarrow=False,
            font=dict(size=15, color="red"),
            text=f"The gap between the average living wage in {area_name.title()} and state minimum wage is ${format(gap, '.2f')}."
            )]
        )

    fig = go.Figure(data=bar_data, layout=basic_layout)

    return fig.show()


def plot_expenses(area_name):
    ''' Display the expenses in a chosen area
    '''
    # wages = access_columns("Wages")[-3:]
    ## ['Living Wage', 'Poverty Wage', 'Minimum Wage']

    # expenses = access_columns("Expenses")[-1]
    ## Required Annual Income Before Taxes
    family_comp = ['1 Adult, No Child', '1 Adult, 1 Child', '1 Adult, 2 Children', '1 Adult, 3 Children',
                '2 Adult (1 Working), No Child', '2 Adult (1 Working), 1 Child', '2 Adult (1 Working), 2 Children', '2 Adult (1 Working), 3 Children',
                '2 Adult (Both Working), No Child', '2 Adult (Both Working), 1 Child', '2 Adult (Both Working), 2 Children', '2 Adult (Both Working), 3 Children']

    tup_1 = extract_one_adult_expenses(area_name)
    tup_2 = extract_two_adults_one_working_expenses(area_name)
    tup_3 = extract_two_adults_both_working_expenses(area_name)

    expense_values = tup_1 + tup_2 + tup_3

    bar_data = go.Bar(x=family_comp, 
        y=expense_values,
        marker_color='#E45756',
        hovertemplate='<i>Expenses</i>: $%{y:}<extra></extra>', 
        showlegend=False)

    basic_layout = go.Layout(title=f"Required Annual Income Before Taxes in {area_name.title()}",
        xaxis_title = "Family Composition",
        yaxis_title = "US Dollars",
        font=dict(
            family="Courier New, monospace",
            color="#7f7f7f"
            )
        )

    fig = go.Figure(data=bar_data, layout=basic_layout)

    return fig.show()


##############################################
############### cache functions ##############
##############################################
def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    If the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    dict
        The opened cache
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    cache_file = open(CACHE_FILENAME,"w")
    cache_file.write(dumped_json_cache)
    cache_file.close()


def make_request_with_cache(url, cache_dict):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.
    
    Parameters
    ----------
    url: string
        The URL with the data that you want to access
    cache_dict: dict
        A dictionary of param:value pairs
    
    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache JSON
    '''
    if (url in cache_dict.keys()):
        # print(f"CURRENTLY USING CACHE: {url}")
        return cache_dict[url]
    else:
        # print(f"CURRENTLY FETCHING: {url}")
        time.sleep(random.randint(5,10))
        response = requests.get(url)
        cache_dict[url] = response.text
        save_cache(cache_dict)
        return cache_dict[url]


##############################################
########### Executing the program ############
##############################################
if __name__ == "__main__":

    CACHE_DICT = open_cache()

    ## Uncomment these 4 functions when completely done
    create_db()

    load_areas()
    load_wages()
    load_expenses()
    ## Uncomment up to here

    switch = True

    dash_lines = ("-" * 50)

    while True:

########### First search term ###########
        while switch == True:

            search_term_1 = input(f'''
{dash_lines}
*** Welcome! ***
This program uses the MIT Living Wage Calculator to explore the local living wages in the State of Michigan.

*** What is a living wage? ***
The minimum income required for a household to afford adequate shelter, food, and the other basic necessities.

*** And, what is the MIT Living Wage Calculator? ***
Invented by Dr. Amy Glasmeier, it measures the living wage of each household composition in each county or metropolitan statistical area (MSA).

*** Awesome possum! Now what? ***
To begin using the program, type anything and press enter.
To leave the program, type "exit" and press enter.
{dash_lines}
''')

            if search_term_1.lower() != "exit":
                area_list = get_areas_for_state(build_combined_dict())

                print(f"\n{dash_lines}")
                print(f"List of areas in Michigan")
                print(dash_lines)

                counter = 1
                for area in area_list:
                    print(f'[{counter}] {area.info()}')
                    FIPS_AREA_LIST.append(area.info())
                    counter += 1
                switch = False
                break
            
            elif search_term_1.lower() == "exit":
                sys.exit()

########### Second search term ###########
        while switch == False:

            search_term_2 = input(f"""
{dash_lines}
Enter one of the following:
   * a number in the above area list for detail search,
   * "back" to the welcome message, or
   * "exit" to leave the program.
{dash_lines}
""")

            if search_term_2.isnumeric():
                try:
                    search_term_2 = int(search_term_2)

                    if 0 < search_term_2 <= len(FIPS_AREA_LIST):
                        for i in range(len(FIPS_AREA_LIST)):
                            if i == (search_term_2 - 1):

                                area_name = FIPS_AREA_LIST[i].split("(")[0].strip()
                                if ('county') in area_name.lower():
                                    area_name = area_name
                                else:
                                    area_name = area_name + ', MI'

                                print(f"\n{dash_lines}")
                                print(f"Let's get details on wages for {area_name}.")
                                print(dash_lines)
                                lower_case_area_name = f'{area_name.lower()}'
                                pretty_print_query(access_sql_table(lower_case_area_name, 'Wages'))

                                print(f"\n{dash_lines}")
                                follow_up = input(f'Let\'s view some graphs for {area_name}.\nEnter "w" for wages, "e" for expenses, or "exit" to leave.\n{dash_lines}\n')

                                if follow_up.lower() == "w":
                                    plot_avg_gap(lower_case_area_name)
                                elif follow_up.lower() == "e":
                                    plot_expenses(lower_case_area_name)
                                elif follow_up.lower() == "exit":
                                    sys.exit()
                                else:
                                    print(f"\n[Error message]: Oof, can't you follow instructions? Apparently not.")

                    else: ## if the input number is not within an appropriate range
                        print(f"\n[Error message]: Please choose a number within range.")

                except KeyError:
                    print(f"\n[Error message]: Invalid input.")
                    break

            elif search_term_2.lower() == "exit":
                sys.exit()

            elif search_term_2.lower() == "back":
                FIPS_AREA_LIST = [] ## empty the list, or else we will keep appending to this list
                switch = True
                break

            else:
                print(f"\n[Error message]: Invalid input.")
                break
