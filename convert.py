from typing import List, NamedTuple
from bs4 import BeautifulSoup as bs
import requests
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

templates_dir = Path(__file__).parent
templates_dir = templates_dir.absolute()

env = Environment(loader=FileSystemLoader(templates_dir))
template = env.get_template("verb_he_en.html")

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
    "INF-L": "inf",
}


class HebrewCard(NamedTuple):
    Hebrew: str
    Definition: str
    Gender: str
    PartOfSpeech: str
    Shoresh: str
    Audio: str
    Inflections: str
    Extended: str
    Image: str

    def __post_init__(self):
        """Perform validation on Gender, PartOfSpeech"""
        if self.Gender not in ["", "נ", "ז", "פָּעַ", "פִּעֵ", "הִפְ", "הִתְ", "נִפְ"]:
            self.Gender = ""

        if self.PartOfSpeech not in ["n", "v", "a", ""]:
            self.PartOfSpeech = ""

    def to_list(self) -> List[str]:
        return [
            self.Hebrew,
            self.Definition,
            self.Gender,
            self.PartOfSpeech,
            self.Shoresh,
            self.Audio,
            self.Inflections,
            self.Extended,
            self.Image,
        ]


def convert_shoresh(shoresh: str) -> str:
    if not shoresh:
        return
    shoresh = shoresh.replace("-", "־")
    shoresh = "".join(shoresh.split())
    return shoresh


def extract_binyan(text: str):
    upper = text.upper()
    if "PA'AL" in upper:
        return "פָּעַ"  # pa'al
    elif "PI'EL" in upper:
        return "פִּעֵ"
    elif "HIF'IL" in upper:
        return "הִפְ"
    elif "HITPA'EL" in upper:
        return "הִתְ"
    elif "NIF'AL" in upper:
        return "נִפְ"
    elif "PU'AL" in upper:
        return "פֻּעַ"
    elif "HUF'AL" in upper:
        return "הֻפְ"
    else:
        return ""


def convert_verb(soup) -> HebrewCard:
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

    binyan_p = get_subheader(soup)
    binyan = extract_binyan(binyan_p)

    return HebrewCard(
        Hebrew=inf,
        Definition=definition,
        Gender=binyan,
        PartOfSpeech="v",
        Shoresh=convert_shoresh(shoresh),
        Audio="",
        Inflections=template.render(**out_dict),
        Extended="",
        Image="",
    )


def convert_noun(soup) -> HebrewCard:
    shoresh = None
    for p in soup.find_all("p"):
        if p.text.startswith("Root:"):
            shoresh = p.find("span").text

    definition = soup.find("div", class_="lead").text

    t1 = soup.find("table", class_="conjugation-table")

    singular = t1.find("div", id="s").find("span", class_="menukad").text
    singular_pr = t1.find("div", id="s").find("div", class_="transcription").text

    plural_div = t1.find("div", id="p")
    plural, plural_pr = "", ""
    if plural_div is not None:
        plural = plural_div.find("span", class_="menukad").text
        plural_pr = plural_div.find("div", class_="transcription").text

    gender = None
    for p in soup.find_all("p"):
        if p.text.startswith("Noun"):
            gender_field = p.text.split(" ")[-1]
            gender = "נ" if "fem" in gender_field else ""
            gender = "ז" if "mas" in gender_field else ""

    return HebrewCard(
        Hebrew=singular,
        Definition=definition,
        Gender=gender,  # TODO
        PartOfSpeech="n",
        Shoresh=convert_shoresh(shoresh),
        Audio="",
        Inflections=plural,
        Extended=f"{singular_pr}, {plural_pr}",
        Image="",
    )


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

    gender = ""

    return HebrewCard(
        Hebrew=f"{m_singular} / {f_singular}",
        Definition=definition,
        Gender=gender,
        PartOfSpeech="n",
        Shoresh=convert_shoresh(shoresh),
        Audio="",
        Inflections=f"{m_plural} / {f_plural}",
        Extended=f"{m_singular_pr} / {f_singular_pr}\n{m_plural_pr} / {f_plural_pr}",
        Image="",
    )


def extract_pos(text: str):
    if "noun" in text.lower():
        return convert_noun
    if "verb" in text.lower():
        return convert_verb
    if "adjective" in text.lower():
        return convert_adj


def get_subheader(soup) -> str:
    return soup.find("h2", class_="page-header").nextSibling.text


def translate(url) -> List[str]:
    resp = requests.get(url)
    soup = bs(resp.content, features="html.parser")

    pos_p = get_subheader(soup)
    fun = extract_pos(pos_p)

    return fun(soup).to_list()
