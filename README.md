# Betsy Webshop
Betsy is a fictional web marketplace where people can sell homemade goods. This project tests skills in modeling data as well as using the peewee ORM.

## Requirements

Python 3 peewee Whoosh Installation

Clone the repository: git clone https://github.com/jomeesters/webshop.git Change directory to the project folder: cd betsy-webshop Create and activate a virtual environment: python3 -m venv venv and source venv/bin/activate (Mac)

Usage

To start the program, run python3 main.py from the command line. The program will prompt you to choose from a list of options.

Betsy Webshop Menu
1. Search for products
2. List user products
3. List products per tag
4. Add product to catalog
5. Update stock
6. Purchase product
7. Remove product
8. Exit

Testing

To run the tests, run python3 test_betsy.py from the command line. Note that the tests will use and modify the existing betsy.db database. Make sure to backup your data before running the tests.

Search Functionality

The Betsy webshop has a search function that allows users to search for products based on a keyword or phrase. The search functionality targets both the name and description fields of the products and is case-insensitive. The products are indexed, which minimizes the time spent on querying them. 
