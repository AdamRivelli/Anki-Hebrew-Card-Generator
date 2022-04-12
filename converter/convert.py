from bs4 import BeautifulSoup as bs
import requests
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import sys

templates_dir = Path(__file__).parent.parent / "templates"
templates_dir = templates_dir.absolute()

env = Environment(loader=FileSystemLoader(templates_dir))
template = env.get_template('verb_he_en.html')

pealim_to_jinja = {
    "AP-ms": "p_x_s_m",
    "AP-fs": "p_x_s_f",
    "AP-mp": "p_x_p_m",
    "AP-fp": "p_x_p_f",
    "PERF-1s": "pp_1_s_x",
    "PERF-1p": "pp_1_p_x",
    "PERF-2ms": "pp_2_s_m",
    "PERF-2fs": "pp_2_s_f",
    "PERF-2mp": "pp_2_p_m",
    "PERF-2fp": "pp_2_p_f",
    "PERF-3ms": "pp_3_s_m",
    "PERF-3fs": "pp_3_s_f",
    "PERF-3p": "pp_2_p_x",
    "IMPF-1s": "f_1_s_x",
    "IMPF-1p": "f_1_p_x",
    "IMPF-2ms": "f_2_s_m",
    "IMPF-2fs": "f_2_s_f",
    "IMPF-2mp": "f_2_p_m",
    "IMPF-2fp": "f_2_p_f",
    "IMPF-3ms": "f_3_s_m",
    "IMPF-3fs": "f_3_s_f",
    "IMPF-3mp": "f_3_p_m",
    "IMPF-3fp": "f_3_p_f",
    "IMP-2ms": "im_2_s_m",
    "IMP-2fs": "im_2_s_f",
    "IMP-2mp": "im_2_p_m",
    "IMP-2fp": "im_2_p_f",
    "INF-L": "inf"
}

def print_shoresh(shoresh: str):
    if not shoresh:
        return
    shoresh = shoresh.replace("-", "־")
    shoresh = "".join(shoresh.split())
    print(shoresh)


def convert_verb(soup):
    out_dict = {}

    shoresh = soup.find("span", class_="menukad").text
    definition = soup.find("div", class_="lead").text

    inf = None

    for peal, jinj in pealim_to_jinja.items():
        div = soup.find("div", id=peal)
        word = div.find("span", class_="menukad").text
        pron = div.find("div", class_="transcription").text
        td = f"<ruby>{word}<rt>{pron}</rt></ruby>"
        out_dict[jinj] = td

        if peal == "INF-L":
            inf = word

    print(template.render(
        **out_dict
    ))

    print(inf)
    print(definition)
    print_shoresh(shoresh)

    print("פָּעַ") # pa'al
    print("פִּעֵ") # pi'el
    print("הִפְ") # hif'il
    print("הִתְ") # hitpa'el
    print("נִפְ") # niph'al
    # print("פֻּעַ") # pu'al
    # print("הֻפְ") # huf'al



def convert_noun(soup):
    shoresh = None
    for p in soup.find_all("p"):
        if p.text.startswith("Root:"):
            shoresh = p.find("span").text

    definition = soup.find("div", class_="lead").text

    t1 = soup.find("table", class_="conjugation-table")

    singular = t1.find("div", id="s").find("span", class_="menukad").text
    singular_pr = t1.find("div", id="s").find("div", class_="transcription").text
    plural = t1.find("div", id="p").find("span", class_="menukad").text
    plural_pr = t1.find("div", id="p").find("div", class_="transcription").text

    gender = None
    for p in soup.find_all("p"):
        if p.text.startswith("Noun"):
            gender = "נ" if "fem" in p.text.split(" ")[-1] else "ז"

    print(singular)
    print(definition)
    print(gender)
    print_shoresh(shoresh)
    print(plural)
    print(f"{singular_pr}, {plural_pr}")


def convert_adj(soup):
    shoresh = None
    for p in soup.find_all("p"):
        if p.text.startswith("Root:"):
            shoresh = p.find("span").text

    definition = soup.find("div", class_="lead").text

    t1 = soup.find("table", class_="conjugation-table")

    m_singular = t1.find("div", id="ms-a").find("span", class_="menukad").parent.text
    m_singular_pr = t1.find("div", id="ms-a").find("div", class_="transcription").text
    m_plural = t1.find("div", id="mp-a").find("span", class_="menukad").parent.text
    m_plural_pr = t1.find("div", id="mp-a").find("div", class_="transcription").text

    f_singular = t1.find("div", id="fs-a").find("span", class_="menukad").parent.text
    f_singular_pr = t1.find("div", id="fs-a").find("div", class_="transcription").text
    f_plural = t1.find("div", id="fp-a").find("span", class_="menukad").parent.text
    f_plural_pr = t1.find("div", id="fp-a").find("div", class_="transcription").text

    gender = "ז"

    print(f"{m_singular} / {f_singular}")
    print(definition)
    print(gender)
    print_shoresh(shoresh)
    print(f"{m_plural} / {f_plural}")
    print(f"{m_singular_pr} / {f_singular_pr}")
    print(f"{m_plural_pr} / {f_plural_pr}")



valid_pos = ["v", "n", "a"]

if __name__ == "__main__":
    url = sys.argv[2]
    pos = sys.argv[1]
    if pos not in valid_pos:
        sys.exit(0)

    resp = requests.get(url)
    soup = bs(resp.content, features="html.parser")

    if pos == "v":
        convert_verb(soup)
    elif pos == "n":
        convert_noun(soup)
    elif pos == "a":
        convert_adj(soup)
