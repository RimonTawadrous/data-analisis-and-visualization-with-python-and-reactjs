import json
from flask import Flask, jsonify
import os
import sys

annotators_input = {}
annotation_time_list = []
images_votes = {}
images_with_cant_solve = {}
images_with_Corrupt_data = {}
references = {}
taken_time_segments_dict ={}

app = Flask(__name__)

@app.route("/annotators",methods = ['GET'])
def annotators():
    global annotators_input
    return_annotators_input = {}
    for user in annotators_input:
        return_annotators_input[user] ={"annotations_count":0, "yes_ans_counts":0, "no_ans_counts":0,"cant_solve_num":0,
    "corrupt_data_num":0,"wrong_ans_count":0}
        return_annotators_input[user]["annotations_count"] = annotators_input[user]["annotations_count"]
        return_annotators_input[user]["yes_ans_counts"] = annotators_input[user]["yes_ans_counts"]
        return_annotators_input[user]["no_ans_counts"] = annotators_input[user]["no_ans_counts"]
        return_annotators_input[user]["cant_solve_num"] = annotators_input[user]["cant_solve_num"]
        return_annotators_input[user]["corrupt_data_num"] = annotators_input[user]["corrupt_data_num"]
        return_annotators_input[user]["wrong_ans_count"] = annotators_input[user]["wrong_ans_count"]
    
    return_annotators_input = dict(sorted(return_annotators_input.items(), key=lambda item: item[1]["annotations_count"]))    
    
    return  json.dumps(return_annotators_input)

@app.route("/annotators/time",methods = ['GET'])
def getAnnotationTime():
    global annotation_time_list, annotators_input, taken_time_segments_dict

    (max_time , min_time_less_than_zero, min_time, average) = annotationTime(annotation_time_list)
    returnMessage = {"maxTime":max_time,"minTimeLessThanZero":min_time_less_than_zero,"minTime":min_time,"average":average,"takenTimeSegments":taken_time_segments_dict}
    return json.dumps(returnMessage)

@app.route("/annotations/answers-agreement-ratio",methods = ['GET'])
def getAnnotationsAnswerAgreementRatio():
    global images_votes
    (agreement_percentage, agreement_number, confused_annotation, confused_annotation_frequency) = answerAgrementRatio(images_votes)
    return  json.dumps({"confusedAnnotations":confused_annotation,"confusedAnnotationsFreq":confused_annotation_frequency})

@app.route("/annotations/data-problems",methods = ['GET'])
def getAnnotationsWithProblems():
    global annotators_input, images_with_cant_solve, images_with_Corrupt_data
    (corrupt_data_num, cant_solve_num) = getDataProblems(annotators_input)
    return  json.dumps({"corruptDataNum":corrupt_data_num,"cantSolveNum":cant_solve_num,"imagesWithCantSolve":images_with_cant_solve,"imagesWithCorruptData":images_with_Corrupt_data})


@app.route("/annotators/correctness",methods = ['GET'])
def getAnnotatorsCorrectness():
    global annotators_input
    return_annotators_input = {}

    for user in annotators_input:
        return_annotators_input[user] = annotators_input[user]["correctnesss"]

    return_annotators_input = dict(sorted(return_annotators_input.items(), key=lambda item: item[1]))    

    return  json.dumps(return_annotators_input)

@app.route("/dataset/meta",methods = ['GET'])
def getDataSetMeta():
    global references
    (dataset_true_images_count, dataset_false_images_count) =  checkDataBalance(references)
    return  json.dumps({"datasetTrueImagesCount":dataset_true_images_count,"datasetFalseImagesCount":dataset_false_images_count})



def annotationTime(annotation_time_list):
    count = 0
    max_time = -100000000
    min_time = 100000000
    min_time_less_than_zero = 100000000
    sum = 0
    average = 0
    
    for time in annotation_time_list:
        count += 1
        sum += time

        if (time > max_time):
            max_time = time
        elif (time < min_time and time > 0):
            min_time = time
        elif (time < min_time_less_than_zero and time < 0):
            min_time_less_than_zero = time

    average = sum / count

    return max_time , min_time_less_than_zero, min_time, average


