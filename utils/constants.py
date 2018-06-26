SCHEMA_URL = "https://raw.githubusercontent.com/vz-risk/veris/master/verisc-merged.json"
VARIETY_AMT_ENUMS = ['asset.assets', 'attribute.confidentiality.data']
VARIETY_AMT = ['variety', 'amount']
ASSETMAP = {'S ' : 'Server', 'N ' : 'Network', 'U ' : 'User Dev', 'M ' : 'Media',
            'P ' : 'Person', 'T ' : 'Kiosk/Term', 'Un' : 'Unknown', 'E ' : 'Embedded'}
A4NAMES = {'actor': ['External', 'Internal', 'Partner', 'Unknown'],
           'action': ['Malware', 'Hacking', 'Social', 'Physical', 'Misuse', 'Error', 'Environmental', 'Unknown'],
           'attribute': ['Confidentiality', 'Integrity', 'Availability'],
           'asset': {'variety': list(ASSETMAP.values()), 
                     'assets.variety': list(ASSETMAP.keys())}}