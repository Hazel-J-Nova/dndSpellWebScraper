from bs4 import BeautifulSoup
import requests


base_url = "http://dnd5e.wikidot.com"
API_URL = "http://127.0.0.1:8000/"


def get_soup(url):
    html_soup = requests.get(url)
    soup = BeautifulSoup(html_soup.text, 'html.parser')
    return soup


def get_spell(soup):
    spell_list = soup.find_all("a", href=re.compile("^/spell:"))
    return [el.get("href") for el in spell_list]


def split_text(spell_list, spell_link):
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
    return (spell_source, class_list, castingTime_range_components_duration, spell_description, level_school_subschool, name)


def create_spell_object(spell_source, class_list, castingTime_range_components_duration, spell_description, level_school_subschool, name):

    spell_object = {
        "name": name,
        # "source": spell_source.replace("Source", ""),
        "spell_level": level_school_subschool[0],
        # "school": level_school_subschool[1],
        "description": spell_description,
        # "spell_class_list": class_list,
        "casting_time": castingTime_range_components_duration[0],
        "range_or_area": castingTime_range_components_duration[1],
        # "components": castingTime_range_components_duration[2],
        "duration": castingTime_range_components_duration[3]
    }
    return spell_object


# test = get_soup("http://dnd5e.wikidot.com/spells")

# spell_list = get_spell(test)
# for spell in spell_list:
#     spell_text = get_soup(f"{base_url}{spell}")
#     formated_spell = split_text(spell_text, spell)
#     spell_object = (create_spell_object(*formated_spell))
#     r = requests.post(f"{API_URL}spells/", json=spell_object)
#     print(r)
