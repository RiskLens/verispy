
import pandas as pd

def get_pattern(df):
    """ Generates the DBIR "patterns," with liberal inspiration from the verisr package: 
    https://github.com/vz-risk/verisr/blob/a293801eb92dda9668844f4f7be14bf5c685d764/R/matrix.R#L78

    Parameters
    ----------
    df: pd DataFrame with most VERIS encodings already built.


    Returns
    -------
    pd DataFrame with the patterns. Does not return as part of original VERIS DF.
    """
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

    # reduce names to single label (first one encountered)
    patterns_copy = patterns.copy()
    for col in patterns_copy.columns:
        patterns_copy[col] = patterns_copy[col].apply(lambda x: col if x else '')
    patterns_copy['pattern'] = patterns_copy.apply(lambda x: ','.join(x), axis = 1)
    def get_first(pats):
        pats = [pat for pat in pats.split(',') if len(pat) > 0]
        return pats[0]
    patterns_copy['pattern'] = patterns_copy['pattern'].apply(lambda x: get_first(x))

    # add 'pattern.' to the column names
    patterns.rename(columns = {col : ''.join(('pattern.', col)) for col in patterns.columns}, inplace=True)
    patterns['pattern'] = patterns_copy['pattern']

    return patterns




