import csv
import glob
import pandas
from biothings.utils.dataload import list_split, dict_sweep, unlist, value_convert_to_number


VALID_COLUMN_NO = 187

'''this parser is for dbNSFP v3.3a beta2 downloaded from
https://sites.google.com/site/jpopgen/dbNSFP'''


# convert one snp to json
def _map_line_to_json(df, version, index=0):
    # specific variable treatment
    chrom = df.get_value(index, "#chr")
    if chrom == 'M':
        chrom = 'MT'
    # fields[7] in version 2, represent hg18_pos
    hg18_end = df.get_value(index, "hg18_pos(1-based)")
    if hg18_end == ".":
        hg18_end = "."
    else:
        hg18_end = int(hg18_end)
    # in case of no hg19 position provided, remove the item
    if df.get_value(index, "hg19_pos(1-based)") == '.':
        return None
    else:
        chromStart = int(df.get_value(index, "hg19_pos(1-based)"))
        chromEnd = chromStart
    chromStart_38 = int(df.get_value(index, "pos(1-based)"))
    ref = df.get_value(index, "ref").upper()
    alt = df.get_value(index, "alt").upper()
    HGVS_19 = "chr%s:g.%d%s>%s" % (chrom, chromStart, ref, alt)
    HGVS_38 = "chr%s:g.%d%s>%s" % (chrom, chromStart_38, ref, alt)
    if version == 'hg19':
        HGVS = HGVS_19
    elif version == 'hg38':
        HGVS = HGVS_38
    siphy_29way_pi = df.get_value(index, "SiPhy_29way_pi")
    if siphy_29way_pi == ".":
        siphy = "."
    else:
        freq = siphy_29way_pi.split(":")
        siphy = {'a': freq[0], 'c': freq[1], 'g': freq[2], 't': freq[3]}
    gtex_gene = df.get_value(index, "GTEx_V6_gene").split('|')
    gtex_tissue = df.get_value(index, "GTEx_V6_tissue").split('|')
    gtex = list(map(dict, map(lambda t: zip(('gene', 'tissue'), t), zip(gtex_gene, gtex_tissue))))
    acc = df.get_value(index, "Uniprot_acc_Polyphen2").rstrip().rstrip(';').split(";")
    pos = df.get_value(index, "Uniprot_aapos_Polyphen2").rstrip().rstrip(';').split(";")
    uniprot = list(map(dict, map(lambda t: zip(('acc', 'pos'), t), zip(acc, pos))))
    provean_score = df.get_value(index, "PROVEAN_score").split(';')
    sift_score = df.get_value(index, "SIFT_score").split(';')
    hdiv_score = df.get_value(index, "Polyphen2_HDIV_score").split(';')
    hvar_score = df.get_value(index, "Polyphen2_HVAR_score").split(';')
    lrt_score = df.get_value(index, "LRT_score").split(';')
    m_cap_score = df.get_value(index, "M-CAP_score").split(';')
    mutationtaster_score = df.get_value(index, "MutationTaster_score").split(';')
    mutationassessor_score = df.get_value(index, "MutationAssessor_score").split(';')
    vest3_score = df.get_value(index, "VEST3_score").split(';')
    metasvm_score = df.get_value(index, "MetaSVM_score").split(';')
    fathmm_score = df.get_value(index, "FATHMM_score").split(';')
    metalr_score = df.get_value(index, "MetaLR_score").split(';')
    modify_score_list = [provean_score, sift_score, hdiv_score, hvar_score, lrt_score,
                         m_cap_score, mutationtaster_score, mutationassessor_score,
                         vest3_score, metasvm_score, fathmm_score, metalr_score]
    for _score in modify_score_list:
        [None if item == '.' else item for item in _score]

