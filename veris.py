# Code for building data frames from VERIS JSON files and working with them

import pandas as pd
import numpy as np
import json
import urllib.request
import glob

from .utils import industry as industry_const
from .utils import constants as veris_const
from .patterns import get_pattern


class VERIS(object):
    """ 
    Build a dataframe from VERIS data

    Parameters
    ------------
    json_dir: str, the directory where the JSON files are stored (locally)
    verbose: bool, print messages while processing
    """

    def __init__(self, json_dir=None, verbose=False):

        self.json_dir = json_dir
        if json_dir:  # build when building data frame
            self.filenames = glob.glob('*'.join((json_dir, 'json')))
            if verbose : print('Found {} json files.'.format(len(self.filenames)))
        else:
            self.filenames = []
        
        self.schema_url = veris_const.SCHEMA_URL # I don't want to have to fetch from the internet though  TODO -- READ STATIC FILE FROM INSIDE PACKAGE

        self.raw_df = None
        self.data = None
        self.enumerations = None
        self.vschema = None
        self.schema_path = None

    def _rawjson2dataframe(self, filenames, verbose=False):
        """ Take a directory of VERIS-formatted JSON data and convert it to Pandas data frame.

        Parameters
        ----------
        filenames: List of filenames of VERIS-schema files to open
        verbose: bool, print messages during processing

        Returns
        -------
        pd.DataFrame of the raw data (no enuemerations)
        """
        if verbose : print('Loading JSON files to DataFrame.')
        jsons = []
        for j in filenames:
            with open(j, 'r') as f:
                jf = json.load(f)
            jsons.append(jf)
        df_comb = pd.io.json.json_normalize(jsons)
        if verbose : print('Finished loading JSON files to dataframe.')

        return df_comb

    def _enums_from_schema(self, schema, curvarname='', outlist=[]):
        """ Recursively determine the enumerations from the schema

        Parameters
        ----------
        schema: dict, The VERIS schema JSON, loaded in the json2dataframe
        curvarname: str, the current varname, gets used in the recursion process
        outlist: list, list of dictionaries of the enumerations from the schema

        Returns
        -------
        list of dictionaries of the schema
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
                    # need to handle a couple situations explicitly:
                
        return outlist


    def _combine_enums_raw_df(self, enums, non_enums, raw_df):
        """ Combine the raw data frame with the enumerations from that data frame

        Parameters
        ----------
        enums: dict, output of `_build_enumerations_dict`
        non_enums: list, the non-enumeration variables
        raw_df: pd DataFrame, output of `_rawjson2dataframe`

        Returns
        -------
        pd DataFrame with columns from the raw DataFrame and enumerations

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

        def var_amt_enum_checker(dfitem, enumitem, variety_or_amt):  # TODO: NEEDS TO HANDLE AMOUNTS NOT JUST VARIETIES!
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
        for col in raw_df.columns:
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

        # add in the variables which were not enumeations
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

    def _a4names(self, df):
        """ Add in the A4 Names and their "sums" (A4: http://veriscommunity.net/a4grid.html) 

        Parameters
        ----------
        df: pd DataFrame following from `self._combine_enums_raw_df`

        Returns
        -------
        pd DataFrame with A4 names and values added in
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

                    if suffix == 'Confidentiality':
                        # TODO: current functionality matches what is done in verisr; however, that appears to be a bug
                        # what we need to do is remove attribute.confidentiality.data_disclosure.No, 
                        # and attribute.confidentiality.data_disclosure.Unknown, and possibly
                        # attribute.confidentiality.data_disclosure.Potentially. However, since this is currently
                        # in verisr, I'm going to hold off until I can verify further (or possibly ignore??)
                        pass
                    elif suffix == 'Unknown': # actor.Unknown, action.Unknown -- should be complement of other A4 enums in its class
                        # get all all other searchnames
                        # TODO: This works but is a mess. would be better to fetch other A4 names after they are created (maybe?)
                        unk_searchnames = ['.'.join((name, suff.lower())) for suff in veris_const.A4NAMES[name] \
                                           if suff != 'Unknown']
                        unk_searchnames_long = ['.'.join((attr, suffix)) for attr in self.enumerations \
                                                for suffix in self.enumerations[attr] \
                                                for searchname in unk_searchnames \
                                                if attr.startswith(searchname) ]
                        df[fullname] = df[unk_searchnames_long].sum(axis=1)
                        df[fullname] = -(df[fullname] - 1) # trick to get True/False working right
                    else:
                        pass
                    df[fullname] = df[fullname].apply(lambda x: True if x >= 1 else False)



        return df

    def _victim_postproc(self, df):
        """ Fill in the victim industries with the 2-digit and 3-digit enumerations columns. And more info about orgsize

        Parameters
        ----------
        df: pd DataFrame with at least a `victim.industry` column

        Returns
        -------
        pd DataFrame with moar `victim.industry*` columns
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

        Parameters
        ----------
        schema_path: str, if you wish to load the schema from local memory
        schema_url: str, if you wish to specify the path to the schema. schema_path takes precedence if populated. 
                    Check the object's `schema_url` attribute first 
        Return
        ------
        None -- Saved into the `self.vschema` attribute of the VERIS object 

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


    def get_pattern(self, df):
        """ Generates the patterns as described originally in the 2014 DBIR. 
        This function is is almost an exact port from the verisr package: https://github.com/vz-risk/verisr/blob/a293801eb92dda9668844f4f7be14bf5c685d764/R/matrix.R#L78

        Parameters
        ----------
        df: pd DataFrame - VERIS-formatted Pandas DataFrame. This function likely won't work unless you've already 
           almost completely generated the VERIS df.

        Returns
        -------
        A new pd DataFrame with the patterns. Note: does not return the original VERIS data frame

        """
        return get_pattern(df) 

    def json2dataframe(self, filenames, keep_raw=False, verbose=False, schema_path=None, schema_url=None):
        """ Take a directory of VERIS-formatted JSON data and convert it to Pandas data frame


        Parameters
        ----------
        filenames: List of filenames of VERIS-schema files to open. 
        keep_raw: bool, Keep the raw data frame, created before creating the enumerations?
        verbose: bool, print messages during processing
        schema_path: str, if you wish to load the schema from local memory
        schema_url: str, if you wish to specify the path to the schema. schema_path takes precedence if populated. 
                    Check the object's `schema_url` attribute first 

        Return
        ------
        pd DataFrame of the parsed, structured VERIS data
        """

        raw_df = self._rawjson2dataframe(filenames, verbose)

        if keep_raw : self.raw_df = raw_df

        # load schema
        self.load_schema(schema_path, schema_url)

        # build the enumerations
        if verbose : print('Building DataFrame with enumerations.')
        #self.enumerations = self._build_enumerations_dict(self.vschema)

        enum_list = self._enums_from_schema(self.vschema, '', [])
        self.enumerations = {item['name']: item['enumlist'] for item in enum_list if 'enumlist' in item}
        self.nonenum_vars = [item for item in enum_list if 'enumlist' not in item]

        comb_df = self._combine_enums_raw_df(self.enumerations, self.nonenum_vars, raw_df)

        if verbose : print('Done building DataFrame with enumerations.')

        # add in A4 names
        if verbose: print('Post-Processing DataFrame (A4 Names, Victim Industries, Patterns)')
        comb_df = self._a4names(comb_df)

        # victim industries
        comb_df = self._victim_postproc(comb_df)

        # add in the breach "patterns"
        patterns = self.get_pattern(comb_df)
        comb_df = pd.concat([comb_df, patterns], axis=1)

        # sort columns alphabetically
        comb_df = comb_df.reindex(sorted(comb_df.columns), axis=1)

        if verbose: print('Finished building VERIS DataFrame')

        return comb_df


