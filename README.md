# verispy

This is a Python package built for working with VERIS data.  This package has two main purposes:  

  1. Allow the user to extract [VERIS](http://veriscommunity.net/) JSON objects into a Pandas DataFrame structure. The most likely source of VERIS data is the VERIS Community Database ([VCDB](https://github.com/vz-risk/VCDB)).  
  2. Provide some basic data analysis functionality for the DataFrame.  

This is a relatively close port of the `verisr` package for R users, originally built by [Jay Jacobs](https://github.com/jayjacobs/verisr) and now maintained by the Verizon Security Research & Cyber Intelligence Center at [https://github.com/vz-risk/verisr](https://github.com/vz-risk/verisr).  

## Installation

To install this package, either `git clone` this repository, and 

```bash
python -m pip install <path>/verispy/
```

Or, you may simply use:  
```bash
pip install verispy
```

(Note: We have not yet submitted this package to [pypi.org](https://pypi.org/), so as of Aug 2018 the latter option does not work).  

You will also need to download the VCDB data:
```bash
git clone https://github.com/vz-risk/VCDB.git
```

## Loading Data  

After installing, creating a VERIS object is simple. We just need the path to the VCDB json directory:

```python
>>> from verispy import VERIS
>>> data_dir = '../VCDB/data/json'
>>> v = VERIS(json_dir=data_dir)
```

We may wish to verify that the VERIS schema URL is correct:

```python
>>> v.schema_url
'https://raw.githubusercontent.com/vz-risk/veris/master/verisc-merged.json'
```

Then, we can load the VERIS data from the JSON and assign to a DataFrame:

```python
>>> veris_df = v.json2dataframe(verbose=True)
Loading schema
Loading JSON files to DataFrame.
Finished loading JSON files to dataframe.
Building DataFrame with enumerations.
Done building DataFrame with enumerations.
Post-Processing DataFrame (A4 Names, Victim Industries, Patterns)
Finished building VERIS DataFrame
```

## Inspecting Data

Then, we might want to inspect our DataFrame:

```python
>>> veris_df.shape
(7833, 2262)
>>> veris_df.head()
   action.Environmental                  ...                                         victim.victim_id
0                 False                  ...                                          C.R. Bard, Inc.
1                 False                  ...                     British Columbia Ministry of Finance
2                 False                  ...                                                      NaN
3                 False                  ...                                   Camberwell High School
4                 False                  ...                    Loyalist Certification Services Exams

[5 rows x 2262 columns]
```

Do a quick value count on one of the enumerations:

```python
>>> veris_df['action.malware.variety.Ransomware'].value_counts()
False    7711
True      122
Name: action.malware.variety.Ransomware, dtype: int64
```

Most of the enumerations are True/False values.

To see a dictionary of the enumerations, look at the `enumerations` attribute in the VERIS object:  

```python
>>> len(v.enumerations)
61
>>> import pprint
>>> pprint.pprint(v.enumerations)
{'action.environmental.variety': ['Deterioration',
                                  'Earthquake',
                                  'EMI',
                                  'ESD',
                                  'Fire',
                                  'Flood',
                                  'Hazmat',
                                  'Humidity',
                                  'Hurricane',
                                  'Ice',
                                  'Landslide',
                                  'Leak',
                                  'Lightning',
                                  'Meteorite',
                                  'Particulates',
                                  'Pathogen',
                                  'Power failure',
                                  'Temperature',
                                  'Tornado',
                                  'Tsunami',
                                  'Vermin',
                                  'Volcano',
                                  'Wind',
                                  'Other',
                                  'Unknown'],
 'action.error.variety': ['Capacity shortage',
                          'Classification error',
                          'Data entry error',
                          'Disposal error',
                          ... 
                          # many more lines
```

## Analysis

The `getenum_ci` (get enumerations with confidence intervals) function is the main analysis function within `verispy`.  

We can look at top-level enumerations: 

```python
>>> v.getenum_ci(veris_df, 'action')
            enum     x       n     freq
0          Error  2266  7623.0  0.29726
1        Hacking  2078  7623.0  0.27260
2         Misuse  1604  7623.0  0.21042
3       Physical  1517  7623.0  0.19900
4        Malware   633  7623.0  0.08304
5         Social   515  7623.0  0.06756
6  Environmental     8  7623.0  0.00105
7        Unknown   210     NaN      NaN
```

Or lower-level enumerations:

```python
>>> v.getenum_ci(veris_df, 'action.social.variety')
           enum    x      n     freq
0      Phishing  348  499.0  0.69739
1       Bribery   51  499.0  0.10220
2    Pretexting   41  499.0  0.08216
3     Extortion   33  499.0  0.06613
4       Forgery   16  499.0  0.03206
5     Influence   13  499.0  0.02605
6         Other   10  499.0  0.02004
7       Baiting    2  499.0  0.00401
8   Elicitation    2  499.0  0.00401
9    Propaganda    2  499.0  0.00401
10         Scam    2  499.0  0.00401
11         Spam    1  499.0  0.00200
12      Unknown   16    NaN      NaN
```

We can add a second variable as the `by` parameter, and thus get enumerations subsetted by the "by":  

```python
>>> v.getenum_ci(veris_df, 'action', by='attribute')
                           by           enum     x       n     freq
0      attribute.Availability       Physical  1148  2342.0  0.49018
1      attribute.Availability        Hacking   664  2342.0  0.28352
2      attribute.Availability          Error   444  2342.0  0.18958
3      attribute.Availability        Malware   137  2342.0  0.05850
4      attribute.Availability         Misuse    67  2342.0  0.02861
5      attribute.Availability         Social    59  2342.0  0.02519
6      attribute.Availability  Environmental     8  2342.0  0.00342
7      attribute.Availability        Unknown     5     NaN      NaN
8   attribute.Confidentiality          Error  2229  7051.0  0.31613
9   attribute.Confidentiality        Hacking  1683  7051.0  0.23869
10  attribute.Confidentiality         Misuse  1552  7051.0  0.22011
11  attribute.Confidentiality       Physical  1492  7051.0  0.21160
12  attribute.Confidentiality        Malware   553  7051.0  0.07843
13  attribute.Confidentiality         Social   457  7051.0  0.06481
14  attribute.Confidentiality  Environmental     2  7051.0  0.00028
15  attribute.Confidentiality        Unknown   198     NaN      NaN
16        attribute.Integrity        Hacking   913  1820.0  0.50165
17        attribute.Integrity        Malware   631  1820.0  0.34670
18        attribute.Integrity         Social   508  1820.0  0.27912
19        attribute.Integrity       Physical   321  1820.0  0.17637
20        attribute.Integrity         Misuse   256  1820.0  0.14066
21        attribute.Integrity          Error    35  1820.0  0.01923
22        attribute.Integrity  Environmental     0  1820.0  0.00000
23        attribute.Integrity        Unknown    15     NaN      NaN
```

We can add in a confidence interval by specifying the `ci_method` (currently supported methods: `wilson`, `normal`, or `agresti_coull`, see https://www.statsmodels.org/dev/generated/statsmodels.stats.proportion.proportion_confint.html for more information):

```python
>>> v.getenum_ci(veris_df, 'action.social.variety', ci_method='wilson')
           enum    x      n     freq  method    lower    upper
0      Phishing  348  499.0  0.69739  wilson  0.65571  0.73607
1       Bribery   51  499.0  0.10220  wilson  0.07859  0.13189
2    Pretexting   41  499.0  0.08216  wilson  0.06114  0.10957
3     Extortion   33  499.0  0.06613  wilson  0.04747  0.09142
4       Forgery   16  499.0  0.03206  wilson  0.01983  0.05145
5     Influence   13  499.0  0.02605  wilson  0.01529  0.04406
6         Other   10  499.0  0.02004  wilson  0.01092  0.03649
7       Baiting    2  499.0  0.00401  wilson  0.00110  0.01449
8   Elicitation    2  499.0  0.00401  wilson  0.00110  0.01449
9    Propaganda    2  499.0  0.00401  wilson  0.00110  0.01449
10         Scam    2  499.0  0.00401  wilson  0.00110  0.01449
11         Spam    1  499.0  0.00200  wilson  0.00035  0.01126
12      Unknown   16    NaN      NaN  wilson      NaN      NaN
```

And we can change the confidence interval width with `ci_level` (default is 0.95):

```python
>>> v.getenum_ci(veris_df, 'action.social.variety', ci_method='wilson', ci_level=0.5)
           enum    x      n     freq  method    lower    upper
0      Phishing  348  499.0  0.69739  wilson  0.68335  0.71108
1       Bribery   51  499.0  0.10220  wilson  0.09342  0.11172
2    Pretexting   41  499.0  0.08216  wilson  0.07425  0.09084
3     Extortion   33  499.0  0.06613  wilson  0.05902  0.07404
4       Forgery   16  499.0  0.03206  wilson  0.02716  0.03782
5     Influence   13  499.0  0.02605  wilson  0.02166  0.03131
6         Other   10  499.0  0.02004  wilson  0.01623  0.02473
7       Baiting    2  499.0  0.00401  wilson  0.00250  0.00642
8   Elicitation    2  499.0  0.00401  wilson  0.00250  0.00642
9    Propaganda    2  499.0  0.00401  wilson  0.00250  0.00642
10         Scam    2  499.0  0.00401  wilson  0.00250  0.00642
11         Spam    1  499.0  0.00200  wilson  0.00103  0.00388
12      Unknown   16    NaN      NaN  wilson      NaN      NaN
```

The `getenum_ci` function returns a DataFrame. With this enumeration DataFrame, we can then draw a simple horizontal bar chart with the `simplebar` function:

```python
>>> actionci_df = v.getenum_ci(veris_df, 'action')
>>> action_fig = v.simplebar(actionci_df, 'Actions')
>>> action_fig.show()
```

![Action Enumeration Bar Plot](./fig/action_horiz_bar.png)

(Note: plots are best viewed from iPython rather than the Python console, as shown in the examples above).

Finally, we can also look at the DBIR "Patterns," which were originally described in the [2014 DBIR](https://www.verizonenterprise.com/resources/reports/rp_Verizon-DBIR-2014_en_xg.pdf).  

```python
>>> veris_df['pattern'].value_counts()
Miscellaneous Errors      1812
Privilege Misuse          1597
Lost and Stolen Assets    1460
Everything Else           1026
Web Applications           896
Payment Card Skimmers      278
Crimeware                  267
Cyber-Espionage            247
Denial of Service          162
Point of Sale               88
Name: pattern, dtype: int64
``` 

## Clustering with Patterns

Another useful feature of the `verispy` package is the `veris2matrix` function, which converts the VERIS DataFrame into a matrix of boolean values for selected enumerations. This feature is inspired by the blog post by Jay Jacobs, [DBIR Data-Driven Cover](http://datadrivensecurity.info/blog/posts/2014/May/dbir-mds/).  

Note: we are switching to iPython for the following examples because plotting is easier than via the Python console.

```python
In [1]: data_dir = '../VCDB/data/json/'

In [2]: from verispy import VERIS

In [3]: v = VERIS(json_dir=data_dir)

In [4]: veris_df = v.json2dataframe(verbose=True)
Loading schema
Loading JSON files to DataFrame.
Finished loading JSON files to dataframe.
Building DataFrame with enumerations.
Done building DataFrame with enumerations.
Post-Processing DataFrame (A4 Names, Victim Industries, Patterns)
Finished building VERIS DataFrame
```

We can create the VERIS matrix:

```python
In [5]: vmat = v.verisdf2matrix(veris_df)

In [6]: vmat
Out[6]: 
array([[1, 0, 0, ..., 0, 0, 0],
       [0, 0, 0, ..., 0, 0, 0],
       [0, 0, 0, ..., 0, 0, 0],
       ...,
       [0, 0, 0, ..., 0, 0, 0],
       [0, 0, 0, ..., 0, 0, 0],
       [0, 0, 0, ..., 0, 0, 0]])

In [7]: vmat.shape
Out[7]: (7833, 564)

```

Then, we can do a dimensionality-reducing technique called [TSNE](https://lvdmaaten.github.io/tsne/). The following operation may take several minutes:

```python
In [8]: from sklearn.manifold import TSNE

In [9]: tsne = TSNE(n_components=2, random_state=42)

In [10]: v_tsne = tsne.fit_transform(vmat)
``` 

Then, we can create a the following plot, which we have colored by DBIR "Pattern", using Seaborn:

```python
In [11]: import seaborn as sns

In [12]: import pandas as pd

In [13]: import matplotlib.pyplot as plt

In [14]: patterns = v.get_pattern(veris_df)

In [15]: tsne_df = pd.DataFrame({'x':v_tsne[:, 0], 'y':v_tsne[:, 1], 'pattern':patterns['pattern']})

In [16]: tsne_df.head()
Out[16]: 
           x          y               pattern
0   3.178218 -56.336880      Privilege Misuse
1  73.526787 -10.194166  Miscellaneous Errors
2 -74.192070 -48.208408       Cyber-Espionage
3 -48.615826  -0.139661      Web Applications
4 -52.831814  13.343343      Web Applications

In [17]: tsne_centers = tsne_df.groupby(by='pattern').mean()
    ...: tsne_centers['pattern'] = tsne_centers.index

In [18]: p1 = sns.lmplot(x='x', y='y', data=tsne_df, fit_reg=False, hue='pattern', #legend=False, 
    ...:                 scatter_kws={'alpha':0.25}, size=6)
    ...: 
    ...: def label_point(df, ax):
    ...:     for i, point in df.iterrows():
    ...:         ax.text(point['x'] - 30, point['y'], point['pattern'])
    ...:     
    ...: label_point(tsne_centers, plt.gca())
    ...: 
    ...: 

In [19: plt.show()
```
![TSNE plot with clusters](./fig/tsne_clusters.png)