# load as json data
    one_snp_json = {
        "_id": HGVS,
        "dbnsfp": {
            "rsid": df.get_value(index, "rs_dbSNP147"),
            #"rsid_dbSNP144": fields[6],
            "chrom": chrom,
            "hg19": {
                "start": chromStart,
                "end": chromEnd
            },
            "hg18": {
                "start": df.get_value(index, "hg18_pos(1-based)"),
                "end": hg18_end
            },
            "hg38": {
                "start": df.get_value(index, "pos(1-based)"),
                "end": df.get_value(index, "pos(1-based)")
            },
            "ref": ref,
            "alt": alt,
            "aa": {
                "ref": df.get_value(index, "aaref"),
                "alt": df.get_value(index, "aaalt"),
                "pos": df.get_value(index, "aapos"),
                "refcodon": df.get_value(index, "refcodon"),
                "codonpos": df.get_value(index, "codonpos"),
                "codon_degeneracy": df.get_value(index, "codon_degeneracy"),
            },
            "genename": df.get_value(index, "genename"),
            "uniprot": uniprot,
            "interpro_domain": df.get_value(index, "Interpro_domain"),
            "cds_strand": df.get_value(index, "cds_strand"),
            "ancestral_allele": df.get_value(index, "Ancestral_allele"),
            #"altaineandertal": fields[17],
            #"denisova": fields[18]
            "ensembl": {
                "geneid": df.get_value(index, "Ensembl_geneid"),
                "transcriptid": df.get_value(index, "Ensembl_transcriptid"),
                "proteinid": df.get_value(index, "Ensembl_proteinid")
            },
            "sift": {
                "score": sift_score,
                "converted_rankscore": df.get_value(index, "SIFT_converted_rankscore"),
                "pred": df.get_value(index, "SIFT_pred")
            },
            "polyphen2": {
                "hdiv": {
                    "score": hdiv_score,
                    "rankscore": df.get_value(index, "Polyphen2_HDIV_rankscore"),
                    "pred": df.get_value(index, "Polyphen2_HDIV_pred")
                },
                "hvar": {
                    "score": hvar_score,
                    "rankscore": df.get_value(index, "Polyphen2_HVAR_rankscore"),
                    "pred": df.get_value(index, "Polyphen2_HVAR_pred")
                }
            },
            "lrt": {
                "score": lrt_score,
                "converted_rankscore": df.get_value(index, "LRT_converted_rankscore"),
                "pred": df.get_value(index, "LRT_pred"),
                "omega": df.get_value(index, "LRT_Omega")
            },
            "mutationtaster": {
                "score": mutationtaster_score,
                "converted_rankscore": df.get_value(index, "MutationTaster_converted_rankscore"),
                "pred": df.get_value(index, "MutationTaster_pred"),
                "model": df.get_value(index, "MutationTaster_model"),
                "AAE": df.get_value(index, "MutationTaster_AAE")
            },
            "mutationassessor": {
                "score": mutationassessor_score,
                "rankscore": df.get_value(index, "MutationAssessor_score_rankscore"),
                "pred": df.get_value(index, "MutationAssessor_pred")
            },
            "fathmm": {
                "score": fathmm_score,
                "rankscore": df.get_value(index, "FATHMM_converted_rankscore"),
                "pred": df.get_value(index, "FATHMM_pred")
            },
            "provean": {
                "score": provean_score,
                "rankscore": df.get_value(index, "PROVEAN_converted_rankscore"),
                "pred": df.get_value(index, "PROVEAN_pred")
            },
            "vest3": {
                "score": vest3_score,
                "rankscore": df.get_value(index, "VEST3_rankscore"),
                "transcriptid": df.get_value(index, "Transcript_id_VEST3"),
                "transcriptvar": df.get_value(index, "Transcript_var_VEST3")
            },
            "fathmm-mkl": {
                "coding_score": df.get_value(index, "fathmm-MKL_coding_score"),
                "coding_rankscore": df.get_value(index, "fathmm-MKL_coding_rankscore"),
                "coding_pred": df.get_value(index, "fathmm-MKL_coding_pred"),
                "coding_group": df.get_value(index, "fathmm-MKL_coding_group")
            },
            "eigen": {
                "coding_or_noncoding": df.get_value(index, "Eigen_coding_or_noncoding"),
                "raw": df.get_value(index, "Eigen-raw"),
                "phred": df.get_value(index, "Eigen-phred")
            },
            "eigen-pc": {
                "raw": df.get_value(index, "Eigen-PC-raw"),
                "phred": df.get_value(index, "Eigen-PC-phred"),
                "raw_rankscore": df.get_value(index, "Eigen-PC-raw_rankscore")
            },
            "genocanyon": {
                "score": df.get_value(index, "GenoCanyon_score"),
                "rankscore": df.get_value(index, "GenoCanyon_score_rankscore")
            },
            "metasvm": {
                "score": metasvm_score,
                "rankscore": df.get_value(index, "MetaSVM_rankscore"),
                "pred": df.get_value(index, "MetaSVM_pred")
            },
            "metalr": {
                "score": metalr_score,
                "rankscore": df.get_value(index, "MetaLR_rankscore"),
                "pred": df.get_value(index, "MetaLR_pred")
            },
            "reliability_index": df.get_value(index, "Reliability_index"),
            "m_cap_score": {
                "score": m_cap_score,
                "rankscore": df.get_value(index, "M-CAP_rankscore"),
                "pred": df.get_value(index, "M-CAP_pred")
            },
            "dann": {
                "score": df.get_value(index, "DANN_score"),
                "rankscore": df.get_value(index, "DANN_rankscore")
            },
            "gerp++": {
                "nr": df.get_value(index, "GERP++_NR"),
                "rs": df.get_value(index, "GERP++_RS"),
                "rs_rankscore": df.get_value(index, "GERP++_RS_rankscore")
            },
            "integrated": {
                "fitcons_score": df.get_value(index, "integrated_fitCons_score"),
                "fitcons_rankscore": df.get_value(index, "integrated_fitCons_score_rankscore"),
                "confidence_value": df.get_value(index, "integrated_confidence_value")
            },
            "gm12878": {
                "fitcons_score": df.get_value(index, "GM12878_fitCons_score"),
                "fitcons_rankscore": df.get_value(index, "GM12878_fitCons_score_rankscore"),
                "confidence_value": df.get_value(index, "GM12878_confidence_value")
            },
            "h1-hesc": {
                "fitcons_score": df.get_value(index, "H1-hESC_fitCons_score"),
                "fitcons_rankscore": df.get_value(index, "H1-hESC_fitCons_score_rankscore"),
                "confidence_value": df.get_value(index, "H1-hESC_confidence_value")
            },
            "huvec": {
                "fitcons_score": df.get_value(index, "HUVEC_fitCons_score"),
                "fitcons_rankscore": df.get_value(index, "HUVEC_fitCons_score_rankscore"),
                "confidence_value": df.get_value(index, "HUVEC_confidence_value")
            },
            "phylo": {
                "p100way": {
                    "vertebrate": df.get_value(index, "phyloP100way_vertebrate"),
                    "vertebrate_rankscore": df.get_value(index, "phyloP100way_vertebrate_rankscore")
                },
                "p20way": {
                    "mammalian": df.get_value(index, "phyloP20way_mammalian"),
                    "mammalian_rankscore": df.get_value(index, "phyloP20way_mammalian_rankscore")
                }
            },
            "phastcons": {
                "100way": {
                    "vertebrate": df.get_value(index, "phastCons100way_vertebrate"),
                    "vertebrate_rankscore": df.get_value(index, "phastCons100way_vertebrate_rankscore")
                },
                "20way": {
                    "mammalian": df.get_value(index, "phastCons20way_mammalian"),
                    "mammalian_rankscore": df.get_value(index, "phastCons20way_mammalian_rankscore")
                }
            },
            "siphy_29way": {
                "pi": siphy,
                "logodds": df.get_value(index, "SiPhy_29way_logOdds"),
                "logodds_rankscore": df.get_value(index, "SiPhy_29way_logOdds_rankscore")
            },
            "1000gp3": {
                "ac": df.get_value(index, "1000Gp3_AC"),
                "af": df.get_value(index, "1000Gp3_AF"),
                "afr_ac": df.get_value(index, "1000Gp3_AFR_AC"),
                "afr_af": df.get_value(index, "1000Gp3_AFR_AF"),
                "eur_ac": df.get_value(index, "1000Gp3_EUR_AC"),
                "eur_af": df.get_value(index, "1000Gp3_EUR_AF"),
                "amr_ac": df.get_value(index, "1000Gp3_AMR_AC"),
                "amr_af": df.get_value(index, "1000Gp3_AMR_AF"),
                "eas_ac": df.get_value(index, "1000Gp3_EAS_AC"),
                "eas_af": df.get_value(index, "1000Gp3_EAS_AF"),
                "sas_ac": df.get_value(index, "1000Gp3_SAS_AC"),
                "sas_af": df.get_value(index, "1000Gp3_SAS_AF")
            },
            "twinsuk": {
                "ac": df.get_value(index, "TWINSUK_AC"),
                "af": df.get_value(index, "TWINSUK_AF")
            },
            "alspac": {
                "ac": df.get_value(index, "ALSPAC_AC"),
                "af": df.get_value(index, "ALSPAC_AF")
            },
            "esp6500": {
                "aa_ac": df.get_value(index, "ESP6500_AA_AC"),
                "aa_af": df.get_value(index, "ESP6500_AA_AF"),
                "ea_ac": df.get_value(index, "ESP6500_EA_AC"),
                "ea_af": df.get_value(index, "ESP6500_EA_AF")
            },
            "exac": {
                "ac": df.get_value(index, "ExAC_AC"),
                "af": df.get_value(index, "ExAC_AF"),
                "adj_ac": df.get_value(index, "ExAC_Adj_AC"),
                "adj_af": df.get_value(index, "ExAC_Adj_AF"),
                "afr_ac": df.get_value(index, "ExAC_AFR_AC"),
                "afr_af": df.get_value(index, "ExAC_AFR_AF"),
                "amr_ac": df.get_value(index, "ExAC_AMR_AC"),
                "amr_af": df.get_value(index, "ExAC_AMR_AF"),
                "eas_ac": df.get_value(index, "ExAC_EAS_AC"),
                "eas_af": df.get_value(index, "ExAC_EAS_AF"),
                "fin_ac": df.get_value(index, "ExAC_FIN_AC"),
                "fin_af": df.get_value(index, "ExAC_FIN_AF"),
                "nfe_ac": df.get_value(index, "ExAC_NFE_AC"),
                "nfe_af": df.get_value(index, "ExAC_NFE_AF"),
                "sas_ac": df.get_value(index, "ExAC_SAS_AC"),
                "sas_af": df.get_value(index, "ExAC_SAS_AF")
            },
            "exac_nontcga": {
                "ac": df.get_value(index, "ExAC_nonTCGA_AC"),
                "af": df.get_value(index, "ExAC_nonTCGA_AF"),
                "adj_ac": df.get_value(index, "ExAC_nonTCGA_Adj_AC"),
                "adj_af": df.get_value(index, "ExAC_nonTCGA_Adj_AF"),
                "afr_ac": df.get_value(index, "ExAC_nonTCGA_AFR_AC"),
                "afr_af": df.get_value(index, "ExAC_nonTCGA_AFR_AF"),
                "amr_ac": df.get_value(index, "ExAC_nonTCGA_AMR_AC"),
                "amr_af": df.get_value(index, "ExAC_nonTCGA_AMR_AF"),
                "eas_ac": df.get_value(index, "ExAC_nonTCGA_EAS_AC"),
                "eas_af": df.get_value(index, "ExAC_nonTCGA_EAS_AF"),
                "fin_ac": df.get_value(index, "ExAC_nonTCGA_FIN_AC"),
                "fin_af": df.get_value(index, "ExAC_nonTCGA_FIN_AF"),
                "nfe_ac": df.get_value(index, "ExAC_nonTCGA_NFE_AC"),
                "nfe_af": df.get_value(index, "ExAC_nonTCGA_NFE_AF"),
                "sas_ac": df.get_value(index, "ExAC_nonTCGA_SAS_AC"),
                "sas_af": df.get_value(index, "ExAC_nonTCGA_SAS_AF")
            },
            "exac_nonpsych": {
                "ac": df.get_value(index, "ExAC_nonpsych_AC"),
                "af": df.get_value(index, "ExAC_nonpsych_AF"),
                "adj_ac": df.get_value(index, "ExAC_nonpsych_Adj_AC"),
                "adj_af": df.get_value(index, "ExAC_nonpsych_Adj_AF"),
                "afr_ac": df.get_value(index, "ExAC_nonpsych_AFR_AC"),
                "afr_af": df.get_value(index, "ExAC_nonpsych_AFR_AF"),
                "amr_ac": df.get_value(index, "ExAC_nonpsych_AMR_AC"),
                "amr_af": df.get_value(index, "ExAC_nonpsych_AMR_AF"),
                "eas_ac": df.get_value(index, "ExAC_nonpsych_EAS_AC"),
                "eas_af": df.get_value(index, "ExAC_nonpsych_EAS_AF"),
                "fin_ac": df.get_value(index, "ExAC_nonpsych_FIN_AC"),
                "fin_af": df.get_value(index, "ExAC_nonpsych_FIN_AF"),
                "nfe_ac": df.get_value(index, "ExAC_nonpsych_NFE_AC"),
                "nfe_af": df.get_value(index, "ExAC_nonpsych_NFE_AF"),
                "sas_ac": df.get_value(index, "ExAC_nonpsych_SAS_AC"),
                "sas_af": df.get_value(index, "ExAC_nonpsych_SAS_AF")
            },
            "clinvar": {
                "rs": df.get_value(index, "clinvar_rs"),
                "clinsig": df.get_value(index, "clinvar_clnsig"),
                "trait": df.get_value(index, "clinvar_trait"),
                "golden_stars": df.get_value(index, "clinvar_golden_stars")
            },
            "gtex": gtex
        }
    }

    one_snp_json = list_split(dict_sweep(unlist(value_convert_to_number(one_snp_json)), vals=["."]), ";")
    one_snp_json["dbnsfp"]["chrom"] = str(one_snp_json["dbnsfp"]["chrom"])
    return one_snp_json


