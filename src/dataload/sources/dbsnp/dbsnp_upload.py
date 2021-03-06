import itertools, glob, os

from .dbsnp_dump import main as download
from .dbsnp_vcf_parser import load_data
import biothings.dataload.uploader as uploader
from dataload.uploader import SnpeffPostUpdateUploader


SRC_META = {
        "url" : "https://www.ncbi.nlm.nih.gov/projects/SNP/",
        "license_url" : "https://www.ncbi.nlm.nih.gov/home/about/policies/",
        "license_url_short": "https://goo.gl/Ztr5rl"
        }


class DBSNPBaseUploader(uploader.IgnoreDuplicatedSourceUploader,
                    uploader.ParallelizedSourceUploader,
                    SnpeffPostUpdateUploader):

    def jobs(self):
        files = glob.glob(os.path.join(self.data_folder,self.__class__.GLOB_PATTERN))
        if len(files) != 1:
            raise uploader.ResourceError("Expected 1 files, got: %s" % files)
        chrom_list = [str(i) for i in range(1, 23)] + ['X', 'Y', 'MT']
        return list(itertools.product(files,chrom_list))

    def load_data(self,input_file,chrom):
        self.logger.info("Load data from '%s' for chr %s" % (input_file,chrom))
        return load_data(self.__class__.__metadata__["assembly"],input_file,chrom)

    @classmethod
    def get_mapping(klass):
        mapping = {
            "dbsnp": {
                "properties": {
                    "allele_origin": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "alt": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "chrom": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "class": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "flags": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "gmaf": {
                        "type": "float"
                    },
                    klass.__metadata__["assembly"]: {
                        "properties": {
                            "end": {
                                "type": "integer"
                            },
                            "start": {
                                "type": "integer"
                            }
                        }
                    },
                    "ref": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "rsid": {
                        "type": "string",
                        "include_in_all": True,
                        "analyzer": "string_lowercase"
                    },
                    "var_subtype": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "vartype": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "validated": {
                        "type": "boolean"
                    },
                    "gene": {
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "analyzer": "string_lowercase",
                                "include_in_all": True
                            },
                            "geneid": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            }
                        }
                    }
                }
            }
        }
        return mapping


class DBSNPHg19Uploader(DBSNPBaseUploader):

    main_source = "dbsnp"
    name = "dbsnp_hg19"
    __metadata__ = {
            "mapper" : 'observed',
            "assembly" : "hg19",
            "src_meta" : SRC_META
            }
    GLOB_PATTERN = "human_9606_*_GRCh37*/VCF/*.vcf.gz"

    def post_update_data(self, *args, **kwargs):
        super(DBSNPBaseUploader,self).post_update_data(*args,**kwargs)
        self.logger.info("Indexing 'rsid'")
        # background=true or it'll lock the whole database...
        self.collection.create_index("dbsnp.rsid",background=True)


class DBSNPHg38Uploader(DBSNPBaseUploader):

    main_source = "dbsnp"
    name = "dbsnp_hg38"
    __metadata__ = {
            "mapper" : 'observed',
            "assembly" : "hg38",
            "src_meta" : SRC_META
            }
    GLOB_PATTERN = "human_9606_*_GRCh38*/VCF/*.vcf.gz"

