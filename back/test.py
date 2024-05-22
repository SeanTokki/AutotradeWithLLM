from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

a = urlopen('https://coinness.com/newsroom')
soup = BeautifulSoup(a.read(), 'html.parser')
print(soup)
c = soup.find_all('div', {'id': 'root'})
print(c)