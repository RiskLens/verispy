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
        raw_df = v._rawjson_to_df(fnames[:num_files])
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
        raw_df = v._rawjson_to_df(fnames)
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


    def test_aggregate_a4s(self):
        # from here out, just going to run the json_to_df procedure and then test individual func results
        v = VERIS()
        fnames = glob.glob(os.path.join(os.path.dirname(__file__), 'data', '*json'))
        comb_df = v.json_to_df(fnames)

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
        comb_df = v.json_to_df(fnames)

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

    def test_enum_summary(self):

        v = VERIS(json_dir=os.path.join(os.path.dirname(__file__), 'data'))
        comb_df = v.json_to_df() 

        # action enumeration should have 8 rows, 4 columns first of which is "Error"
        action_ci = v.enum_summary(comb_df, 'action')
        assert action_ci.shape == (8, 4)
        assert action_ci['enum'].iloc[0] == 'Error'
        assert action_ci['enum'].iloc[-1] == 'Unknown'

        # if use_unk, the n will be greater than without
        action_ci_unk = v.enum_summary(comb_df, 'action', use_unk=True)
        assert action_ci_unk.shape == action_ci.shape
        assert action_ci_unk['n'].iloc[0] > action_ci['n'].iloc[0]

        # asking for a column that doesn't exist gives back a df of 0 length
        donuts_ci = v.enum_summary(comb_df, 'mmm_donuts')
        assert donuts_ci.shape == (0, 4)

        # test the "by" keyword
        by_ci = v.enum_summary(comb_df, 'action', 'actor')
        assert by_ci.shape == (32, 5)
        assert by_ci['by'].iloc[0] == 'actor.External'
        assert by_ci['enum'].iloc[0] == 'Hacking'

        # test the "wilson" method
        wilson = v.enum_summary(comb_df, 'action', 'actor', ci_method='wilson')
        assert wilson.shape == (32, 8)
        assert wilson['freq'].iloc[0] < wilson['upper'].iloc[0]
        assert wilson['freq'].iloc[0] > wilson['lower'].iloc[0]
        wilson05 = v.enum_summary(comb_df, 'action', 'actor', ci_method='wilson', ci_level=0.5)
        assert wilson['upper'].iloc[0] > wilson05['upper'].iloc[0]  # bounds will be wider with first ci_level of 0.95
        assert wilson['lower'].iloc[0] < wilson05['lower'].iloc[0]

        # nonsensical ci_method should raise error
        with pytest.raises(NotImplementedError, match=r'donuts'):
            v.enum_summary(comb_df, 'action', 'actor', ci_method='donuts')

    def test_plot_barchart(self):

        v = VERIS(json_dir=os.path.join(os.path.dirname(__file__), 'data'))
        comb_df = v.json_to_df() 

        # use this enumeration df:
        action_ci = v.enum_summary(comb_df, 'action')

        # test we get an object back (need to figure out how to test this. as long as it doesn't fail I guess it's ok)
        plot = v.plot_barchart(action_ci)

        # passing in the original df gives a KeyError
        with pytest.raises(KeyError, match=r'enum'):
            v.plot_barchart(comb_df)

        # ok to pass in matplotlib keys:
        v.plot_barchart(action_ci, edgecolor='blue')
        v.plot_barchart(action_ci, title='Man Yells at Cloud', fill='yellow')

        # bad matplotlib keys throw error
        with pytest.raises(AttributeError, match=r'abe_simpson'):
            v.plot_barchart(action_ci, abe_simpson='yelling_at_clouds')


