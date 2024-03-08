import sqlite3
import requests
from bs4 import BeautifulSoup

def create_database():

    # Connect to the SQLite database
    conn = sqlite3.connect('as_database.sqlite')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS airports')

    # Create table
    c.execute('''CREATE TABLE airports
                 (id INTEGER PRIMARY KEY,
                  Name TEXT,
                  IATA TEXT,
                  ICAO TEXT,
                  Country TEXT,
                  Continent TEXT,
                  Passengers INTEGER,
                  Cargo INTEGER,
                  Altitude INTEGER,
                  Latitude REAL,
                  Longitude REAL)''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

def add_airport(airports):
    conn = sqlite3.connect('as_database.sqlite')
    c = conn.cursor()
    for item in airports:
        c.execute('''INSERT INTO airports (Name, IATA, ICAO, Country, Continent, Passengers, Cargo, Altitude, Latitude, Longitude) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ? ,?, ?)''',
                          (item['Name'], item['IATA'], item['ICAO'], item['Country'], item['Continent'], item['Passengers'], item['Cargo'], item['altitude'], item['latitude'], item['longitude']))
    conn.commit()
    conn.close()


def scrape_airports():
    airports = []
    for i in range(1, 10):
        url = "https://hindenburg.airlinesim.aero/app/info/airports/" + str(i)
        print(url)
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            airport = {}



            try:
                airport_name = soup.find("h1").text
                start_index = airport_name.index(": ") + len(": ")
                end_index = airport_name.index(" (")
                airport["Name"] = airport_name[start_index:end_index]
            except:
                airport["Name"] = "Not found"
                airport["IATA"] = "Not found"
                airport["ICAO"] = "Not found"
                airport["Country"] = "Not found"
                airport["Continent"] = "Not found"
                airport["Passengers"] = 0
                airport["Cargo"] = 0
                airport["altitude"] = 0
                airport["latitude"] = 1.0
                airport["longitude"] = 1.0
                airports.append(airport)

                continue

            table = soup.find("table", class_="table table-hover")
            tbody_elements = table.find_all('tbody')

            for tbody in tbody_elements:

                for row in tbody.find_all('tr'):
                    cells = row.find_all('td')
                    if cells[0].text == "IATA code":
                        airport["IATA"] = cells[1].text
                    elif cells[0].text == "ICAO code":
                        airport["ICAO"] = cells[1].text
                    elif cells[0].text == "Country":
                        airport["Country"] = cells[1].text
                    elif cells[0].text == "Continent":
                        airport["Continent"] = cells[1].text
                    elif cells[0].text == "Passengers":
                        demand_passenger = cells[1].img["title"]
                        start_index = demand_passenger.index(": ") + len(": ")
                        airport["Passengers"] = int(demand_passenger[start_index:])
                    elif cells[0].text == "Cargo":
                        demand_cargo = cells[1].img["title"]
                        start_index = demand_cargo.index(": ") + len(": ")
                        airport["Cargo"] = int(demand_cargo[start_index:])

            if "ICAO" not in airport:
                airport["ICAO"] = "Not found"

            airport["altitude"] = 0
            airport["latitude"] = 1.0
            airport["longitude"] = 1.0


            print(airport)

            airports.append(airport)

        else:
            print("Failed to retrieve page")

    return airports


def search_for_data():

    conn = sqlite3.connect('as_database.sqlite')
    c = conn.cursor()

    c.execute('SELECT * FROM airports')
    result_as = []
    rows = c.fetchall()
    for row in rows:
        # Create a dictionary with column names as keys and row values as values
        row_dict = {
            'id': row[0],
            'Name': row[1],
            'IATA': row[2],
            'ICAO': row[3],
            'Country': row[4],
            'Continent': row[5],
            'Passengers': row[6],
            'Cargo': row[7]

        }
        # Append the dictionary to the result list
        result_as.append(row_dict)
    print(result_as)

    conn.close()
    conn = sqlite3.connect('airports.sqlite')
    c = conn.cursor()

    c.execute('SELECT * FROM airports')
    result_airports = []
    rows = c.fetchall()
    for row in rows:
        # Create a dictionary with column names as keys and row values as values
        row_dict = {
            'id': row[0],
            'Name': row[1],
            'City': row[2],
            'Country': row[3],
            'IATA': row[4],
            'ICAO': row[5],
            'latitude': row[6],
            'longitude': row[7],
            'altitude': row[8],
            'timezone': row[9],
            'DST': row[10],

        }
        # Append the dictionary to the result list
        result_airports.append(row_dict)

    print(result_airports)
    conn.close()

    for airport in result_as:
        iata = airport['IATA']
        for airport_info in result_airports:
            if airport_info['IATA'] == iata:
                airport['longitude'] = airport_info['longitude']
                airport['latitude'] = airport_info['latitude']
                airport['altitude'] = airport_info['altitude']
                break

    return result_as




if __name__ == '__main__':
    create_database()
    example_airports = scrape_airports()
    add_airport(example_airports)
    result_as = search_for_data()
    create_database()
    add_airport(result_as)