# function to figure out the DBIR "patterns," with liberal inspiration from the verisr package: https://github.com/vz-risk/verisr/blob/a293801eb92dda9668844f4f7be14bf5c685d764/R/matrix.R#L78
import pandas as pd

def get_pattern(df):

	skimmer = df['action.physical.variety.Skimmer'] | \
	          (df['action.physical.variety.Tampering'] & df['attribute.confidentiality.data.variety.Payment'])
	
	espionage = df['actor.external.motive.Espionage'] | df['actor.external.variety.State-affiliated']

	pos = df['asset.assets.variety.S - POS controller'] | df['asset.assets.variety.U - POS terminal']

	dos = df['action.hacking.variety.DoS']

	webapp = df['action.hacking.vector.Web application']
	webapp = webapp & ~(webapp & dos)

	misuse = df['action.Misuse']

	vfilter = skimmer | espionage | pos | dos | webapp | misuse

	mal_tmp = df['action.Malware'] & ~df['action.malware.vector.Direct install']
	malware = mal_tmp & ~vfilter

	theftloss = df['action.error.variety.Loss'] | df['action.physical.variety.Theft']

	vfilter = vfilter | malware | theftloss

	errors = df['action.Error'] & ~vfilter

	vfilter = vfilter | errors

	other = ~vfilter

	patterns = pd.DataFrame({
		'Point of Sale' : pos, 
		'Web Applications' : webapp,
		'Privilege Misuse' : misuse,
		'Lost and Stolen Assets' : theftloss,
		'Miscellaneous Errors' : errors,
		'Crimeware' : malware, 
		'Payment Card Skimmers' : skimmer,
		'Denial of Service' : dos, 
		'Cyber-Espionage' : espionage, 
		'Everything Else' : other
		})

	# finish here with: https://github.com/vz-risk/verisr/blob/master/R/matrix.R#L119

	return patterns




