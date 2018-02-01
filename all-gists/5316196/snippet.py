from path import path
import pandas as pd

allActors = ['AFG', 'ALA', 'ALB', 'DZA', 'ASM', 'AND', 'AGO', 'AIA', 'ATG', 
            'ARG', 'ARM', 'ABW', 'AUS', 'AUT', 'AZE', 'BHS', 'BHR', 'BGD', 
            'BRB', 'BLR', 'BEL', 'BLZ', 'BEN', 'BMU', 'BTN', 'BOL', 'BIH', 
            'BWA', 'BRA', 'VGB', 'BRN', 'BGR', 'BFA', 'BDI', 'KHM', 'CMR',
            'CAN', 'CPV', 'CYM', 'CAF', 'TCD', 'CHL', 'CHN', 'COL', 'COM', 
            'COD', 'COG', 'COK', 'CRI', 'CIV', 'HRV', 'CUB', 'CYP', 'CZE', 
            'DNK', 'DJI', 'DMA', 'DOM', 'TMP', 'ECU', 'EGY', 'SLV', 'GNQ', 
            'ERI', 'EST', 'ETH', 'FRO', 'FLK', 'FJI', 'FIN', 'FRA', 'GUF',
            'PYF', 'GAB', 'GMB', 'GEO', 'DEU', 'GHA', 'GIB', 'GRC', 'GRL',
            'GRD', 'GLP', 'GUM', 'GTM', 'GIN', 'GNB', 'GUY', 'HTI', 'VAT', 
            'HND', 'HKG', 'HUN', 'ISL', 'IND', 'IDN', 'IRN', 'IRQ', 'IRL', 
            'IMY', 'ISR', 'ITA', 'JAM', 'JPN', 'JOR', 'KAZ', 'KEN', 'KIR',
            'PRK', 'KOR', 'KWT', 'KGZ', 'LAO', 'LVA', 'LBN', 'LSO', 'LBR', 
            'LBY', 'LIE', 'LTU', 'LUX', 'MAC', 'MKD', 'MDG', 'MWI', 'MYS',
            'MDV', 'MLI', 'MLT', 'MHL', 'MTQ', 'MRT', 'MUS', 'MYT', 'MEX',
            'FSM', 'MDA', 'MCO', 'MNG', 'MTN', 'MSR', 'MAR', 'MOZ', 'MMR',
            'NAM', 'NRU', 'NPL', 'NLD', 'ANT', 'NCL', 'NZL', 'NIC', 'NER',
            'NGA', 'NIU', 'NFK', 'MNP', 'NOR', 'PSE', 'OMN', 'PAK', 'PLW', 
            'PAN', 'PNG', 'PRY', 'PER', 'PHL', 'PCN', 'POL', 'PRT', 'PRI', 
            'QAT', 'REU', 'ROM', 'RUS', 'RWA', 'SHN', 'KNA', 'LCA', 'SPM', 
            'VCT', 'WSM', 'SMR', 'STP', 'SAU', 'SEN', 'SRB', 'SYC', 'SLE', 
            'SGP', 'SVK', 'SVN', 'SLB', 'SOM', 'ZAF', 'ESP', 'LKA', 'SDN',
            'SUR', 'SJM', 'SWZ', 'SWE', 'CHE', 'SYR', 'TJK', 'TZA', 'THA', 
            'TGO', 'TKL', 'TON', 'TTO', 'TUN', 'TUR', 'TKM', 'TCA', 'TUV',
            'UGA', 'UKR', 'ARE', 'GBR', 'USA', 'VIR', 'URY', 'UZB', 'VUT', 
            'VEN', 'VNM', 'WLF', 'ESH', 'YEM', 'ZMB', 'ZWE']

quad_codes = ['2', '3']

filepaths = path.getcwd().files('*.reduced.txt')
output = list()

for path in filepaths:
    data = open(path, 'r')
    print 'Just read in the %s data...' % path
    for line in data:
        line = line.replace('\n', '')
        split_line = line.split('\t')
        condition1 = split_line[1][0:3] == 'USA'
        condition2 = split_line[2][0:3] != 'USA'
        condition3 = split_line[2][0:3] in allActors
        condition4 = split_line[4] in quad_codes
        try:
            if all([condition1, condition2, condition3, condition4]):
                output.append(split_line)
        except IndexError:
            pass

header = open(filepaths[0], 'r').readline().split('\t')
subset = pd.DataFrame(output, columns = header)

subset['year'] = subset['Day'].str[0:4]
subset['month'] = subset['Day'].str[4:6]

keep_columns = ['year', 'month', 'Actor1Code', 'Actor2Code', 'QuadCategory']
subset = subset[keep_columns]

subset['verbal_coop'] = 0
subset['verbal_conf'] = 0

subset['verbal_coop'][subset['QuadCategory'] == '2'] = 1
subset['verbal_conf'][subset['QuadCategory'] == '3'] = 1

subset_grouped = subset.groupby(['year', 'month', 'Actor1Code',
'Actor2Code'], as_index = False)
subset_aggregated = subset_grouped.sum()

subset_aggregated.to_csv('gdelt_subset.csv', index = False)
