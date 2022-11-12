# Name: Brandon Watson
# UMID: 76996200
# SOLO
import csv
import os
from bs4 import BeautifulSoup
import re
import unittest


def get_listings_from_search_results(html_file):
    """
    Write a function that creates a BeautifulSoup object on html_file. Parse
    through the object and return a list of tuples containing:
     a string of the title of the listing,
     an int of the cost to rent for one night,
     and a string of the listing id number
    in the format given below. Make sure to turn costs into ints.

    The listing id is found in the url of a listing. For example, for
        https://www.airbnb.com/rooms/1944564
    the listing id is 1944564.
.

    [
        ('Title of Listing 1', 'Cost 1', 'Listing ID 1'),  # format
        ('Loft in Mission District', 210, '1944564'),  # example
    ]
    """
    # Load the file data from the variable html_file into BeautifulSoup.
    with open(html_file,
              'r') as f:
        contents = f.read()
        soup = BeautifulSoup(contents,
                             'html.parser')

        # class_='t1jojoys dir dir-ltr' is the class for the title of the listing.
        divs = soup.find_all('div',
                             class_='t1jojoys dir dir-ltr')
        # Get titles from the divs and eliminate the new line characters or tabs
        # regex to remove new line characters and tabs
        titles = [re.sub(r'[\n\t]', '', div.get_text()) for div in divs]

        # class_='_tyxjp1' is the class for the cost of the listing.
        spans = soup.find_all('span',
                              class_='_tyxjp1')
        # The costs are in the text of the spans.
        costs = [span.text for span in spans]
        # The costs are in the format "$123.00", so we need to remove the "$" and the ".00".
        costs = [int(cost[1:]) for cost in costs]

        metas = soup.find_all('meta')
        urls = []
        for meta in metas:
            if meta.get('content',
                        None) is not None and 'www.airbnb.com/rooms/' in meta.get('content',
                                                                                  None):
                urls.append(meta.get('content',
                                     None))

        # regex to find the listing id
        pattern = r'www.airbnb.com/rooms/[a-z]*\/?([0-9]+)'

        # The listing ids are in the urls.
        ids = []
        for url, id in zip(urls, re.findall(pattern, str(urls))):
            ids.append(id)

        # Consolidate the three lists into a list of tuples.
        listings = list(zip(titles,
                            costs,
                            ids))
        return listings


def get_listing_information(listing_id):
    """
    Write a function to return relevant information in a tuple from an Airbnb listing id.
    NOTE: Use the static files in the html_files folder, do NOT send requests to the actual website.
    Information we're interested in:
        string - Policy number: either a string of the policy number, "Pending", or "Exempt"
            This field can be found in the section about the host.
            Note that this is a text field the lister enters, this could be a policy number, or the word
            "pending" or "exempt" or many others. Look at the raw data, decide how to categorize them into
            the three categories.
        string - Place type: either "Entire Room", "Private Room", or "Shared Room"
            Note that this data field is not explicitly given from this page. Use the
            following to categorize the data into these three fields.
                "Private Room": the listing subtitle has the word "private" in it
                "Shared Room": the listing subtitle has the word "shared" in it
                "Entire Room": the listing subtitle has neither the word "private" nor "shared" in it
        int - Number of bedrooms
.
    (
        policy number,
        place type,
        number of bedrooms
    )
    """

    # Load the file data from the variable html_file into BeautifulSoup.
    with open('html_files/listing_' + listing_id + '.html', encoding='utf-8') as f:

        soup = BeautifulSoup(f, 'html.parser')

        # Find the policy numbers using the class 'f19phm7j dir dir-ltr'
        policy_numbers = soup.find_all('li', class_='f19phm7j dir dir-ltr')

        # Loop through the policy numbers to check if any are pending or exempt
        for policy_number in policy_numbers:
            if 'pending'.casefold() in policy_number.text.casefold():
                policy_number = 'Pending'
            elif 'exempt'.casefold() in policy_number.text.casefold():
                policy_number = 'Exempt'
            else:
                # The policy number is in the format of 'STR-0001541'
                policy_number = policy_number.text.split(' ')[1]

        # Check if the policy number is "Pending" or "Exempt"
        if 'pending'.casefold() in policy_number:
            policy_number = 'Pending'
        elif 'exempt'.casefold() in policy_number:
            policy_number = 'Exempt'

        # Find the place type. Use h2 from class '_14i3z6h' and check if it contains "private" or "shared"
        h2 = soup.find('h2', class_='_14i3z6h').text
        if 'private'.casefold() in h2:
            place_type = 'Private Room'
        elif 'shared'.casefold() in h2:
            place_type = 'Shared Room'
        else:
            place_type = 'Entire Room'

        # Find the number of bedrooms. Use li from class '17n41sf dir dir-ltr' and check if it contains "bedroom"
        li = soup.find_all('li', class_='17n41sf dir dir-ltr')

        # See if any of the li's contain "bedroom" and if so, get the number of bedrooms from the span
        for item in li:
            if 'bedroom'.casefold() in item.text.casefold():
                num_rooms = int(item.find('span').text)
                break
        else:
            num_rooms = 1

        # Return the policy number, place type, and number of bedrooms as a tuple
        return policy_number, place_type, num_rooms