def answerAgrementRatio(annotation_time_dict):
    agreement_percentage = {}
    agreement_number = {}
    confused_annotation = {}
    confused_annotation_frequency = {}
    for key in annotation_time_dict:
        if( len(annotation_time_dict[key]["yes_Voters"]) > len(annotation_time_dict[key]["no_Voters"])):
            agreement_percentage[key] = len(annotation_time_dict[key]["yes_Voters"]) / (len(annotation_time_dict[key]["no_Voters"]) if len(annotation_time_dict[key]["no_Voters"]) > 0 else 1 )
        else:
            agreement_percentage[key] = len(annotation_time_dict[key]["no_Voters"]) / (len(annotation_time_dict[key]["yes_Voters"]) if len(annotation_time_dict[key]["yes_Voters"]) > 0 else 1 )
        if(agreement_percentage[key] <= 3):
            confused_annotation[key] = agreement_percentage[key]
            if(agreement_percentage[key] not in confused_annotation_frequency):
                confused_annotation_frequency[agreement_percentage[key]] = []
            confused_annotation_frequency[agreement_percentage[key]].append(key)
            
        agreement_number[key] = {"yes_ans_num": len(annotation_time_dict[key]["yes_Voters"]), "no_ans_num":len(annotation_time_dict[key]["no_Voters"]),
        "cant_solve_num":len(annotation_time_dict[key]["cant_solve_true_users_id_list"]), "corrupt_data_num":len(annotation_time_dict[key]["corrupt_data_true_users_id_list"])}
    return agreement_percentage,agreement_number, confused_annotation,confused_annotation_frequency

def getDataProblems(annotators_input):
    corrupt_data_num = 0
    cant_solve_num = 0

    for user in annotators_input:
        corrupt_data_num += annotators_input[user]["corrupt_data_num"]
        cant_solve_num += annotators_input[user]["cant_solve_num"]

    return corrupt_data_num, cant_solve_num

def checkDataBalance(annotators_input):
    false_num = 0
    true_num = 0
    for image in annotators_input:
        if (annotators_input[image]["is_bicycle"] == True):
            true_num += 1
        else:
            false_num += 1
    return true_num,false_num

def checkAnnotatorsSkills(annotators_data):
    for annotator in annotators_data:
        annotators_data[annotator]["correctnesss"] = ((annotators_data[annotator]["annotations_count"] - annotators_data[annotator]["wrong_ans_count"]) / annotators_data[annotator]["annotations_count"]) * 100

def timeDuration(annotation_time_list):
    taken_time_segmentation_dict = {-1:0}
    for time in annotation_time_list:
        if time < 0:
            taken_time_segmentation_dict[-1] += 1
        rounded_val = round(time, -3)
        if((rounded_val-time) < 0):
            rounded_val = rounded_val+1000

        if (rounded_val not in taken_time_segmentation_dict):
            taken_time_segmentation_dict[rounded_val] = 0
        taken_time_segmentation_dict[rounded_val] += 1
    return taken_time_segmentation_dict


