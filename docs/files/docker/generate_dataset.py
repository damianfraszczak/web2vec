import csv

import pandas as pd

import web2vec as w2v

websites_to_process = {
    "Domain": [
        "sourceforge.net",
        "indianexpress.com",
        "temu.com",
        "indeed.com",
        "messenger.com",
        "zoom.us",
        "accuweather.com",
        "qq.com",
        "espn.com",
        "onlyfans.com",
        "walmart.com",
        "foxnews.com",
        "disneyplus.com",
        "manganato.com",
        "imgur.com",
        "deepl.com",
        "ampproject.org",
        "wordpress.com",
        "instructure.com",
        "banprogrupopromerica-com-84367ee1e040.herokuapp.com",
        "bspoke.cn",
        "cannada.site",
        "crbkmcv.cn",
        "csyvc.cn",
        "cyclope.cn",
        "eglkc.cn",
        "examen.cn",
        "28239929901werb.weebly.com",
        "att-currently-18-10-24.weeblysite.com",
        "myyahoocurrentlyahoomailservice.weeblysite.com",
        "lxqse.cn",
        "mamingsk.bond",
        "mamingso.top",
        "mihqrfe.cn",
        "numyo-teserous.otzo.com",
        "obyvomv.cn",
        "ojhbzra.cn",
        "opuybfj.cn",
        "espace-orange25.weebly.com",
        "urless.com",
    ],
    "is_phish": [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
    ],
}

data = pd.DataFrame(websites_to_process)


websites_parameters = {}
extractors = [
    w2v.HtmlBodyExtractor(),
    w2v.HttpResponseExtractor(),
    w2v.UrlLexicalExtractor(),
    w2v.CertificateExtractor(),
    w2v.OpenPhishExtractor(),
]


# process each domain
for domain, is_phish in zip(data["Domain"], data["is_phish"]):
    url = f"https://{domain}"  # noqa
    websites_parameters[domain] = w2v.process_extractors(
        url, extractors, use_only_numerical=True
    )
    websites_parameters[domain]["is_phish"] = is_phish

# store the parameters in a CSV file
with open("sample_dataset.csv", "w", newline="") as file:
    fieldnames = ["Domain"] + list(next(iter(websites_parameters.values())).keys())
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    for domain, parameters in websites_parameters.items():
        row = {"Domain": domain}
        row.update(parameters)
        writer.writerow(row)

# show the first 5 rows of the dataset
dataset = pd.read_csv("sample_dataset.csv")
dataset.head()
