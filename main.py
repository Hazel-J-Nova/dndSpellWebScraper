
from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv
import re
from pathlib import Path

load_dotenv()
env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("API_KEY")


base_url = "http://dnd5e.wikidot.com"
API_URL = "https://spellforgeapi.online/"

schools = {"Abjuration": True, "Alteration": True, "Conjuration": True, "Divination": True,
           "Enchantment": True, "Illusion": True, "Invocation": True,  "Necromancy": True}

damage_type = {
    "slashing": True,
    "piercing": True,
    "bludgeoning": True,
    "poison": True,
    "acid": True,
    "fire": True,
    "cold": True,
    "radiant": True,
    "necrotic": True,
    "lightning": True,
    "thunder": True,
    "force": True,
    "psychic": True,
}


def get_soup(url):
    html_soup = requests.get(url)
    soup = BeautifulSoup(html_soup.text, 'html.parser')
    return soup


def get_spell(soup):
    spell_list = soup.find_all("a", href=re.compile("^/spell:"))
    return [el.get("href") for el in spell_list]


def split_text(spell_list, spell_link):
    spell_save_or_attack = ""
    spell_damage_type = ""
    spell_text = spell_list.find_all('p')
    spell_text = [str(el) for el in spell_text]
    spell_text = " ".join(spell_text)
    spell_text = "".join(spell_text).split("\n")
    spell_text = "".join(spell_text).split("<p>")
    spell_text = [el.replace("<strong>", "").replace("<p>", "").replace(
        "</p>", "").replace("</strong>", "").replace("</br>", "").replace("<em>", "").replace("</em>", "") for el in spell_text]
    del spell_text[0]
    if not "Spell Lists" in spell_text[-1] and not "Spell list" in spell_text[-1]:
        spell_text.pop(-1)
    class_list = re.sub('<.*?>', '', spell_text[-1])
    spell_text.pop(-1)
    castingTime_range_components_duration = spell_text[2].split("<br/>")
    spell_text.pop(2)
    spell_description = "".join(spell_text[2:])
    spell_text = spell_text[:2]
    level_school_subschool = spell_text[1].split(" ")
    spell_source = spell_text[0]
    name = spell_link.replace("/spell:", "").replace("-", " ")
    for [index, el] in enumerate(spell_description):
        if(re.search("^\s*\d+.+?\d+\s*$", el)):
            if index + 1 < len(spell_description) and spell_description[index+1] in damage_type:
                spell_damage_type = spell_description[index+1]
        if el == 'saving':
            spell_save_or_attack = spell_description[index-1]
    return (spell_source, class_list, castingTime_range_components_duration, spell_description, level_school_subschool, name, spell_save_or_attack, spell_damage_type)


def create_spell_object(spell_source, class_list, castingTime_range_components_duration, spell_description, level_school_subschool, name, spell_save_or_attack, spell_damage_type):
    if level_school_subschool[0] in schools:
        level = "Cantrip"
        school = level_school_subschool[0]
    else:
        level = level_school_subschool[0]
        school = level_school_subschool[1]

    spell_object = {
        "name": name,
        "Character_Class": class_list,
        "spell_level": level,
        "spell_source": spell_source,
        "spell_school": school,
        "casting_time": castingTime_range_components_duration[0],
        "duration": castingTime_range_components_duration[3],
        "range_or_area": castingTime_range_components_duration[1],
        "Spell_Component": castingTime_range_components_duration[2],
        "description": spell_description,
        "spell_save_or_attack": spell_save_or_attack,
        "spell_damage_type": spell_damage_type,
    }
    return spell_object


test = get_soup("http://dnd5e.wikidot.com/spells")

spell_list = get_spell(test)
for spell in spell_list:
    spell_text = get_soup(f"{base_url}{spell}")
    formated_spell = split_text(spell_text, spell)
    spell_object = (create_spell_object(*formated_spell))
    r = requests.post(f"{API_URL}spells/?key={ API_KEY}", json=spell_object)
    print(r)
spell_text = get_soup(f"{base_url}{spell_list[50]}")
formated_spell = split_text(spell_text, spell_list[50])
spell_object = (create_spell_object(*formated_spell))
print(spell_object)
payload = {"key": API_KEY}

r = requests.post(f"{API_URL}spells/", json=spell_object, params=payload)
print(r)