def get_detailed_listing_database(html_file):
    """
    Write a function that calls the above two functions in order to return
    the complete listing information using the functions you’ve created.
    This function takes in a variable representing the location of the search results html file.
    The return value should be in this format:


    [
        (Listing Title 1,Cost 1,Listing ID 1,Policy Number 1,Place Type 1,Number of Bedrooms 1),
        (Listing Title 2,Cost 2,Listing ID 2,Policy Number 2,Place Type 2,Number of Bedrooms 2),
        ...
    ]
    """

    # Get the listings from the html file
    listings = get_listings_from_search_results(html_file)

    # Create a list to hold the listings with the policy number, place type, and number of bedrooms
    listings_with_details = []

    # Loop through the listings and get the policy number, place type, and number of bedrooms
    for listing in listings:
        policy_number, place_type, num_rooms = get_listing_information(listing[2])
        listings_with_details.append((listing[0], listing[1], listing[2], policy_number, place_type, num_rooms))

    return listings_with_details


def write_csv(data, filename):
    """
    Write a function that takes in a list of tuples (called data, i.e. the
    one that is returned by get_detailed_listing_database()), sorts the tuples in
    ascending order by cost, writes the data to a csv file, and saves it
    to the passed filename. The first row of the csv should contain
    "Listing Title", "Cost", "Listing ID", "Policy Number", "Place Type", "Number of Bedrooms",
    respectively as column headers. For each tuple in data, write a new
    row to the csv, placing each element of the tuple in the correct column.

    When you are done your CSV file should look like this:

    Listing Title,Cost,Listing ID,Policy Number,Place Type,Number of Bedrooms
    title1,cost1,id1,policy_number1,place_type1,num_bedrooms1
    title2,cost2,id2,policy_number2,place_type2,num_bedrooms2
    title3,cost3,id3,policy_number3,place_type3,num_bedrooms3
    ...

    In order of least cost to most cost.

    This function should not return anything.
    """

    # Sort the data ascending by cost
    sorted_data = sorted(data, key=lambda x: x[1])

    # Write the data to a csv file
    # Formatted as: Listing Title,Cost,Listing ID,Policy Number,Place Type,Number of Bedrooms
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Listing Title', 'Cost', 'Listing ID', 'Policy Number', 'Place Type', 'Number of Bedrooms'])
        for row in sorted_data:
            writer.writerow(row)


def check_policy_numbers(data):
    """
    Write a function that takes in a list of tuples called data, (i.e. the one that is returned by
    get_detailed_listing_database()), and parses through the policy number of each, validating the
    policy number matches the policy number format. Ignore any pending or exempt listings.
    Return the listing numbers with respective policy numbers that do not match the correct format.
        Policy numbers are a reference to the business license San Francisco requires to operate a
        short-term rental. These come in two forms, where # is a number from [0-9]:
            20##-00####STR
            STR-000####
    .
    Return value should look like this:
    [
        listing id 1,
        listing id 2,
        ...
    ]

    """

    # Create a list to hold the invalid policy numbers
    invalid_policy_numbers = []

    # Loop through the data and check if the policy number is valid
    for listing in data:
        if listing[3] != 'Pending' and listing[3] != 'Exempt':
            if not re.match(r'20\d{2}-00\d{5}STR|STR-000\d{5}', listing[3]):
                invalid_policy_numbers.append(listing[2])

    # Return the invalid policy numbers
    return invalid_policy_numbers


def extra_credit(listing_id):
    """
    There are few exceptions to the requirement of listers obtaining licenses
    before listing their property for short term leases. One specific exception
    is if the lister rents the room for less than 90 days of a year.

    Write a function that takes in a listing id, scrapes the 'reviews' page
    of the listing id for the months and years of each review (you can find two examples
    in the html_files folder), and counts the number of reviews the apartment had each year.
    If for any year, the number of reviews is greater than 90 (assuming very generously that
    every reviewer only stayed for one day), return False, indicating the lister has
    gone over their 90 day limit, else return True, indicating the lister has
    never gone over their limit.
    """
    pass


