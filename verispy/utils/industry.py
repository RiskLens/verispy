INDUSTRY_LONG = [
  { "code": "00",   
    "title": "Non Categorized", 
    "short": "Unknown",
    "shorter": "Unknown"
  }, 
  {
    "code": "11",
    "title": "Agriculture, Forestry, Fishing and Hunting",
    "short": "Agriculture (11)",
    "shorter": "Agriculture"
  },
  {
    "code": "21",
    "title": "Mining, Quarrying, and Oil and Gas Extraction",
    "short": "Mining (21)",
    "shorter": "Mining"
  },
  {
    "code": "22",
    "title": "Utilities",
    "short": "Utilities (22)",
    "shorter": "Utilities"
  },
  {
    "code": "23",
    "title": "Construction",
    "short": "Construction (23)",
    "shorter": "Construction"
  },
  {
    "code": "31",
    "title": "Manufacturing",
    "short": "Manufacturing (31)",
    "shorter": "Manufacturing"
  },
  {
    "code": "32",
    "title": "Manufacturing",
    "short": "Manufacturing (32)",
    "shorter": "Manufacturing"
  },
  {
    "code": "33",
    "title": "Manufacturing",
    "short": "Manufacturing (33)",
    "shorter": "Manufacturing"
  },
  {
    "code": "42",
    "title": "Wholesale Trade",
    "short": "Trade (42)",
    "shorter": "Trade"
  },
  {
    "code": "44",
    "title": "Retail Trade",
    "short": "Retail (44)",
    "shorter": "Retail"
  },
  {
    "code": "45",
    "title": "Retail Trade",
    "short": "Retail (45)",
    "shorter": "Retail"
  },
  {
    "code": "48",
    "title": "Transportation and Warehousing",
    "short": "Transportation (48)",
    "shorter": "Transportation"
  },
  {
    "code": "49",
    "title": "Transportation and Warehousing",
    "short": "Transportation (49)",
    "shorter": "Transportation"
  },
  {
    "code": "51",
    "title": "Information Services",
    "short": "Information (51)",
    "shorter": "Information"
  },
  {
    "code": "52",
    "title": "Finance and Insurances",
    "short": "Finance (52)",
    "shorter": "Finance"
  },
  {
    "code": "53",
    "title": "Real Estate and Rental and Leasing",
    "short": "Real Estate (53)",
    "shorter": "Real Estate"
  },
  {
    "code": "54",
    "title": "Professional, Scientific, and Technical Services",
    "short": "Professional (54)",
    "shorter": "Professional"
  },
  {
    "code": "55",
    "title": "Management of Companies and Enterprises",
    "short": "Management (55)",
    "shorter": "Management"
  },
  {
    "code": "56",
    "title": "Administrative and Support and Waste Management and Remediation Services",
    "short": "Administrative (56)",
    "shorter": "Administrative"
  },
  {
    "code": "61",
    "title": "Educational Services",
    "short": "Educational (61)",
    "shorter": "Educational"
  },
  {
    "code": "62",
    "title": "Health Care and Social Assistance",
    "short": "Healthcare (62)",
    "shorter": "Healthcare"
  },
  {
    "code": "71",
    "title": "Arts, Entertainment, and Recreation",
    "short": "Entertainment (71)",
    "shorter": "Entertainment"
  },
  {
    "code": "72",
    "title": "Accommodation and Food Services",
    "short": "Accommodation (72)",
    "shorter": "Accommodation"
  },
  {
    "code": "81",
    "title": "Other Services (except Public Administration)",
    "short": "Other Services (81)",
    "shorter": "Other Services"
  },
  {
    "code": "92",
    "title": "Public Administration",
    "short": "Public (92)",
    "shorter": "Public"
  }
]

INDUSTRY_BY_CODE = {ind['code'] : ind for ind in INDUSTRY_LONG}

INDUSTRY_BY_TITLE = {}
for ind in INDUSTRY_LONG:
    if ind['title'] not in INDUSTRY_BY_TITLE:
        INDUSTRY_BY_TITLE[ind['title']] = {'code': [ind['code']], 'short': [ind['short']], 'shorter': ind['shorter']}
    else:
        INDUSTRY_BY_TITLE[ind['title']]['code'].append(ind['code'])
        INDUSTRY_BY_TITLE[ind['title']]['short'].append(ind['short'])