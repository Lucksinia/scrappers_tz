from bs4 import BeautifulSoup as bs
import requests_html
import re
import json

# please be aware that I use black formatter and not autopep8

result_dict = {
    "addres": "",
    "latlon": "",
    "name": "",
    "phones": "",
    "working_hours": "",
}

# coudn't find a way in state menu, so checked all links manually after ... hours
links = [
    "https://som1.ru/shops/133702/",
    "https://som1.ru/shops/131067/",
    "https://som1.ru/shops/64106/",
    "https://som1.ru/shops/64070/",
    "https://som1.ru/shops/136241/",
    "https://som1.ru/shops/256331/",
    "https://som1.ru/shops/539467/",
    "https://som1.ru/shops/120882/",
    "https://som1.ru/shops/64071/",
    "https://som1.ru/shops/151877/",
    "https://som1.ru/shops/151877/",
    "https://som1.ru/shops/64072/",
    "https://som1.ru/shops/64068/",
    "https://som1.ru/shops/64067/",
    "https://som1.ru/shops/408658/",
    "https://som1.ru/shops/64069/",
    "https://som1.ru/shops/278351/",
    "https://som1.ru/shops/146332/",
    "https://som1.ru/shops/354764/",
    "https://som1.ru/shops/398172/",
    "https://som1.ru/shops/454325/",
    "https://som1.ru/shops/311526/",
    "https://som1.ru/shops/431729/",
    "https://som1.ru/shops/507705/",
    "https://som1.ru/shops/614211/",
    "https://som1.ru/shops/552624/",
]


def find_work_hours(soup):
    hours = soup.select_one("table > tbody > tr:nth-child(3) > td:nth-child(3)").text
    time = re.findall("\d+", hours)
    if len(time) == 4:
        string = f"пн-вс {time[0]}:{time[1]} - {time[2]}:{time[3]}"
    if len(time) == 8:
        string_2 = f"пт-сб {time[0]}:{time[1]} - {time[2]}:{time[3]}"
        string_1 = f"вс {time[4]}:{time[5]} - {time[6]}:{time[7]}"
        string = [string_1, string_2]
    return string


def map_parser(soup):
    latlon = soup.select_one("body > script:nth-child(80)").text
    cleared_string = latlon[13:-1]
    latlon = cleared_string[0 : len(cleared_string) // 2 + 5]
    name = cleared_string[len(cleared_string) // 2 + 6 :]
    latlon = latlon[10:]  # finished latlon
    name = name[7:-2]  # finished name
    return latlon, name


def addres_find(soup):
    addres = soup.select_one(
        "table > tbody > tr:nth-child(1) > td:nth-child(3)"
    ).text  # finished addres
    return addres


def phones(soup):
    phonestring = soup.select_one(
        "table > tbody > tr:nth-child(2) > td:nth-child(3)"
    ).text
    s1 = "".join(digit for digit in phonestring if digit.isdecimal())
    phone_1 = soup.find("a", class_="phone-footer")["href"]
    phone_1 = phone_1[4:]  # first phone
    phone_2 = s1[:11]  # second phone
    phone_3 = s1[14:]  # third phone
    phones = [phone_1, phone_2, phone_3]  # result phones
    return phones


def cycle_scrapper(res_dict, list_of_links):
    pages = []
    session = requests_html.HTMLSession()
    for link in list_of_links:
        r_dict = res_dict.copy()
        content = session.get(link)
        content.html.render(sleep=3)
        soup = bs(content.html.raw_html, "lxml")
        r_dict["addres"] = addres_find(soup)
        r_dict["latlon"], r_dict["name"] = map_parser(soup)
        r_dict["phones"] = phones(soup)
        r_dict["working_hours"] = find_work_hours(soup)
        pages.append(r_dict)
    return pages


r_list = cycle_scrapper(result_dict, links)
json_output = json.dumps(r_list, ensure_ascii=False, indent=4)
file = open("output_som.json", "w", errors="ignore")
file.write(json_output)