class TestCases(unittest.TestCase):

    def test_get_listings_from_search_results(self):
        # call get_listings_from_search_results("html_files/mission_district_search_results.html")
        # and save to a local variable
        listings = get_listings_from_search_results("html_files/mission_district_search_results.html")
        # check that the number of listings extracted is correct (20 listings)
        self.assertEqual(len(listings),
                         20)
        # check that the variable you saved after calling the function is a list
        self.assertEqual(type(listings),
                         list)
        # check that each item in the list is a tuple

        # check that the first title, cost, and listing id tuple is correct (open the search results html and find it)

        # check that the last title is correct (open the search results html and find it)
        # pass

    def test_get_listing_information(self):
        html_list = ["1623609",
                     "1944564",
                     "1550913",
                     "4616596",
                     "6600081"]
        # call get_listing_information for i in html_list:
        listing_informations = [get_listing_information(id) for id in html_list]
        # check that the number of listing information is correct (5)
        self.assertEqual(len(listing_informations),
                         5)
        for listing_information in listing_informations:
            # check that each item in the list is a tuple
            self.assertEqual(type(listing_information),
                             tuple)
            # check that each tuple has 3 elements
            self.assertEqual(len(listing_information),
                             3)
            # check that the first two elements in the tuple are string
            self.assertEqual(type(listing_information[0]),
                             str)
            self.assertEqual(type(listing_information[1]),
                             str)
            # check that the third element in the tuple is an int
            self.assertEqual(type(listing_information[2]),
                             int)
        # check that the first listing in the html_list has policy number 'STR-0001541'

        # check that the last listing in the html_list is a "Private Room"

        # check that the third listing has one bedroom

        pass

    def test_get_detailed_listing_database(self):
        # call get_detailed_listing_database on "html_files/mission_district_search_results.html"
        # and save it to a variable
        detailed_database = get_detailed_listing_database("html_files/mission_district_search_results.html")
        # check that we have the right number of listings (20)
        self.assertEqual(len(detailed_database),
                         20)
        for item in detailed_database:
            # assert each item in the list of listings is a tuple
            self.assertEqual(type(item),
                             tuple)
            # check that each tuple has a length of 6
            self.assertEqual(len(item), 6)

        # check that the first tuple is made up of the following:
        # 'Loft in Mission District', 210, '1944564', '2022-004088STR', 'Entire Room', 1
        self.assertEqual(detailed_database[0],
                         ('Loft in Mission District', 210, '1944564', '2022-004088STR', 'Entire Room', 1))

        # check that the last tuple is made up of the following:
        # 'Private Room in Mission District', 65, '6600081', 'STR-0001541', 'Private Room', 1
        self.assertEqual(detailed_database[-1],
                         ('Private Room in Mission District', 65, '6600081', 'STR-0001541', 'Private Room', 1))

    def test_write_csv(self):
        # call get_detailed_listing_database on "html_files/mission_district_search_results.html"
        # and save the result to a variable
        detailed_database = get_detailed_listing_database("html_files/mission_district_search_results.html")
        # call write csv on the variable you saved
        write_csv(detailed_database,
                  "test.csv")
        # read in the csv that you wrote
        csv_lines = []
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               'test.csv'),
                  'r') as f:
            csv_reader = csv.reader(f)
            for i in csv_reader:
                csv_lines.append(i)
        # check that there are 21 lines in the csv
        self.assertEqual(len(csv_lines),
                         21)
        # check that the header row is correct\
        self.assertEqual(csv_lines[0], ['Title', 'Cost', 'Listing ID', 'Policy Number', 'Room Type', 'Bedrooms'])
        # check that the next row is correct
        self.assertEqual(csv_lines[1], ['Loft in Mission District', '210', '1944564', '2022-004088STR', 'Entire Room', '1'])
        # check that the last row is correct
        self.assertEqual(csv_lines[-1], ['Private Room in Mission District', '65', '6600081', 'STR-0001541', 'Private Room', '1'])

    def test_check_policy_numbers(self):
        # call get_detailed_listing_database on "html_files/mission_district_search_results.html"
        # and save the result to a variable
        detailed_database = get_detailed_listing_database("html_files/mission_district_search_results.html")
        # call check_policy_numbers on the variable created above and save the result as a variable
        invalid_listings = check_policy_numbers(detailed_database)
        # check that the return value is a list
        self.assertEqual(type(invalid_listings),
                         list)
        # check that there is exactly one element in the string

        # check that the element in the list is a string

        # check that the first element in the list is '16204265'
        pass


if __name__ == '__main__':
    database = get_detailed_listing_database("html_files/mission_district_search_results.html")
    write_csv(database,
              "airbnb_dataset.csv")
    check_policy_numbers(database)
    unittest.main(verbosity=2)