# open file, parse, pass to json mapper
def data_generator(input_file, version):
    open_file = open(input_file)
    db_nsfp = csv.reader(open_file, delimiter="\t")
    index = next(db_nsfp)
    assert len(index) == VALID_COLUMN_NO
    previous_row = None
    for row in db_nsfp:
        df = pandas.DataFrame(row,index=index)
        # use transpose matrix to have 1 row with N 187 columns
        current_row = _map_line_to_json(df.T, version=version)
        if previous_row and current_row:
            if current_row["_id"] == previous_row["_id"]:
                aa = previous_row["dbnsfp"]["aa"]
                if not isinstance(aa, list):
                    aa = [aa]
                aa.append(current_row["dbnsfp"]["aa"])
                previous_row["dbnsfp"]["aa"] = aa
                if len(previous_row["dbnsfp"]["aa"]) > 1:
                    continue
            else:
                yield previous_row
        previous_row = current_row
    if previous_row:
        yield previous_row


def load_data_file(input_file, version):
    data = data_generator(input_file, version=version)
    for one_snp_json in data:
        yield one_snp_json


# load path and find files, pass to data_generator
def load_data(path_glob, version='hg19'):
    todo = sorted(glob.glob(path_glob))
    for input_file in sorted(glob.glob(path_glob)):
        return load_data_file(input_file,version)

