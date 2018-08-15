# as fetched directly from `verisr` using the following commands:
# > data(industry2, envir = environment(), package='verisr')
# > jsonlite::toJSON(industry2, pretty = TRUE)

INDUSTRY_LONG = [
  { "code": "00",   # this actually isn't in the VERIS, added in by TGB
    "title": "Unknown", 
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
    "title": "Mining",
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
    "title": "Information",
    "short": "Information (51)",
    "shorter": "Information"
  },
  {
    "code": "52",
    "title": "Finance and Insurance",
    "short": "Finance (52)",
    "shorter": "Finance"
  },
  {
    "code": "53",
    "title": "Real Estate Rental and Leasing",
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
    "short": "Accomodation (72)",
    "shorter": "Accomodation"
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