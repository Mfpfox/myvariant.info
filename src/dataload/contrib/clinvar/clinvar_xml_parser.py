# Generated Mon Mar 30 11:14:08 2015 by generateDS.py version 2.15a.
# Command line:
#   /home/cwu/opt/devpy/bin/generateDS.py -o\
# "clinvar.py" -s "clinvarsubs.py" /home/cwu/Desktop/clinvar_public.xsd
import clinvar
from itertools import groupby

from utils.dataload import unlist, dict_sweep, \
    value_convert, rec_handler


def merge_rcv_accession(generator):
    groups = []
    for key, group in groupby(generator, lambda x: x['_id']):
        groups.append(list(group))

    # get the number of groups, and uniquekeys
    print "number of groups: ", len(groups), "\n"

    # loop through each item, if item number >1, merge rcv accession number
    for item in groups:
        rcv_new = []
        if len(item) > 1:
            json_item = item[0]
            for _item in item:
                    rcv_info = _item['clinvar']['rcv']
                    rcv_new.append(rcv_info)
            json_item['clinvar']['rcv'] = rcv_new
            yield json_item
        else:
            yield item[0]


def _map_line_to_json(cp, hg19):
    try:
        clinical_significance = cp.ReferenceClinVarAssertion.\
            ClinicalSignificance.Description
    except:
        clinical_significance = None
    rcv_accession = cp.ReferenceClinVarAssertion.ClinVarAccession.Acc
    try:
        review_status = cp.ReferenceClinVarAssertion.ClinicalSignificance.\
            ReviewStatus
    except:
        review_status = None
    try:
        last_evaluated = cp.ReferenceClinVarAssertion.ClinicalSignificance.\
            DateLastEvaluated
    except:
        last_evaluated = None
    variant_id = cp.ReferenceClinVarAssertion.MeasureSet.ID
    number_submitters = len(cp.ClinVarAssertion)
    # some items in clinvar_xml doesn't have origin information
    try:
        origin = cp.ReferenceClinVarAssertion.ObservedIn[0].Sample.Origin
    except:
        origin = None
    trait = cp.ReferenceClinVarAssertion.TraitSet.Trait[0]
    synonyms = []
    conditions_name = ''
    for name in trait.Name:
        if name.ElementValue.Type == 'Alternate':
            synonyms.append(name.ElementValue.get_valueOf_())
        if name.ElementValue.Type == 'Preferred':
            conditions_name += name.ElementValue.get_valueOf_()
    identifiers = {}
    for item in trait.XRef:
        if item.DB == 'Human Phenotype Ontology':
            key = 'Human_Phenotype_Ontology'
        else:
            key = item.DB
        identifiers[key.lower()] = item.ID
    for symbol in trait.Symbol:
        if symbol.ElementValue.Type == 'Preferred':
            conditions_name += ' (' + symbol.ElementValue.get_valueOf_() + ')'
    age_of_onset = ''
    for _set in trait.AttributeSet:
        if _set.Attribute.Type == 'age of onset':
            age_of_onset = _set.Attribute.get_valueOf_()

    # MeasureSet.Measure return a list, there might be multiple
    # Measure under one MeasureSet
    for Measure in cp.ReferenceClinVarAssertion.MeasureSet.Measure:
        variation_type = Measure.Type
        # exclude any item of which types belong to
        # 'Variation', 'protein only' or 'Microsatellite'
        if variation_type == 'Variation' or variation_type\
           == 'protein only' or variation_type == 'Microsatellite':
            continue
        allele_id = Measure.ID
        chrom = None
        chromStart_19 = None
        chromEnd_19 = None
        chromStart_38 = None
        chromEnd_38 = None
        ref = None
        alt = None
        if Measure.SequenceLocation:
            for SequenceLocation in Measure.SequenceLocation:
                # In this version, only accept information concerning GRCh37
                if 'GRCh37' in SequenceLocation.Assembly:
                    chrom = SequenceLocation.Chr
                    chromStart_19 = SequenceLocation.start
                    chromEnd_19 = SequenceLocation.stop
                    ref = SequenceLocation.referenceAllele
                    alt = SequenceLocation.alternateAllele
                if 'GRCh38' in SequenceLocation.Assembly:
                    chromStart_38 = SequenceLocation.start
                    chromEnd_38 = SequenceLocation.stop
                    if not ref:
                        ref = SequenceLocation.referenceAllele
                    if not alt:
                        alt = SequenceLocation.alternateAllele
        if Measure.MeasureRelationship:
            try:
                symbol = Measure.MeasureRelationship[0].\
                    Symbol[0].get_ElementValue().valueOf_
            except:
                symbol = None
            gene_id = Measure.MeasureRelationship[0].XRef[0].ID
        else:
            symbol = None
            gene_id = None
        if Measure.Name:
            name = Measure.Name[0].ElementValue.valueOf_
        else:
            name = None
        if len(Measure.CytogeneticLocation) == 1:
            cytogenic = Measure.CytogeneticLocation[0]
        else:
            cytogenic = Measure.CytogeneticLocation
        hgvs_coding = None
        hgvs_genome = None
        HGVS = {'genomic': [], 'coding': [], 'non-coding': [], 'protein': []}
        coding_hgvs_only = None
        hgvs_id = None
        if hg19:
            chromStart = chromStart_19
            chromEnd = chromEnd_19
        else:
            chromStart = chromStart_38
            chromEnd = chromEnd_38
        # hgvs_not_validated = None
        if Measure.AttributeSet:
            # 'copy number loss' or 'gain' have format different\
            # from other types, should be dealt with seperately
            if (variation_type == 'copy number loss') or \
                    (variation_type == 'copy number gain'):
                for AttributeSet in Measure.AttributeSet:
                    if 'HGVS, genomic, top level' in AttributeSet.\
                            Attribute.Type:
                        if AttributeSet.Attribute.integerValue == 37:
                            hgvs_genome = AttributeSet.Attribute.get_valueOf_()
                    if 'genomic' in AttributeSet.Attribute.Type:
                        HGVS['genomic'].append(AttributeSet.Attribute.
                                               get_valueOf_())
                    elif 'non-coding' in AttributeSet.Attribute.Type:
                        HGVS['non-coding'].append(AttributeSet.Attribute.
                                                  get_valueOf_())
                    elif 'coding' in AttributeSet.Attribute.Type:
                        HGVS['coding'].append(AttributeSet.Attribute.
                                              get_valueOf_())
                    elif 'protein' in AttributeSet.Attribute.Type:
                        HGVS['protein'].append(AttributeSet.
                                               Attribute.get_valueOf_())
            else:
                for AttributeSet in Measure.AttributeSet:
                    if 'genomic' in AttributeSet.Attribute.Type:
                        HGVS['genomic'].append(AttributeSet.
                                               Attribute.get_valueOf_())
                    elif 'non-coding' in AttributeSet.Attribute.Type:
                        HGVS['non-coding'].append(AttributeSet.
                                                  Attribute.get_valueOf_())
                    elif 'coding' in AttributeSet.Attribute.Type:
                        HGVS['coding'].append(AttributeSet.Attribute.
                                              get_valueOf_())
                    elif 'protein' in AttributeSet.Attribute.Type:
                        HGVS['protein'].append(AttributeSet.
                                               Attribute.get_valueOf_())
                    if AttributeSet.Attribute.Type == 'HGVS, coding, RefSeq':
                        hgvs_coding = AttributeSet.Attribute.get_valueOf_()
                    elif AttributeSet.Attribute.Type == \
                            'HGVS, genomic, top level, previous':
                        hgvs_genome = AttributeSet.Attribute.get_valueOf_()
                        break
            if chrom and chromStart and chromEnd:
                if variation_type == 'single nucleotide variant':
                    hgvs_id = "chr%s:g.%s%s>%s" % (chrom, chromStart, ref, alt)
                # items whose type belong to 'Indel, Insertion, \
                # Duplication' might not hava explicit alt information, \
                # so we will parse from hgvs_genome
                elif variation_type == 'Indel':
                    if hgvs_genome:
                        indel_position = hgvs_genome.find('del')
                        indel_alt = hgvs_genome[indel_position+3:]
                        hgvs_id = "chr%s:g.%s_%sdel%s" % \
                                  (chrom, chromStart, chromEnd, indel_alt)
                elif variation_type == 'Deletion':
                    hgvs_id = "chr%s:g.%s_%sdel" % \
                              (chrom, chromStart, chromEnd)
                elif variation_type == 'Insertion':
                    if hgvs_genome:
                        ins_position = hgvs_genome.find('ins')
                        if 'ins' in hgvs_genome:
                            ins_ref = hgvs_genome[ins_position+3:]
                            hgvs_id = "chr%s:g.%s_%sins%s" % \
                                      (chrom, chromStart, chromEnd, ins_ref)
                elif variation_type == 'Duplication':
                    if hgvs_genome:
                        dup_position = hgvs_genome.find('dup')
                        if 'dup' in hgvs_genome:
                            dup_ref = hgvs_genome[dup_position+3:]
                            hgvs_id = "chr%s:g.%s_%sdup%s" % \
                                      (chrom, chromStart, chromEnd, dup_ref)
            elif variation_type == 'copy number loss' or\
                    variation_type == 'copy number gain':
                if hgvs_genome and chrom:
                    hgvs_id = "chr" + chrom + ":" + hgvs_genome.split('.')[2]
            elif hgvs_coding:
                hgvs_id = hgvs_coding
                coding_hgvs_only = True
            else:
                print "couldn't find any id", rcv_accession
                return
        else:
            print 'no measure.attribute', rcv_accession
            return
        for key in HGVS:
            HGVS[key].sort()
        rsid = None
        cosmic = None
        dbvar = None
        uniprot = None
        omim = None
        # loop through XRef to find rsid as well as other ids
        if Measure.XRef:
            for XRef in Measure.XRef:
                if XRef.Type == 'rs':
                    rsid = 'rs' + str(XRef.ID)
                elif XRef.DB == 'COSMIC':
                    cosmic = XRef.ID
                elif XRef.DB == 'OMIM':
                    omim = XRef.ID
                elif XRef.DB == 'UniProtKB/Swiss-Prot':
                    uniprot = XRef.ID
                elif XRef.DB == 'dbVar':
                    dbvar = XRef.ID

        # make sure the hgvs_id is not none
        if hgvs_id:
            one_snp_json = {

                "_id": hgvs_id,
                "clinvar":
                    {
                        "allele_id": allele_id,
                        "variant_id": variant_id,
                        "chrom": chrom,
                        "omim": omim,
                        "cosmic": cosmic,
                        "uniprot": uniprot,
                        "dbvar": dbvar,
                        "hg19":
                            {
                                "start": chromStart_19,
                                "end": chromEnd_19
                            },
                        "hg38":
                            {
                                "start": chromStart_38,
                                "end": chromEnd_38
                            },
                        "type": variation_type,
                        "gene":
                            {
                                "id": gene_id,
                                "symbol": symbol
                            },
                        "rcv":
                            {
                                "accession": rcv_accession,
                                "clinical_significance": clinical_significance,
                                "number_submitters": number_submitters,
                                "review_status": review_status,
                                "last_evaluated": str(last_evaluated),
                                "preferred_name": name,
                                "origin": origin,
                                "conditions":
                                    {
                                        "name": conditions_name,
                                        "synonyms": synonyms,
                                        "identifiers": identifiers,
                                        "age_of_onset": age_of_onset
                                }
                            },
                        "rsid": rsid,
                        "cytogenic": cytogenic,
                        "hgvs": HGVS,
                        "coding_hgvs_only": coding_hgvs_only,
                        "ref": ref,
                        "alt": alt
                    }
            }
            obj = (dict_sweep(unlist(value_convert(one_snp_json,
                                                   ['chrom', 'omim', 'id', 'orphanet', 'gene',
                                                    'rettbase_(cdkl5)', 'cosmic', 'dbrbc'])), [None, '', 'None']))
            yield obj


def rcv_feeder(input_file, hg19):
    # the first two line of clinvar_xml is not useful information
    cv_data = rec_handler(input_file, block_end='</ClinVarSet>\n',
                          skip=2, include_block_end=True)
    print input_file
    for record in cv_data:
        # some exceptions
        if record.startswith('\n</ReleaseSet>'):
            continue
        try:
            record_parsed = clinvar.parseString(record, silence=1)
        except:
            print(record)
            raise
        for record_mapped in _map_line_to_json(record_parsed, hg19):
            yield record_mapped

def load_data(input_file, hg19=True):
    data_generator = rcv_feeder(input_file, hg19)
    data_list = list(data_generator)
    data_list_sorted = sorted(data_list, key=lambda k: k['_id'])
    data_merge_rcv = merge_rcv_accession(data_list_sorted)
    return data_merge_rcv
