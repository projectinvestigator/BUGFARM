import os
import sys
import json
import utils
from json import loads
import jsonlines

projects = [
    "commons-cli","commons-collections","commons-csv",
    "commons-lang","gson","jackson-databind",
    "jfreechart","jsoup","commons-codec",
    "commons-compress","commons-jxpath","commons-math",
    "jackson-core","jackson-dataformat-xml","joda-time"
]

def get_file(dir,saveDir,timeStamp):

    for project in projects:
        all = []
        num = 0
        filenum = 0
        unique = []
        new_data = []
        parsed_mutants = []
        unparsed_mutants = []
        final_mutants = []

        for dirpath, _, files in os.walk(dir):
            for file in files:
                if ".json" in file and project in file:
                    filenum += 1
                    file_path = os.path.join(dirpath,file)
                    f= open(file_path)
                    data = json.load(f) # all mutants

                    num += len(data)
                    id = 0
                    for item in data:
                        new_item = { 
                            "idss":item["idss"],"filename":item["filename"],
                            "old_line_num":item["line"], # line number selected in original code
                            "prob":item["prob"],
                            "old_line_code":item["oldcode"], # line selected in original code
                            "original": item["precode"] + item["oldcode"] + item["aftercode"],
                            "mutated":item["code"]
                        }
                        new_data.append(new_item)

                        # to get parsed mutants - syntactically correct
                        
                        original_sets = utils.read_java(new_item["filename"])
                        mutated_sets = utils.parse_java_func_intervals(new_item["mutated"],new_item["filename"])

                        if len(mutated_sets) == 0:
                            unparsed_mutants.append(new_item)
                        else:
                            parsed_mutants.append(new_item)
                            selected_line_to_mutate = new_item["old_line_code"]
                            tag = 0

                            for mutated_set in mutated_sets:
                                mutated_start = mutated_set[0] # mutated method start line
                                mutated_method = mutated_set[2] # mutated method

                                for original_set in original_sets:
                                    original_start = original_set[0] # original method start line
                                    original_end = original_set[1] # original method end line
                                    original_method = original_set[2] # original method

                                    if original_start == mutated_start \
                                    and new_item["old_line_num"] >= original_start and new_item["old_line_num"] <= original_end:
                                        mutant = {
                                            "idss": new_item["idss"],
                                            "filename": new_item["filename"],
                                            "line_num_to_mutate": new_item["old_line_num"], # line number selected in original code
                                            "prob": new_item["prob"],
                                            "old_line_code": new_item["old_line_code"], # line selected in original code
                                            "original_method": original_method,
                                            "mutated_method": mutated_method,
                                            "start": original_start
                                        }
                                        if mutant not in final_mutants:
                                            final_mutants.append([mutant])
                                            tag = 1
                                            break
                                    if tag == 1:
                                        break

        if num != 0:
            print(project,saveDir," all_results:",num, " all_mutants:",len(new_data), \
            " unparsed_mutants:", len(unparsed_mutants), \
            " parsed_mutants:",len(parsed_mutants), \
            " final_mutants:",len(final_mutants))

            if not os.path.exists(saveDir):
                os.mkdir(saveDir)

            if len(parsed_mutants) > 0:
                parsed_mutants_saveTo = os.path.join(saveDir,timeStamp + "_" + project + "_parsed_mutants.json")
                parsed_mutants_file = open(parsed_mutants_saveTo,"w+")
                parsed_mutants_file.close()
                with open(parsed_mutants_saveTo, "a") as pmfile:
                    json.dump(parsed_mutants, pmfile)
            
            if len(unparsed_mutants) > 0:
                unparsed_mutants_saveTo = os.path.join(saveDir,timeStamp + "_" + project + "_unparsed_mutants.json")
                unparsed_mutants_file = open(unparsed_mutants_saveTo,"w+")
                unparsed_mutants_file.close()
                with open(unparsed_mutants_saveTo, "a") as umfile:
                    json.dump(unparsed_mutants, umfile)
            
            if len(final_mutants) > 0:
                final_mutants_saveTo = os.path.join(saveDir,timeStamp + "_" + project + "_final_mutants.jsonl")
                final_mutants_file = open(final_mutants_saveTo,"w+")
                final_mutants_file.close()
                for final_item in final_mutants:
                    with jsonlines.open(final_mutants_saveTo,"a") as finalfile:
                        finalfile.write_all([final_item])


if __name__ == "__main__":
    args = sys.argv[1:]
    mutant_dir = args[0]
    saveto_dir = args[1]
    timeStamp = args[2]
    get_file(mutant_dir,saveto_dir,timeStamp)

