import requests
import re
from bs4 import BeautifulSoup

USER = ""
PASSWORD = ""

def get_books():
    params = {
        'fn': 'MyZone',
        'Style': 'Portal3',
        'SubStyle': '',
        'Lang': 'GER',
        'ResponseEncoding': 'utf-8'
    }

    session = requests.Session()
    r = session.get('https://bibliothek.hannover-stadt.de/alswww3.dll/APS_ZONES', params=params)
    obj_id = re.search("Obj_[a-zA-Z0-9]+", r.text).group()

    login_params = {
        'Method': 'CheckID',
        'ZonesLogin': 1,
        'Interlock': obj_id,
        'BrowseAsHloc': '',
        'Style': 'Portal3',
        'SubStyle': '',
        'Lang': 'GER',
        'ResponseEncoding': 'utf-8',
        'BRWR': USER,
        'PIN': PASSWORD,
    }
    resp = session.post(f'https://bibliothek.hannover-stadt.de/alswww3.dll/{obj_id}', login_params)
    obj_id = re.search("Obj_[a-zA-Z0-9]+", resp.text).group()

    response = session.get(f'https://bibliothek.hannover-stadt.de/alswww3.dll/{obj_id}?Style=Portal3&SubStyle=&Lang=GER&ResponseEncoding=utf-8?Method=ShowLoans')

    soup = BeautifulSoup(response.content, "html.parser")
    browse_list = soup.find(id="BrowseList").find_all('tr', recursive=False)

    books = []
    for book_raw in browse_list:
        book = {}
        for cell in book_raw.find_all("td", {"class": 'LoanBrowseFieldNameCell'}):
            key = cell.contents[0]
            data = cell.parent.find("td", {"class": 'LoanBrowseFieldDataCell'})
            
            if key == "Titel":
                book['title'] = data.find('a').contents[0].strip()
            elif key == "Verfasser":
                book['author'] = data.contents[0].strip()
            elif key == "Verbuchungsnummer":
                book['id'] = data.contents[0].strip()
            elif key == "ausgeliehen in":
                book['rental_place'] = data.contents[0].strip()
            elif key == "Ausleihdatum":
                book['loan_date'] = data.contents[0].strip()
            elif key == "Rückgabedatum":
                book['return_date'] = data.find('b').contents[0].strip()


        books.append(book)


    return books


if __name__ == '__main__':
    import pprint
    pprint.pprint(get_books())