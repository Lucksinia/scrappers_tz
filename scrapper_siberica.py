from bs4 import BeautifulSoup
import requests_html
import re
import json
import time

# please be aware that I use black formatter and not autopep8

url = "https://www.naturasiberica.ru/our-shops/natura-siberica-moskva-trts-metropolis/"
session = requests_html.HTMLSession()
content = session.get(url)
content.html.render(sleep=2)
soup = BeautifulSoup(content.html.raw_html, "lxml")
place = soup.find("div", class_="original-shops__info")
result_dict = {
    "addres": "",
    "latlon": "",
    "name": "Natura Siberica",
    "phones": "",
    "working_hours": "",
}

# coudn't find path to other bosnia place. it links to
# the /our-shops/, so maybe, it doesen't exsist?
def link_seeker(soup):
    nec_ul = soup.find("ul", class_="card-list")
    li_list = nec_ul.find_all("li", class_="card-list__item")
    link_list = []
    for li in li_list:
        if li.a["href"] == "/our-shops/":  # Specifically for that one bosnia...
            continue
        link_list.append(li.a["href"])
    return link_list


def cycle_scrapper(soup, res_dict):
    pages = []
    session = requests_html.HTMLSession()
    list_of_links = link_seeker(soup)
    for link in list_of_links:
        r_dict = res_dict.copy()
        url = f"https://www.naturasiberica.ru{link}"
        time.sleep(1)  # hack so that origin host dont boot me out.
        content = session.get(url)
        content.html.render(sleep=3)  # four is too much, booted.
        soup = BeautifulSoup(content.html.raw_html, "lxml")
        place = soup.find("div", class_="original-shops__info")
        r_dict["addres"] = str(place.find("p", class_="original-shops__address").text)
        # r_dict["latlon"] = parse_maps(soup) #TODO: not yet
        r_dict["phones"] = phone(place)
        r_dict["working_hours"] = work_hours_find(place)
        pages.append(r_dict)
    return pages


def phone(place):
    phone_string = place.find("p", class_="original-shops__phone").text
    cleared_string = re.findall("\d+", phone_string)
    full_number = "".join([str(el) for el in cleared_string])
    return full_number


def work_hours_find(place):
    string = "пн-вс 10:00 - 22:00"
    hours = place.find(
        "div", class_="shop-schedule original-shops__schedule", id="schedule1782"
    ).text
    if (
        hours == "Мы будем рады видеть Вас "
    ):  # apperently, [] is of type:Any and not None. So this is a hack
        string = [f"пн-вс 10:00 - 22:00"]
        return string
    stripped = re.findall("\d+", hours)
    if len(stripped) == 4:
        string = [f"пн-вс {stripped[0]}:{stripped[1]} - {stripped[2]}:{stripped[3]}"]
    elif len(stripped) == 2:
        string = [f"пн-вс {stripped[0]}:00 - {stripped[1]}:00"]
    elif stripped[2] == "18":
        string = [f"пн-пт {stripped[0]}:{stripped[1]} - {stripped[2]}:{stripped[3]}"]
    elif stripped[2] == "23" and len(stripped) > 4:
        string_1 = f"вс-чт {stripped[0]}:{stripped[1]} - {stripped[2]}:{stripped[3]}"
        string_2 = f"пт-сб {stripped[0]}:{stripped[1]} - {stripped[6]}:{stripped[7]}"
        string = [string_1, string_2]
    elif stripped[2] == "22" and len(stripped) > 4:
        string_1 = f"вс-чт {stripped[0]}:{stripped[1]} - {stripped[2]}:{stripped[3]}"
        string_2 = f"пт-сб {stripped[0]}:{stripped[1]} - {stripped[6]}:{stripped[7]}"
        string = [string_1, string_2]
    elif len(stripped) == 9:
        string = [f"пн-вс {stripped[0]}:{stripped[1]} - {stripped[2]}:{stripped[3]}"]
    return string


r_list = cycle_scrapper(soup, result_dict)
json_output = json.dumps(r_list, ensure_ascii=False, indent=4)
file = open("output_naturasiberica.json", "w", errors="ignore")
file.write(json_output)
