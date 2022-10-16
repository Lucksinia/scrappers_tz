from bs4 import BeautifulSoup
import requests
import re
import json

# please be aware that I use black formatter and not autopep8


def link_seeker(soup):
    """
    Links to other parts of the site-parser
    """
    nec_ul = soup.find("ul", class_="c-list c-accordion")
    internal_uls = nec_ul.find_all("ul", class_="sub-menu")
    list_ = []
    for ul in internal_uls:
        l = ul.find_all("li")
        l = [
            el.a["href"] for el in l
        ]  # allowing to peak "inside" nested ul tags more than on one li tag
        list_ += l
    return list_


def phones_list(place, soup):
    """
    Phones parser
    """
    phones = []
    phones.append(
        place.find("strong", text="Teléfono:").find_next("span").text
    )  # first phone
    phones.append(
        soup.find("h5", text="Call Center").find_next("a").text
    )  # second phone
    phones.append(
        soup.find("h5", text="Teléfono").find_next("a").text.replace(" ", "")
    )  # third phone, coud use strip, i think. but not shure, so...
    return phones


def work_hours_find(soup):
    place = soup
    am = (
        place.find("strong", text="Horarios:").find_next("span").text
    )  # First half of the day
    pm = (
        place.find("strong", text="Horarios:").find_next("span").find_next("span").text
    )  # Second half of the day
    first_nums = re.findall("\d+", am)  # Numbers of the first half of the day-time
    last_nums = re.findall("\d+", pm)  # just returns list of numbers
    if len(last_nums) == 4:
        str_1 = (
            f"mon-thu {first_nums[0]}:{first_nums[1]} - {first_nums[2]}:{first_nums[3]}"
        )
        str_2 = f"fri {first_nums[0]}:{first_nums[1]} - {first_nums[2]}:{first_nums[3]}"
    else:
        str_1 = f"mon-thu {first_nums[0]}:{first_nums[1]} - {first_nums[2]}:{first_nums[3]} {last_nums[0]}:{last_nums[1]} - {last_nums[2]}:{last_nums[3]}"
        str_2 = f"fri {first_nums[0]}:{first_nums[1]} - {first_nums[2]}:{first_nums[3]} {last_nums[0]}:{last_nums[1]} - {last_nums[4]}:{last_nums[5]}"
    working_hours = [str_1, str_2]  # time of work
    return working_hours


def parse_maps(soup):
    """
    Embeded map parser - that i spend a 5 hours befor found out, that i parsed wrong iframe
    """
    iframes = soup.find_all("iframe")
    src = iframes[1]["src"]
    resp = requests.get(src).content
    map_soup = BeautifulSoup(resp, "lxml")
    _script = map_soup.find("script")
    match = re.findall(
        "(-\d+\.\d{7})", _script.text
    )  # regex thats finds -+digits.sevendigitsafter.
    latlon = match[0:2]  # don't need repeated value
    return latlon


def cycle_scrapper(soup, res_dict):
    pages = []
    list_of_links = link_seeker(soup)
    for link in list_of_links:
        r_dict = res_dict.copy()
        url = f"https://www.oriencoop.cl{link}"
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "lxml")
        place = soup.find("div", class_="s-dato")
        r_dict["addres"] = place.span.text
        r_dict["latlon"] = parse_maps(soup)
        r_dict["phones"] = phones_list(place, soup)
        r_dict["working_hours"] = work_hours_find(soup)
        pages.append(r_dict)
    return pages


url = "https://www.oriencoop.cl/sucursales.htm"
content = requests.get(url)
soup = BeautifulSoup(content.text, "lxml")
result_dict = {
    "addres": "",
    "latlon": "",
    "name": "Orientcoop",  # Or is this about name of the place where it stands?
    "phones": "",
    "working_hours": "",
}

r_list = cycle_scrapper(soup, result_dict)
json_output = json.dumps(r_list, indent=4)
file = open("output_chili.json", "w")
file.write(json_output)
