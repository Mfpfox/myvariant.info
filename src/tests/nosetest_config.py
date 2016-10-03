###################################################################################
# Nosetest settings
###################################################################################
from tests import variant_list

# biothings specific options - these should be identical to the production server 
# you are testing for...  For example, JSONLD_CONTEXT_PATH should point to a file
# with contents identical to the file pointed to by JSONLD_CONTEXT_PATH on the 
# production server (if your intention is to test the production server).
JSONLD_CONTEXT_URL = "http://myvariant.info/context/context.json"
API_VERSION = "v1"
QUERY_ENDPOINT = "query"
ANNOTATION_ENDPOINT = "variant"

# This is the name of the environment variable to load for testing
HOST_ENVAR_NAME = 'MV_HOST'
# This is the URL of the production server, if the above envar can't be loaded, nosetest defaults to this
NOSETEST_DEFAULT_URL = "http://myvariant.info"

###################################################################################
# Nosetests used in tests.py, fill these in with IDs/queries.
###################################################################################

# This is the test for fields in the annotation object.  You should pick an ID
# with a representative set of root level annotations associated with it.
ANNOTATION_OBJECT_ID = 'chr6:g.152708291G>A'
# This is the list of expected keys that the JSON object returned by the ID above
ANNOTATION_OBJECT_EXPECTED_ATTRIBUTE_LIST = ['_id', '_version', 'cadd', 'clinvar', 'cosmic', 'dbsnp', 'exac']

# -----------------------------------------------------------------------------------

# This is a list of IDs (& options) to test a GET to the annotation endpoint
ANNOTATION_GET_IDS = ['chr6:g.152708291G>A', 
                      'chr6:g.152708291G>A?fields=cadd&callback=mycallback', 
                      'chr6:g.152708291G>A?fields=cadd,clinvar.hg19,clinvar.hg38,exac.ac.ac', 
                      'chr6:g.152708291G>A?jsonld=true',
                      'chr6:g.152708291G>A?fields=cadd,clinvar.hg19,clinvar.hg38,exac.ac.ac&jsonld=true'
                     ] 

# -----------------------------------------------------------------------------------

# This is a list of dictionaries to test a POST to the annotation endpoint

ANNOTATION_POST_DATA = [{'ids': 'chr16:g.28883241A>G'},
                        {'ids': 'chr16:g.28883241A>G, chr11:g.66397320A>G'},
                        {'ids': 'chr16:g.28883241A>G, chr11:g.66397320A>G', 'fields': 'dbsnp'},
                        {'ids': variant_list.VARIANT_POST_LIST},
                        {'ids': 'chr16:g.28883241A>G, chr11:g.66397320A>G', 'jsonld': 'true'}
                        ]

# -----------------------------------------------------------------------------------

# This is a list of query strings (& options to test a GET to the query endpoint
QUERY_GETS = ['rs58991260',
              '_exists_:wellderly%20AND%20cadd.polyphen.cat:possibly_damaging&fields=wellderly,cadd.polyphen',
              'clinvar.chrom:"10"&fields=clinvar&callback=mycallback',
              'clinvar.chrom:"10"&fields=clinvar&fetch_all=true',
              'clinvar.chrom:"10"&fields=clinvar&facets=clinvar.chrom',
              'clinvar.chrom:"10"&fields=clinvar&size=2000',
              'clinvar.chrom:"10"&fields=clinvar&jsonld=true'
              ]
              

# -----------------------------------------------------------------------------------

# This is a list of dictionaries to test a POST to the query endpoint
QUERY_POST_DATA = [{'q': 'rs58991260', 'scopes': 'dbsnp.rsid'},
                   {'q': 'rs58991260', 'scopes': 'dbsnp.rsid', 'fields': 'dbsnp'},
                   {'q': 'rs58991260,rs2500', 'scopes': 'dbsnp.rsid', 'fields': 'dbsnp', 'jsonld': 'true'} 
                  ]

# -----------------------------------------------------------------------------------

# This is the minimum number of unique field keys (from /metadata/fields)
MINIMUM_NUMBER_OF_ACCEPTABLE_FIELDS = 480

# -----------------------------------------------------------------------------------

# This is the minimum number of unique field keys (from /metadata/fields)
TEST_FIELDS_GET_FIELDS_ENDPOINT = ['cadd', 'dbnsfp', 'dbsnp', 'wellderly', 'clinvar']

# -----------------------------------------------------------------------------------

# Any additional fields added for check_fields subset test
CHECK_FIELDS_SUBSET_ADDITIONAL_FIELDS = ['cadd._license']
