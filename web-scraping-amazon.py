import requests
from bs4 import BeautifulSoup
import pandas as pd

# Author: Thiago Moura

# This program scraps the amazon.com.br page.
# The 'iphone' is the product you are looking for.
# Some errors in the query were detected (example: search returning
# cell phones from other brands) and errors in standardizing HTML tags
# and CSS selectors were found on the site.

# I put several comments to indicate the line of reasoning and show
# what each line does for teaching purposes.
# Excessive comments are not good practice and should be avoided.

# Create the variable 'uri' to assign the uri Amazon target website.
# with iphone search.
uri = "https://www.amazon.com.br/s?k=iphone"

# Extract the uri data using the BeautifulSoup library and assign the
# content the soup variable
soup = BeautifulSoup((requests.get(uri)).text, 'html.parser')
print(soup)
# The find_all method is triggered to find all divs tags responsible
# for the products on the page.
product_container = soup.find_all('div', class_='sg-col-4-of-24 '
'sg-col-4-of-12 sg-col-4-of-36 s-result-item s-asin sg-col-4-of-28'
'sg-col-4-of-16 sg-col sg-col-4-of-20 sg-col-4-of-32')

# Create a list that will add product names.
names = []

# Scans all elements on the page.
for i in range(len(product_container)):
    # Get the tag that has the content value.
    name = product_container[i].span.find('span', class_='a-size-base-plus'
                                            ' a-color-base a-text-normal')
    # Add the content of the product name to the name list.
    names.append(name.text)

# Create a price list for all products on the first page.
prices = []

# Scans all elements on the page.
for i in range(len(product_container)):
    # get the tag that has the content value.
    price = product_container[i].span.find('span', class_='a-offscreen')
    # Some products on the Amazon website have no prices.
    # So we had to deal with these cases.
    if price == None:
        # Adds "None" for priceless products.
        prices.append(price)
        # Load the product without price, as stated on the Amazon website.
        prices.pop()
    else:
        # Since the tag has the product price, the price variable will
        # store the text content of the tag.
        price = price.text
    # The price of each product is entered in the price list.
    prices.append(price)

# The two-dimensional DataFrame structure of the pandas library is used
# to format the output that will be generated later in Excel with two
# columns: Name and Price.
data_frame = pd.DataFrame({
    # Create the name column
    "Nome": names,
    # Create the price column
    "Preço": prices
})

# Creates an Excel file with extension .xlsx called Amazon.
excel = pd.ExcelWriter('Amazon.xlsx', engine='xlsxwriter')
# Converts the contents of the df variable to excel, edits the
# spreadsheet name to "Results for iPhone" and removes the automatic
# index from the pandas library.
data_frame.to_excel(excel, sheet_name='Results for iPhone', index=False)
# Save the file
excel.save()