if __name__ == '__main__':

    anonymized_project_file = open(os.path.join(sys.path[0], "anonymized_project.json"))
    references_file = open(os.path.join(sys.path[0], "references.json"))

    anonymized_project = json.load(anonymized_project_file)
    references = json.load(references_file)

    for i , row in enumerate(anonymized_project["results"]["root_node"]["results"]):
        for j , result in enumerate(anonymized_project["results"]["root_node"]["results"][row]["results"]):
            image_url = str(result["task_input"]["image_url"])
            image_id = image_url[image_url.rfind("/")+1:image_url.rfind(".")]
            image_true_answer = references[image_id]["is_bicycle"]

            if(result["user"]["id"] not in annotators_input):
                annotators_input[result["user"]["id"]] = {"annotations_count":0, "yes_ans_counts":0, "no_ans_counts":0,
                "cant_solve_num":0,"corrupt_data_num":0,"wrong_ans_count":0,"anotations":{}}
            annotators_input[result["user"]["id"]]["annotations_count"] += 1 

            if(image_id not in images_votes):
                images_votes[image_id] = {"yes_Voters":[], "no_Voters":[], "cant_solve_true_users_id_list":[], "cant_solve_false_users_id_list":[], "corrupt_data_true_users_id_list":[], "corrupt_data_false_users_id_list":[]}
            
            if (image_id not in annotators_input[result["user"]["id"]]["anotations"]):
                annotators_input[result["user"]["id"]]["anotations"][image_id] = {}

            if(result["task_output"]["answer"] == "no"):
                images_votes[image_id]["no_Voters"].append(result["user"]["id"])
                annotators_input[result["user"]["id"]]["anotations"][image_id]["answer"] = "no"
                annotators_input[result["user"]["id"]]["no_ans_counts"] += 1
                if(image_true_answer == True):
                    annotators_input[result["user"]["id"]]["wrong_ans_count"] += 1


            elif(result["task_output"]["answer"] == "yes"):
                images_votes[image_id]["yes_Voters"].append(result["user"]["id"])
                annotators_input[result["user"]["id"]]["anotations"][image_id]["answer"] = "yes"
                annotators_input[result["user"]["id"]]["yes_ans_counts"] += 1
                if(image_true_answer == False):
                    annotators_input[result["user"]["id"]]["wrong_ans_count"] += 1

            if (result["task_output"]["cant_solve"] == True):
                images_votes[image_id]["cant_solve_true_users_id_list"].append(result["user"]["id"])
                annotators_input[result["user"]["id"]]["anotations"][image_id]["cant_solve"] = True
                annotators_input[result["user"]["id"]]["cant_solve_num"] += 1
                if(image_id not in images_with_cant_solve):
                    images_with_cant_solve[image_id] = {"count":0,"voted_annotators_list":[]}
                images_with_cant_solve[image_id]["count"] += 1
                images_with_cant_solve[image_id]["voted_annotators_list"].append(result["user"]["id"])

            elif (result["task_output"]["cant_solve"] == False):
                images_votes[image_id]["cant_solve_false_users_id_list"].append(result["user"]["id"])
                annotators_input[result["user"]["id"]]["anotations"][image_id]["cant_solve"] = False

            if (result["task_output"]["corrupt_data"] == True):
                images_votes[image_id]["corrupt_data_true_users_id_list"].append(result["user"]["id"])
                annotators_input[result["user"]["id"]]["anotations"][image_id]["corrupt_data"] = True
                annotators_input[result["user"]["id"]]["corrupt_data_num"] += 1
                if(image_id not in images_with_Corrupt_data):
                    images_with_Corrupt_data[image_id] = {"count":0,"voted_annotators_list":[]}
                images_with_Corrupt_data[image_id]["count"] += 1
                images_with_Corrupt_data[image_id]["voted_annotators_list"].append(result["user"]["id"])


            elif (result["task_output"]["corrupt_data"] == False):
                images_votes[image_id]["corrupt_data_false_users_id_list"].append(result["user"]["id"])
                annotators_input[result["user"]["id"]]["anotations"][image_id]["corrupt_data"] = False
            
            annotators_input[result["user"]["id"]]["anotations"][image_id]["time"] = result["task_output"]["duration_ms"]
            annotation_time_list.append(result["task_output"]["duration_ms"])

    (agreement_percentage, agreement_number, confused_annotation,confused_annotation_frequency) = answerAgrementRatio(images_votes)
    (dataset_true_images_count, dataset_false_images_count) =  checkDataBalance(references)
    (corrupt_data_num, cant_solve_num) = getDataProblems(annotators_input)
    checkAnnotatorsSkills(annotators_input)
    taken_time_segments_dict = timeDuration(annotation_time_list)

    # print("1-a) How many annotators did contribute to the dataset?  ", len(annotators_input))
    # print("1-b) What are the average, min and max annotation times (durations)?  ", annotationTime(annotation_time_list))
    # print("1-c) Did all annotators produce the same amount of results, or are there differences? no")
    # print("1-D) Are there questions for which annotators highly disagree?", len(confused_annotation) ,confused_annotation)
    # print("2) How often does each occur in the project and do you see a trend within the annotators that made use of these options? ",
    #  "corrupt_data_num : ", corrupt_data_num, " cant_solve_num : ", cant_solve_num)
    # print("3) Is the reference set balanced? ", "num of true bikes : ",dataset_true_images_count, "num of false bikes : ", dataset_false_images_count)

    # print("What are the average, min and max annotation times (durations)?  ", annotationTime(annotation_time_list))

    # with open('annotatorsData.json', 'w') as outfile:
    #     json.dump(annotators_input, outfile)
    
    # with open('annotationsTimeList.json', 'w') as outfile:
    #     json.dump(annotation_time_list, outfile)

    # with open('imagesAnnotations.json', 'w') as outfile:
    #     json.dump(images_votes, outfile)
    
    # with open('imagesWithCantSolve.json', 'w') as outfile:
    #     json.dump(images_with_cant_solve, outfile)

    # with open('imagesWithcorruptData.json', 'w') as outfile:
    #     json.dump(images_with_Corrupt_data, outfile)

    # with open('anntotationTakenTimeSegments.json', 'w') as outfile:
    #     json.dump(taken_time_segments_dict, outfile)


    anonymized_project_file.close()
    references_file.close()


    app.run(debug=True)
