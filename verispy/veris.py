import pandas as pd
import numpy as np
import json
import urllib.request
import glob
import warnings
import os
from statsmodels.stats.proportion import proportion_confint
import matplotlib.pyplot as plt
from tqdm import tqdm

from .utils import industry as industry_const
from .utils import constants as veris_const


class VERIS(object):
    """ 
    Build a DataFrame from VERIS data.

    This class handles building a DataFrame from raw VERIS-formatted JSON objects. It also supplies some convenient analysis functions to analyze 
    and plot enumerations, their frequencies, and confidence intervals. 

    Parameters
    ------------
    json_dir: str (default: None)
        The directory where the VERIS-formatted JSON files are stored (locally).
    verbose: bool (default: False) 
        Print status messages while processing
    schema_url: str (default: "https://raw.githubusercontent.com/vz-risk/veris/master/verisc-merged.json")
        URL where VERIS schema lives.
    """

    def __init__(self, json_dir=None, verbose=False, schema_url=veris_const.SCHEMA_URL):

        self.json_dir = json_dir
        if json_dir:  # build when building data frame
            self.filenames = glob.glob(os.path.join(json_dir, '*.json'))
            print('Found {} json files.'.format(len(self.filenames)))
            if len(self.filenames) == 0:
                print('Heads up!! No valid json files found in specified directory!')
        else:
            self.filenames = []
        
        self.schema_url = schema_url 

        self.raw_df = None
        self.data = None
        self.enumerations = None
        self.vschema = None
        self.schema_path = None
        self.matrix_enums = veris_const.MATRIX_ENUMS
        self.matrix_ignore = veris_const.MATRIX_IGNORE
        self.industry_by_title = industry_const.INDUSTRY_BY_TITLE

    def _rawjson_to_df(self, filenames, verbose=False):
        """ Take a directory of VERIS-formatted JSON data and convert it to Pandas data frame.

        Parameters
        ----------
        filenames: list
            Filenames of VERIS-schema files to open
        verbose: bool, optional (default: False) 
            Print status messages during processing

        Returns
        -------
        pd DataFrame 
            The raw data (no enuemerations)
        """
        print('Loading JSON files to DataFrame.')
        jsons = []
        for j in tqdm(filenames):
            with open(j, 'r') as f:
                jf = json.load(f)
            jsons.append(jf)
        df_comb = pd.io.json.json_normalize(jsons)
        if verbose : print('Finished loading JSON files to dataframe.')

        return df_comb

    def _enums_from_schema(self, schema, curvarname='', outlist=[]):
        """ Recursively determine the enumerations from the schema.

        Parameters
        ----------
        schema: dict
            The VERIS schema JSON, loaded in the `json_to_df` function
        curvarname: str, (default: '') 
            The current varname, gets used in the recursion process
        outlist: list, (default: [])
            List of dictionaries of the enumerations from the schema

        Returns
        -------
        list
            Dictionaries of the schema
        """
        if type(schema) is dict: 

            if 'items' in schema.keys():
                if 'enum' in schema['items'].keys():
                    return {'name': curvarname, 'enumlist': schema['items']['enum'], 'type': schema['type']}
                else:
                    return self._enums_from_schema(schema['items'], curvarname, outlist)
            elif 'type' in schema.keys():
                if schema['type'] == 'object' and 'properties' in schema.keys():
                    return self._enums_from_schema(schema['properties'], curvarname, outlist)
                elif 'enum' in schema.keys():
                    return {'name': curvarname, 'enumlist': schema['enum'], 'type': schema['type']}
                else:
                    return {'name': curvarname, 'type': schema['type']}
            else:
                for key in schema.keys():
                    newvarname = '.'.join((curvarname, key)) if len(curvarname) > 0 else key
                    if curvarname in veris_const.VARIETY_AMT_ENUMS and key == 'amount': # pull these out into a separate variable!
                        newenumfinder = self._enums_from_schema(schema['variety'], newvarname, outlist)
                    else:
                        newenumfinder = self._enums_from_schema(schema[key], newvarname, outlist)
                    if type(newenumfinder) is dict:
                        outlist.append(newenumfinder) 
                
        return outlist


    def _combine_enums_raw_df(self, enums, non_enums, raw_df):
        """ Combine the raw DataFrame with the enumerations from that DataFrame

        Parameters
        ----------
        enums: dict 
            Output of `_build_enumerations_dict`
        non_enums: list
             The non-enumeration variables
        raw_df: pd DataFrame
            Output of `_rawjson_to_df`

        Returns
        -------
        pd DataFrame 
            With columns from the raw DataFrame and enumerations.
        """

        # function to check the enumerations in the raw dataframe and set to True-False
        def enum_checker(dfitem, enumitem):
            if type(dfitem) is list:
                if enumitem in dfitem:
                    return True
            elif type(dfitem) is str:
                if enumitem == dfitem:
                    return True
            return False

        def var_amt_enum_checker(dfitem, enumitem, variety_or_amt):  
            if type(dfitem) is list:
                for value in dfitem:
                    if type(value) is dict and variety_or_amt in value.keys() and value['variety'] == enumitem:
                        if variety_or_amt == 'variety':  
                            return True
                        elif variety_or_amt == 'amount':
                            return value[variety_or_amt]
                    if type(value) is str:
                        if value == enumitem:
                            return True

            # if found nothing, return value depends on whether this is a variety or amount
            return False if variety_or_amt == 'variety' else None


        comb_df = pd.DataFrame()
        top_level_enums = [enum for enum in enums]
        print('Building enumeration columns.')
        for col in tqdm(raw_df.columns):
            if col in top_level_enums:
                # go through the enumerations
                for item in enums[col]:
                    newvarname = '.'.join((col, item))
                    comb_df[newvarname] = raw_df[col].apply(lambda x: enum_checker(x, item))
            elif col in veris_const.VARIETY_AMT_ENUMS:  # handle "variety" and "amount" pairs separately
                for variety_or_amt in veris_const.VARIETY_AMT:
                    enum_var_or_amt = '.'.join((col, variety_or_amt))
                    for item in enums[enum_var_or_amt]:
                        newvarname = '.'.join((enum_var_or_amt, item))
                        comb_df[newvarname] = raw_df[col].apply(lambda x: var_amt_enum_checker(x, item, variety_or_amt))
            else:
                comb_df[col] = raw_df[col]

        # now add in the rest of the enumerations
        comb_df_cols = comb_df.columns
        for enum in enums:
            for suffix in enums[enum]:
                var = '.'.join((enum, suffix))
                if var not in comb_df_cols:
                    comb_df[var] = False

        # add in the variables which were not enumerations
        comb_df_cols = comb_df.columns
        for vardict in non_enums:
            varname = vardict['name']
            vartype = vardict['type']
            if varname not in comb_df_cols:  # only add the columns in that haven't already been added
                if vartype == 'string':
                    comb_df[varname] = None
                elif vartype == 'integer' or vartype == 'number':
                    comb_df[varname] = np.nan
                else:
                    comb_df[varname] = None 


        return comb_df

    def _aggregate_a4s(self, df):
        """ Add in the A4 Names; apply OR operation to the binary vars making up the a4(A4: http://veriscommunity.net/a4grid.html).

        This function is normally called from `json_to_df` and should not be called individually.

        Parameters
        ----------
        df: pd DataFrame 
            DataFrame following from `self._combine_enums_raw_df`

        Returns
        -------
        pd DataFrame 
            With A4 names and values added in.
        """

        revassetmap = {veris_const.ASSETMAP[key]: key for key in veris_const.ASSETMAP}

        for name in veris_const.A4NAMES:
            if name.startswith('asset'):
                assetdict = veris_const.A4NAMES[name]
                varname = '.'.join((name, 'variety'))
                for suffix in assetdict['variety']:
                    fullname = '.'.join((varname, suffix))
                    searchname = '.'.join((name, 'assets.variety', revassetmap[suffix]))
                    df[fullname] = df[[col for col in df.columns if col.startswith(searchname)]].sum(axis=1)
                    df[fullname] = df[fullname].apply(lambda x: True if x >= 1 else False)
            else:
                for suffix in veris_const.A4NAMES[name]:
                    fullname = '.'.join((name, suffix))
                    searchname = fullname.lower()
                    searchnames = ['.'.join((attr, suffix)) for attr in self.enumerations \
                                   for suffix in self.enumerations[attr] if attr.startswith(searchname)]

                    df[fullname] = df[searchnames].sum(axis=1)
                    if fullname == 'attribute.Confidentiality':
                        # Need to remove attribute.confidentiality.data_disclosure.No
                        # and attribute.confidentiality.data_disclosure.Unknown from sum/searchlist
                        # Unsure if I should leave in attribute.confidentiality.data_disclosure.Potentially.  Will do so for now.
                        #  Note: after testing both ways, it doesn't much matter, because `True`s get summed over the partial values too. 
                        searchnames.remove('attribute.confidentiality.data_disclosure.No')
                        searchnames.remove('attribute.confidentiality.data_disclosure.Unknown')
                        df[fullname] = df[searchnames].sum(axis=1)
                    elif suffix == 'Unknown': # actor.Unknown, action.Unknown -- should be complement of other A4 enums in its class
                        # get all other searchnames
                        unk_searchnames = ['.'.join((name, suff.lower())) for suff in veris_const.A4NAMES[name] \
                                           if suff != 'Unknown']
                        unk_searchnames_long = ['.'.join((attr, suffix)) for attr in self.enumerations \
                                                for suffix in self.enumerations[attr] \
                                                for searchname in unk_searchnames \
                                                if attr.startswith(searchname) ]
                        df[fullname] = df[unk_searchnames_long].sum(axis=1)
                        df[fullname] = -(df[fullname] - 1) # trick to get True/False working right
                    
                    # might have some numerical values that should just be True
                    df[fullname] = df[fullname].apply(lambda x: True if x >= 1 else False)

        return df

    def _victim_postproc(self, df):
        """ Fill in the victim industries with the 2-digit and 3-digit enumerations columns, and additional information about organization size.

        Parameters
        ----------
        df: pd DataFrame 
            A processed data frame (from `json_to_df`) with a `victim.industry` column.

        Returns
        -------
        pd DataFrame 
            Returns initial DataFrame, but with processed `victim.industry*` columns and orgsize columns.
        """

        # get victim industry 2 and 3
        df['victim.industry2'] = df['victim.industry'].apply(lambda x: str(x)[:2] if not pd.isnull(x) else None)
        df['victim.industry3'] = df['victim.industry'].apply(lambda x: str(x)[:3] if not pd.isnull(x) else None)

        # victim industry name
        known_ind_codes = list(industry_const.INDUSTRY_BY_CODE.keys())
        df['victim.industry.name'] = df['victim.industry2'].apply(
            lambda x: industry_const.INDUSTRY_BY_CODE[x]['shorter'] if x in known_ind_codes else 'Unknown')

        # fill out the 2-digit code columns
        for code in industry_const.INDUSTRY_BY_CODE.keys(): #df['victim.industry2'].unique():
            colname = '.'.join(('victim.industry2', code))
            df[colname] = df['victim.industry2'].apply(lambda x: True if x == code else False)

        # partner industry
        df['actor.partner.industry2'] = df['actor.partner.industry'].apply(lambda x: str(x)[:2] if not pd.isnull(x) else None)

        # next fill out orgsize
        for orgsize, orgcols in veris_const.ORG_SMALL_LARGE.items():
            df[orgsize] = df[[col for col in df.columns if col in orgcols]].sum(axis = 1)
            df[orgsize] = df[orgsize].apply(lambda x: True if x >= 1 else False)

        return df

    def load_schema(self, schema_path=None, schema_url=None):
        """ Load the VERIS schema into the VERIS object

        This function is normally called from the `json_to_df` function; however, if you would like to individually load the schema for whatever reason
        you may do so here. 

        Parameters
        ----------
        schema_path: str, optional (default: None)
            Specify a path if you wish to load the schema from local memory.
        schema_url: str, optional (default: None)
            If you wish to specify the url to the schema. `schema_path` takes precedence if it is populated.  Check the object's `schema_url` attribute first,
            the schema location may already be in the object.
        Return
        ------
        None
            Schema is stored in the `self.vschema` attribute of the VERIS object 
        """
        if schema_path:  # load from the local computer if possible
            self.schema_path = schema_path
            with open(schema_path, 'r') as f:
                vschema = json.load(f)
        else:
            if schema_url:
                self.schema_url = schema_url
            with urllib.request.urlopen(self.schema_url) as url:
                vschema = json.loads(url.read().decode())
        self.vschema = vschema

    def json_to_df(self, filenames=None, keep_raw=False, schema_path=None, schema_url=None, verbose=False):
        """ Take a directory of VERIS-formatted JSON data and convert it to pd DataFrame

        This is the main data conversion function of the `verispy` package. It takes a directory full of VERIS-formatted JSON files and converts the files
        from JSON (difficult to work with) to a pd DataFrame (slightly easier to work with). This function also requires a valid VERIS schema (in JSON format).
        At the time of package creation, the VERIS schema was on the [veris GitHub](https://github.com/vz-risk/veris) at 
        [https://raw.githubusercontent.com/vz-risk/veris/master/verisc-merged.json](https://raw.githubusercontent.com/vz-risk/veris/master/verisc-merged.json). 
        This package also maintains a copy of the schema herein, in the data directory, in case it cannot find the schema online. 
        The user may also specify a new url if needed.


        Parameters
        ----------
        filenames: list, optional (default: None)
            List of filenames of VERIS-schema files to open, ideally from the local file system. Not needed if `json_dir` passed when object initialized.
        keep_raw: bool (default: False)
            Keep the raw data frame, created before creating the enumerations?  If `True`, it is stored in the `raw_df` attribute in the current object.
        schema_path: str, optional (default: None)
            Specify a path if you wish to load the schema from local memory.
        schema_url: str, optional (default: None)
            If you wish to specify the url to the schema. `schema_path` takes precedence if it is populated.  Check the object's `schema_url` attribute first,
            the schema location may already be in the object.
        verbose: bool, (default: False)
            Print progress messages during processing.
        
        Returns
        -------
        pd DataFrame 
            The parsed, structured VERIS data. This function will also populate the `enumerations` attribute, which may be useful. 
        """

        # load schema
        if verbose: print('Loading schema')
        self.load_schema(schema_path, schema_url)

        if not filenames:
            filenames = self.filenames

        if len(filenames) == 0:
            warnings.warn('No valid JSON filenames passed to `json_to_df` function. This returns a Data Frame with 0 rows.')

        raw_df = self._rawjson_to_df(filenames, verbose)

        if keep_raw : self.raw_df = raw_df

        # build the enumerations
        if verbose : print('Building DataFrame with enumerations.')

        enum_list = self._enums_from_schema(self.vschema, '', [])
        self.enumerations = {item['name']: item['enumlist'] for item in enum_list if 'enumlist' in item}
        self.nonenum_vars = [item for item in enum_list if 'enumlist' not in item]

        comb_df = self._combine_enums_raw_df(self.enumerations, self.nonenum_vars, raw_df)

        if verbose : print('Done building DataFrame with enumerations.')

        # add in A4 names
        if verbose: print('Post-Processing DataFrame (A4 Names, Victim Industries, Patterns)')
        comb_df = self._aggregate_a4s(comb_df)

        # victim industries
        comb_df = self._victim_postproc(comb_df)

        # sort columns alphabetically
        comb_df = comb_df.reindex(sorted(comb_df.columns), axis=1)

        print('Finished building VERIS DataFrame')

        return comb_df

    def df_to_matrix(self, df, bools_only=True):
        """ Convert VERIS DataFrame to binary matrix for clustering

        This function takes a DataFrame obtained through the `json_to_df` function and converts it to a numpy
        matrix for use with distance functions.  

        To change the default variables filtered on, the user can change the `matrix_enums` or `matrix_ignore` attributes.  

        Parameters
        ----------
        df: pd DataFrame 
            DataFrame returned by `json_to_df` function
        bools_only: bool (default: True)
            Whether to return just the boolean enumerations. If False, will scale numerical values. At this time, `False` logic not yet implemented

        Returns
        -------
        np ndarray
            Array of 0-1 values for False-True, and scaled numerical values.
        """

        if bools_only:
            boolvars = [col for col in df.columns if df[col].dtype == bool]
            cols_enums = set([col for enum in self.matrix_enums for col in boolvars if col.startswith(enum)])
            ignore_enums = set([enum for ignore in self.matrix_ignore for enum in cols_enums if ignore in enum])
            keep_cols = list(cols_enums.difference(ignore_enums))
            matrix = np.array(df[keep_cols]).astype(int)
            # do we need to save off incident_id or anything like that?
        else:
            raise NotImplementedError('The bools_only=False logic is not yet implemented.')
            # with the keep_cols, we need to hold on to the order of those columns *and* their types, as well as scaling
            # factors if and when we implement that part of the code.  This would be helpful in many ways because
            # it would allow us to perhaps pull out sections of the data and matricize it, and then find the "average" for 
            # columns of interest.   

        return matrix

    def enum_summary(self, df, enum, by=None, use_unk=False, ci_method=None, ci_level=0.95, round_freq=5):
        ''' Build summary DataFrame given a VERIS enumeration

        This function is the primary analysis and summary function for the `verispy` package. At a minimum, it calculates the count and frequency
        of a given enumeration or set of enumerations within a feature. If desired, it can conduct binomial hypothesis tests on the selected 
        enumeration. (For example, 'Malware', 'Hacking', etc within 'action').
        The 'by' parameter allows enumerating one feature by another, (for example to count the frequency of each action by year).

        Parameters
        ----------
        df: pd DataFrame
            DataFrame from the `json_to_df` function
        enum: string
            VERIS feature or enumeration to summarize
        by: string, optional (default: None)
            VERIS feature or enumeration to group by
        use_unk: bool, optional (default: False) 
            Use 'Unknown' values in the frequency calculations
        ci_method: str, optional (default: None) 
            Method to use for producing the confidence intervals. Use one of "wilson", "normal", or "agresti_coull" for best results. 
            See `statsmodels.stats.proportion.proportion_confint` for more details.
        ci_level: float, optional (default: 0.95)
            Confidence interval to use when specifying the `ci_method`
        round_freq: int (default: 5) 
            Decimal places to round the frequency values to

        Returns
        -------
        pd DataFrame
            DataFrame with the enumeration summary. 

        See Also
        --------
        statsmodels.stats.proportion.proportion_confint: confidence interval for a binomial proportion
        
        '''
        
        # get all the variables that start with enum (`enum.`) and only keep the ones that are length 1 longer and boolean:

        if enum in df.columns and df[enum].dtype in ['int', 'float']:
            enum_is_col = True
            keep_list = list(set(df[enum]))
        else:
            enum_is_col = False
            enum_len = len(enum.split('.'))
            keep_list = [col for col in df.columns if col.startswith('.'.join((enum, '')))]
            keep_list = [col for col in keep_list if len(col.split('.')) == enum_len + 1]
            keep_list = [col for col in keep_list if df[col].dtype == 'bool']
        
        if by: # split into sub-dataframes if there is a `by` parameters
            # need to be able to tell if "by" is already a column (like `timeline.incident.year`, or if we are looking at enumerations of it)
            if by in df.columns and df[by].dtype in ['int', 'float']:   # `by` is a column and an int or float
                uniques = set(df[by])
                # remove nans
                uniques = {x for x in uniques if x==x}
                subdfs = [(unique_val, df[df[by] == unique_val]) for unique_val in uniques]
            else:  # check to see if `by` is an enumeration (should we do this check before the column check? Does it matter?)
                by_len = len(by.split('.'))
                by_list = [col for col in df.columns if col.startswith('.'.join((by, '')))]
                by_list = [col for col in by_list if len(col.split('.')) == by_len + 1]
                by_list = [col for col in by_list if df[col].dtype == 'bool']
                if len(by_list) == 0:
                    warnings.warn('Could not find enumeration columns matching "by" value "{}". Ignoring this value at this time.'.format(by))
                    by = None
                    subdfs = [(None, df)]
                else:
                    subdfs = [(by_col, df[df[by_col]]) for by_col in by_list]
        else:
            subdfs = [(None, df)]
        
        # Calculate the enumerations. Because of `subdfs` structure, doing whole dataframe or subsets can be done at once
        outdfs = []
        for curby, subdf in subdfs:
            if enum_is_col:
                count = subdf.shape[0]
            else:
                if use_unk:  # what if enum_is_col
                    count = subdf[keep_list].any(axis=1).sum()
                else:
                    count = subdf[[col for col in keep_list if col.split('.')[-1].lower() != 'unknown']].any(axis=1).sum()

            enum_dict = {'by': [], 'enum': [], 'x': [], 'n': []}
            if enum_is_col:
                for val in keep_list:
                    num_this_val = subdf[subdf[enum] == val].shape[0]
                    if num_this_val == 0: continue
                    enum_dict['by'].append(curby)
                    enum_dict['n'].append(count) # check this
                    enum_dict['enum'].append(val)
                    enum_dict['x'].append(num_this_val)
            else:
                for var in keep_list:
                    var_suff = var.split('.')[-1]
                    enum_dict['by'].append(curby)
                    enum_dict['enum'].append(var_suff)
                    enum_dict['x'].append(subdf[var].sum())
                    if var_suff.lower() != 'unknown' or use_unk:
                        enum_dict['n'].append(count)
                    else:
                        enum_dict['n'].append(np.nan)
            out_df = pd.DataFrame(enum_dict)
            out_df['freq'] = np.round(out_df['x'] / out_df['n'], round_freq)
            out_df.sort_values(by=['freq'], ascending=False, inplace=True)
            out_df.reset_index(inplace=True, drop=True)
            outdfs.append(out_df)
            
        out_df = pd.concat(outdfs)
        if not by:
            out_df.drop('by', axis=1, inplace=True)

        if ci_method:
            out_df['method'] = ci_method
            out_df['lower'], out_df['upper'] = np.round(proportion_confint(out_df['x'], out_df['n'], alpha=1-ci_level, method=ci_method), round_freq)
        
        out_df.reset_index(inplace=True, drop=True)

        return out_df


    def plot_barchart(self, enum_df, title=None, fill='darkred', use_top=-1, **kwargs):
        """ Produce a simple horizontal bar chart from an `enum_summary` DataFrame.

        Using the results of `enum_summary`, produce a simple horizontal bar chart with the enumerations and their frequencies labeled on the plot.

        Parameters
        ----------
        enum_df: pd DataFrame
            DataFrame returned by the `enum_summary` function. Must have `enum` and `freq` columns.
        title: str
            Title for the plot.
        fill: str
            Bar fill color
        use_top: int, (default: -1)
            Only plot the top `use_top` enumerations (useful for large DataFrames).  A value of -1 defaults to the entire DataFrame
        **kwargs: 
            Additional arguments to pass to `matplotlib.pyplot.barh`

        Returns
        -------
        matplotlib fig
            Returns the figure just created.

        See Also
        --------
        matplotlib.pyplot.barh: Matplotlib horizontal bar plot
        """
        if use_top <= 0:
            use_top = enum_df.shape[0]

        enum_df = enum_df.iloc[:use_top]

        fig, ax = plt.subplots()
        ax.barh(enum_df['enum'], enum_df['freq'], color=fill, **kwargs)
        for i, f in enumerate(enum_df['freq']):
            if np.isnan(f):
                continue
            ax.text(f, i, ' {}%'.format(round(100 * f, 0)))
        if title:
            plt.title(title)
        fig.gca().invert_yaxis()

        return fig
