import pytest
import os
import glob
import pandas as pd
from ..veris import VERIS
from ..utils import industry as industry_const
from ..utils import constants as veris_const


class Test_VERIS(object):

    def test_load_schema(self):
        v = VERIS()
        v.load_schema(schema_path=os.path.join(os.path.dirname(__file__), 'data', 'schema', 'verisc-merged.json'))
        assert type(v.vschema) is dict

    def test_load_raw_data(self):
        v = VERIS()
        fnames = glob.glob(os.path.join(os.path.dirname(__file__), 'data', '*json'))
        num_files = 10
        raw_df = v._rawjson2dataframe(fnames[:num_files])
        assert type(raw_df) is pd.DataFrame
        assert raw_df.shape == (num_files, 85)

    def test_schema_enumerations(self):
        v = VERIS()
        v.load_schema(schema_path=os.path.join(os.path.dirname(__file__), 'data', 'schema', 'verisc-merged.json'))
        enum_list = v._enums_from_schema(v.vschema)
        assert type(enum_list) is list
        assert len(enum_list) > 100 # this will change over time, don't want to lock this in

        enumerations = {item['name']: item['enumlist'] for item in enum_list if 'enumlist' in item}
        nonenum_vars = [item for item in enum_list if 'enumlist' not in item]

        assert type(nonenum_vars[0]) is dict
        assert type(enumerations['action.error.variety']) is list
        assert len(enumerations['action.error.variety']) >= 15

    def test_combine_enums_raw_df(self):
        v = VERIS()
        fnames = glob.glob(os.path.join(os.path.dirname(__file__), 'data', '*json'))
        raw_df = v._rawjson2dataframe(fnames)
        v.load_schema(schema_path=os.path.join(os.path.dirname(__file__), 'data', 'schema', 'verisc-merged.json'))
        enum_list = v._enums_from_schema(v.vschema)

        v.enumerations = {item['name']: item['enumlist'] for item in enum_list if 'enumlist' in item}
        v.nonenum_vars = [item for item in enum_list if 'enumlist' not in item]

        comb_df = v._combine_enums_raw_df(v.enumerations, v.nonenum_vars, raw_df)

        assert comb_df.shape[0] == raw_df.shape[0]
        assert comb_df.shape[1] > raw_df.shape[1] 

        # make sure all enumeration variables are in the df and are all booleans
        enum_vars = ['.'.join((name, suff)) for name, suffixes in v.enumerations.items() for suff in suffixes]
        comb_df_cols = comb_df.columns
        for var in enum_vars:
            assert var in enum_vars
            if 'amount' not in var:  # all enumerations except the amount ones will be boolean
                assert comb_df[var].dtype == bool
            else:  # amounts might be objects or floats
                assert comb_df[var].dtype in ['object', 'float']

        # the non-enumeration variables should also all be in the dataframe
        for item in v.nonenum_vars:
            itemname = item['name']
            itemtype = item['type']
            assert item['name'] in comb_df_cols
            if itemtype == 'string':
                assert comb_df[itemname].dtype == 'object'
            elif itemtype == 'number' or itemtype == 'float':
                assert comb_df[itemname].dtype in ['float', 'int']


    def test_a4_names(self):
        # from here out, just going to run the json2dataframe procedure and then test individual func results
        v = VERIS()
        fnames = glob.glob(os.path.join(os.path.dirname(__file__), 'data', '*json'))
        comb_df = v.json2dataframe(fnames)

        # test a few A4 names
        hacking_sum = comb_df[[col for col in comb_df.columns if col.startswith('action.hacking')]].sum(axis=1)
        hacking_sum = hacking_sum.apply(lambda x: True if x >= 1 else False)
        assert comb_df['action.Hacking'].sum(axis=0) == hacking_sum.sum(axis=0)
        assert comb_df['action.Hacking'].all() == hacking_sum.all()

        actor_int_sum = comb_df[[col for col in comb_df.columns if col.startswith('actor.internal')]].sum(axis=1)
        actor_int_sum = actor_int_sum.apply(lambda x: True if x >= 1 else False)
        assert comb_df['actor.Internal'].sum(axis=0) == actor_int_sum.sum(axis=0)
        assert comb_df['actor.Internal'].all() == actor_int_sum.all()

        integrity_sum = comb_df[[col for col in comb_df.columns \
                                 if col.startswith('attribute.integrity.variety')]].sum(axis=1)
        integrity_sum = integrity_sum.apply(lambda x: True if x >= 1 else False)
        assert comb_df['attribute.Integrity'].sum(axis=0) == integrity_sum.sum(axis=0)
        assert comb_df['attribute.Integrity'].all() == integrity_sum.all()

        # test the unknowns
        # actor unknown
        actor_a4s = ['.'.join(('actor', suffix)) for suffix in veris_const.A4NAMES['actor'] if suffix != 'Unknown']
        actor_a4s_sum = comb_df[actor_a4s].sum(axis=1)
        actor_a4s_sum = actor_a4s_sum.apply(lambda x: True if x >= 1 else False)
        assert comb_df['actor.Unknown'].all() == (~actor_a4s_sum).all()

        # action unknown
        action_a4s = ['.'.join(('action', suffix)) for suffix in veris_const.A4NAMES['action'] if suffix != 'Unknown']
        action_a4s_sum = comb_df[action_a4s].sum(axis=1)
        action_a4s_sum = action_a4s_sum.apply(lambda x: True if x >= 1 else False)
        assert comb_df['action.Unknown'].all() == (~action_a4s_sum).all()

    def test_victim_industries(self):
        v = VERIS()
        fnames = glob.glob(os.path.join(os.path.dirname(__file__), 'data', '*json'))
        comb_df = v.json2dataframe(fnames)

        # are all victim industries represented?
        industry2s = ['.'.join(('victim.industry2', ind['code'])) for ind in industry_const.INDUSTRY_LONG]
        colnames = comb_df.columns
        for industry2 in industry2s:
            assert industry2 in colnames

        # for all industry2s, is there only one (can't be more than one industry)
        industry_2_sums = comb_df[industry2s].sum(axis=1)
        assert industry_2_sums.all() == 1

        # did the 2- and 3-digit codes survive?
        assert comb_df['victim.industry2'].all() == \
               comb_df['victim.industry'].apply(lambda x: str(x)[:2] if not pd.isnull(x) else None).all()

        assert comb_df['victim.industry3'].all() == \
               comb_df['victim.industry'].apply(lambda x: str(x)[:3] if not pd.isnull(x) else None).all()

    def test_patterns(self):
        v = VERIS()
        fnames = glob.glob(os.path.join(os.path.dirname(__file__), 'data', '*json'))
        comb_df = v.json2dataframe(fnames)
        colnames = comb_df.columns
        pattern_df = v.get_pattern(comb_df)

        pattern_cols_req = ['Point of Sale', 'Web Applications', 'Privilege Misuse', 'Lost and Stolen Assets', \
                            'Miscellaneous Errors', 'Crimeware', 'Payment Card Skimmers', 'Denial of Service', \
                            'Cyber-Espionage', 'Everything Else']
        pattern_cols_full = ['.'.join(('pattern', pat)) for pat in pattern_cols_req] + ['pattern']


        for col in pattern_df.columns:
            assert col in colnames
            assert col in pattern_cols_full
            assert pattern_df[col].all() == comb_df[col].all()

        assert pattern_df['pattern'].all() in pattern_cols_req

        assert comb_df[pattern_cols_full].sum(axis=1).all() >= 1
        assert comb_df['pattern'].all() == comb_df['pattern'].all()







