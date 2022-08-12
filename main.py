from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import requests
import datetime

def main():

    with open("company_names.txt", "r") as f:
        company_list = f.read()
    company_list = company_list.split("\n")
    company_list = [x.strip() for x in company_list]

    company_names = pd.DataFrame(columns=["NameToFind", "del1", "del2", "FundooLinks", "Name", "Industry", "Address", "Ph No", "Website"])
    company_names['NameToFind'] = company_list

    for ind in tqdm(company_names.index):
        search_link = "https://www.google.com/search?q="+company_names["NameToFind"][ind]+" fundoodata"
        source = requests.get(search_link).text
        soup = BeautifulSoup(source, 'html.parser')
        fundoo_link = soup.find_all('div', class_='kCrYT')
        if(fundoo_link):
            for link in fundoo_link[:3]:
                if(link.a):
                    if("fundoodata" in link.a['href']):
                        company_link = link.a["href"].replace("/url?q=", "")
                        company_link = company_link[:(company_link.find(".html")+5)]
                        company_names["FundooLinks"][ind]= company_link
                        if ("fundoodata" in company_link):
                            details = requests.get(company_link).text
                            soup1 = BeautifulSoup(details, 'lxml')
                            if(soup1.find('div', class_="search-page-heading-red")):
                                company_names["Name"][ind] = " ".join(soup1.find('div', class_="search-page-heading-red").text.split())
                                if(soup1.find('div', class_="detail-line")):
                                    temp3 = soup1.find('div', class_="detail-line")
                                    if(temp3.a.text):
                                        company_names['Website'][ind] = temp3.a.text
                                    hola = temp3.text.split()
                                    if (temp3.a.text in hola):
                                        hola.remove(temp3.a.text)
                                    phno = " ".join(hola)
                                    company_names["Ph No"][ind] = phno
                                    tempo = soup1.find('div', class_="search-page-right-pannel")
                                    if(tempo is not None):
                                        a = tempo.text.split()
                                        try: 
                                            address = " ".join(a[(a.index('Address')+2):a.index(phno.split()[0])])
                                            company_names["Address"][ind] = address
                                        except IndexError:
                                            pass
                                industrysoup = soup1.find('div', class_="overview-box2")
                                if(industrysoup is not None):
                                    industry = industrysoup.text.replace("\nIndustry\n", "")
                                    company_names["Industry"][ind] = industry
                        break
    company_names.drop(columns=['del1', 'del2'], inplace=True)
    company_names.to_csv('output/output'+datetime.datetime.now().strftime('%Y%m%d%H%M%S')+'.csv', index=False)

main()