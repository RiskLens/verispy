import pytest
import os
import glob
import pandas as pd
from ..veris import VERIS


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

	

