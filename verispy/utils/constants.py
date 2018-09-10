SCHEMA_URL = "https://raw.githubusercontent.com/vz-risk/veris/master/verisc-merged.json"
VARIETY_AMT_ENUMS = ['asset.assets', 'attribute.confidentiality.data', 'impact.loss']
VARIETY_AMT = ['variety', 'amount']
ASSETMAP = {'S ' : 'Server', 'N ' : 'Network', 'U ' : 'User Dev', 'M ' : 'Media',
            'P ' : 'Person', 'T ' : 'Kiosk/Term', 'Un' : 'Unknown', 'E ' : 'Embedded'}
A4NAMES = {'actor': ['External', 'Internal', 'Partner', 'Unknown'],
           'action': ['Malware', 'Hacking', 'Social', 'Physical', 'Misuse', 'Error', 'Environmental', 'Unknown'],
           'attribute': ['Confidentiality', 'Integrity', 'Availability'],
           'asset': {'variety': list(ASSETMAP.values()), 
                     'assets.variety': list(ASSETMAP.keys())}}
SMALL_ORG_SUFFIXES = ['1 to 10', '11 to 100', '101 to 1000', 'Small']
LARGE_ORG_SUFFIXES = ['1001 to 10000', '10001 to 25000', '25001 to 50000', '50001 to 100000', 'Over 100000', 'Large']
SMALL_ORG = ['.'.join(('victim.employee_count', suffix)) for suffix in SMALL_ORG_SUFFIXES]
LARGE_ORG = ['.'.join(('victim.employee_count', suffix)) for suffix in LARGE_ORG_SUFFIXES]
ORG_SMALL_LARGE = {'victim.orgsize.Small' : SMALL_ORG, 'victim.orgsize.Large' : LARGE_ORG}

# MATRIX CONSTANTS
MATRIX_ENUMS = ['actor', 'action', 'victim.employee_count', 'security_incident', 'asset.assets', 
               "asset.assets.variety", "asset.cloud", "asset.hosting", "asset.management", "asset.ownership",
               "attribute.confidentiality.data.variety", "attribute.confidentiality.data_disclosure",
               "discovery_method", "targeted", "attribute.integrity.variety", "attribute.availability.variety"]
MATRIX_IGNORE = ['cve', 'name', 'notes', 'country', 'industry']