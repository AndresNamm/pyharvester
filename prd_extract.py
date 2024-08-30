
#%%
from dataclasses import dataclass
import pandas as pd
import conf_utils
import file_utils 
import os
from dataclasses import dataclass


def parse_stanford_file(file_info:file_utils.FileInfo):
    lines=[]
    with open(file_info.abs_path,"r",encoding="iso8859_2") as f:
        for line in f.readlines():
            lines.append(line)

    # SPLIT EACH VARIABLE_KEY,VALUE COMBINATION WITH SEPARATOR ~
    variables = "".join(lines).split("~")
    variables_tf_l1=[]

    for element in variables:
            var_list = element.split(" ")
            if len(var_list)>2:
                var_nr = var_list[0]
                var_type = var_list[1]
                var_value = " ".join(var_list[2:])                
                element_tf = {"var_nr":var_nr,"type":var_type,"val":var_value.lstrip('\n')}
                variables_tf_l1.append(element_tf)

    # GET THE VARIABLE DECODING INFORMATION
    var_definitions = pd.read_excel("/workspaces/kv-scraper/timberly/data/vars.xlsx")
    var_definitions.info()
    var_definitions.drop(['History','DpOth2'],axis=1,inplace=True)
    var_prd_sample = pd.DataFrame.from_records(variables_tf_l1)
    var_prd_sample['var_nr']=var_prd_sample['var_nr'].astype("int64")
    var_prd_sample['type']=var_prd_sample['type'].astype("int64")

    sample_with_explanations = var_prd_sample.merge(var_definitions,left_on=['var_nr','type'], right_on = ['VarNr','Typ'],how='inner')
    sample_with_explanations['idx'] = sample_with_explanations['var_nr'].astype(str) + "-" + sample_with_explanations['type'].astype(str)

    sample_with_explanations = sample_with_explanations.set_index('idx')
    sample_with_explanations.to_excel(file_info.get_result_with_extension("xlsx",file_info.extension))
    sample_with_explanations.to_json(file_info.get_result_with_extension("json",file_info.extension),orient="index",force_ascii=True)


if __name__ == '__main__':
    DATA_PATH='/workspaces/kv-scraper/timberly/data/'
    RESULT_PATH='/workspaces/kv-scraper/timberly/results/'
    TEST_FILE='QB236_5-251022-224821.prd'
    conf = conf_utils.read_conf()
    
    if not conf["TIMBERLY"]["CONVERT_ALL_PRDS"]:
        print("Starting parse")
        file_info = file_utils.FileInfo(os.path.join(DATA_PATH,TEST_FILE),RESULT_PATH)
        parse_stanford_file(file_info=file_info)
    DATA_PATH='/workspaces/kv-scraper/timberly/data/'
    TEST_FILE='QB236-5.apt'
    conf = conf_utils.read_conf()
    if not conf["TIMBERLY"]["CONVERT_ALL_PRDS"]:
        print("Starting parse")
        file_info = file_utils.FileInfo(os.path.join(DATA_PATH,TEST_FILE),RESULT_PATH)
        parse_stanford_file(file_info=file_info)

# %%
