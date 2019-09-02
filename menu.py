# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urllib import request, parse
import requests
import json, datetime, re
from slack import WebClient

slack_client = WebClient("xoxb-2525381780-596877194132-JC5Q8zTiD6DCXqSmVfQq2l33")

def sodexo(id, restaurant_number):

    date = datetime.datetime.now()
    day = date.day

    if day < 10:
        str_day = "0" + str(day)
    else:
        str_day = str(day)

    month = date.month

    if month < 10:
        str_month = "0" + str(month)
    else:
        str_month = str(month)

    str_year = str(date.year)

    sodexo_url = "http://www.sodexo.fi/ruokalistat/output/daily_json/%s/%s/%s/%s/fi" % (id, str_year, str_month, str_day)
    data = requests.get(url=sodexo_url)

    json_data = data.json()
    payload = "```Sodexo Hermia " + str(restaurant_number) + " menu \n=================================================\n\n"

    for course in json_data["courses"]:
        if course.get("category") != None:
          category = course["category"]
        else:
          category = "Sodexo fucking sucks keeping the JSON intact"
        if course.get("price") != None:
          price = course["price"]
        else:
          price = ""
        if course.get("title_en") != None:
          title_en = course["title_en"]
        else:
          title_en = ""
        row = category + ": " + "\t" + price + "\n" + course["title_fi"] + "\n" + title_en + "\n\n"
        checkFavorites(row, lines, "Sodexo Hermia " + str(restaurant_number))
        payload = payload + row

    payload = payload + "```"

    payload_re = re.sub('[^a-zA-ZäöÄÖ -:\n`]*$', "", payload)
    payload_re = payload_re.replace("&", "and")
    payload_re = '{"text": "' + payload_re + '"}'

    #print(payload_re)
    req = request.Request("https://hooks.slack.com/services/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", headers={"Content-Type":"application/x-www-form-urlencoded"}, data=payload_re.encode('utf-8'))

    # OMA
    #req = request.Request("https://hooks.slack.com/services/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", headers={"Content-Type":"application/x-www-form-urlencoded"}, data=payload_re.encode('utf-8'))

    response = request.urlopen(req)

def farmi():

    day = datetime.datetime.now().strftime("%A")

    day_number = datetime.datetime.now().day
    month_number = datetime.datetime.now().month

    weekdays = {"Monday":"Maanantai", "Tuesday":"Tiistai", "Wednesday":"Keskiviikko", "Thursday":"Torstai", "Friday":"Perjantai"}

    now = weekdays.get(day)

    farmi_url = "https://www.antell.fi/hermian-farmi#lounas"
    html = requests.get(url=farmi_url)
    parsed_html = BeautifulSoup(html.text, "html5lib")

    fi_header = parsed_html.find("h3", text=now + " " + str(day_number) + "." + str(month_number) + ".")
    en_header = parsed_html.find("h3", text=day + " " + str(day_number) + "." + str(month_number) + ".")

    payload = "```Farmi menu \n=================================================\n\n"

    #for li in fi_header.next_sibling.next_sibling.find_all('li'):
     #   if li.has_attr('class'):
      #      for strong_rows in li.find_all('strong'):
       #         row = " ".join(strong_rows.string.split()).upper()  + "\t"
        #        payload = payload + row
         #   payload = payload + "\n"
        #else:
         #   row = str(" ".join(li.text.split()))
          #  payload = payload + row
           # payload = payload + "\n"
        #payload = payload + "\n"
    fi_siblings = fi_header.next_sibling.next_sibling.find_all('li')
    en_siblings = en_header.next_sibling.next_sibling.find_all('li')

    for x in range(len(fi_siblings)):
        if fi_siblings[x].has_attr('class') and en_siblings[x].has_attr('class'):
                for fi_strong_row in fi_siblings[x].find_all('strong'):
                    row = " ".join(fi_strong_row.string.split()).upper() + "\t"
                    payload = payload + row
        else:
            row = str(" ".join(fi_siblings[x].text.split()))
            payload = payload + row
            payload = payload + "\n"
            row = str(" ".join(en_siblings[x].text.split()))
            row = row.replace('&', "and")
            payload = payload + row
            payload = payload + "\n"
        payload = payload + "\n"

    payload = payload + "```"
    payload = '{"text": "' + payload + '"}'

    req = request.Request("https://hooks.slack.com/services/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", headers={"Content-Type":"application/x-www-form-urlencoded"}, data=payload.encode('utf-8'))

    # OMA
    #req = request.Request("https://hooks.slack.com/services/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", headers={"Content-Type":"application/x-www-form-urlencoded"}, data=payload.encode('utf-8'))

    response = request.urlopen(req)

def checkFavorites(menu_row, lines, restaurant):
    for line in lines:
        splitted_line = line.split(":")
        user = splitted_line[0]
        favorites_list = splitted_line[1]
        for favorite_item in favorites_list.split(","):
            if favorite_item.lower().rstrip() in menu_row.lower():
                print("notify")
                notify_favorite(user, favorite_item.rstrip(), menu_row, restaurant)

def notify_favorite(user, favorite_item, menu_row, restaurant):
    slack_client.rtm_connect(with_team_state=False)
    response = "Hi! Your favorite item *{}* is now on menu at *{}* \n" \
               "{}\n\n".format(favorite_item, restaurant, menu_row)
    slack_client.api_call(
        "chat.postMessage",
        channel=user,
        text=response
    )

def load_favorites():
    path = "favorites.txt"
    favorites_file = open(path, 'r')
    lines = favorites_file.readlines()
    favorites_file.close()
    return lines

lines = load_favorites()

# Sodexo 6
sodexo(9870, 6)

# Sodexo 5
sodexo(134, 5)

# Farmi
farmi()