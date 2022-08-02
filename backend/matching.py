import pandas as pd
import json

class Person:
  def __init__(self, name, university, course, lob, location, interest1, interest2, interest3, programming1, programming2):
    self.name = name
    self.university = university
    self.course = course
    self.lob = lob
    self.location = location
    self.interests = [interest1, interest2, interest3]
    self.programming = [programming1, programming2]

class Intern(Person):
  def __init__(self, name, university, course, lob, location, interest1, interest2, interest3, programming1, programming2, request_time, potential_buddies):
    super().__init__(name, university, course, lob, location, interest1, interest2, interest3, programming1, programming2)
    self.request_time = request_time
    self.potential_buddies = potential_buddies
    self.assigned_buddy = None

class Buddy(Person):
  def __init__(self, name, university, course, lob, location, interest1, interest2, interest3, programming1, programming2, time_available):
    super().__init__(name, university, course, lob, location, interest1, interest2, interest3, programming1, programming2)
    self.time_available = time_available
    self.assigned_interns = []

# TODO: Cannot assume name is buddies.csv and interns.csv, check table headers time availbale, time required and if table doesn't have these headers, reject
def read_csv_files():
    buddies = pd.read_csv("data/buddies.csv")
    interns = pd.read_csv("data/interns.csv")
    return buddies, interns

def create_objects(buddies_csv, interns_csv):
    buddies = []
    interns = []

    for _, buddy_row in buddies_csv.iterrows():
        buddy = Buddy(
            buddy_row["Name"], 
            buddy_row["University"], 
            buddy_row["Course"], 
            buddy_row["LoB"],
            buddy_row["Location"], 
            buddy_row["Interest 1"], 
            buddy_row["Interest 2"], 
            buddy_row["Interest 3"], 
            buddy_row["Programming 1"],
            buddy_row["Programming 2"],
            buddy_row["Time Available"])
        buddies.append(buddy)

    for _, intern_row in interns_csv.iterrows():
        intern = Intern(
            intern_row["Name"],
            intern_row["University"], 
            intern_row["Course"], 
            intern_row["LoB"],
            intern_row["Location"], 
            intern_row["Interest 1"], 
            intern_row["Interest 2"], 
            intern_row["Interest 3"], 
            intern_row["Programming 1"],
            intern_row["Programming 2"],
            intern_row["Request Time"],
            buddies.copy()
            )
        interns.append(intern)

    return interns

def filter_by_lob_location(interns):
    for intern in interns:
        new_potential_buddies = []
        for potential_buddy in intern.potential_buddies:
            if potential_buddy.lob != intern.lob and potential_buddy.location == intern.location:
                new_potential_buddies.append(potential_buddy)
        intern.potential_buddies = new_potential_buddies

def build_compatibility_score(interns):
    for intern in interns:
        compatibility_scores = []
        for potential_buddy in intern.potential_buddies:
            compatibility_score = 0
            if potential_buddy.university == intern.university:
                compatibility_score += 1
            if potential_buddy.course == intern.course:
                compatibility_score += 1
            for potential_buddy_interest in potential_buddy.interests:
                for intern_interest in intern.interests:
                    if potential_buddy_interest == intern_interest:
                        compatibility_score += 1
            for potential_buddy_programming in potential_buddy.programming:
                for intern_programming in intern.programming:
                    if potential_buddy_programming == intern_programming:
                        compatibility_score += 1
            compatibility_scores.append(compatibility_score)
        intern.potential_buddies = list(zip(intern.potential_buddies, compatibility_scores))

def sort_interns(interns):
    return sorted(interns, key = lambda intern: len(intern.potential_buddies))

def sort_potential_buddies(interns):
    for intern in interns:
        intern.potential_buddies = sorted(intern.potential_buddies, key = lambda intern_score: intern_score[1], reverse = True)

def assign_buddies(interns):
    for intern in interns:
        for potential_buddy, compatibility_score in intern.potential_buddies:
            if potential_buddy.time_available >= intern.request_time:
                intern.assigned_buddy = (potential_buddy, compatibility_score)
                potential_buddy.assigned_interns.append(intern)
                potential_buddy.time_available -= intern.request_time
                break

def identify_unassigned_interns(interns):
    unassigned_interns = []
    for intern in interns:
        if not intern.assigned_buddy:
            unassigned_interns.append(intern)
    return unassigned_interns

def reassign_buddies(unassigned_interns):
    for unassigned_intern in unassigned_interns:
        assignment_found = False
        for potential_buddy_for_unassigned_intern, compatibility_score_for_unassigned_intern in unassigned_intern.potential_buddies:
            if assignment_found:
                break
            for assigned_intern in potential_buddy_for_unassigned_intern.assigned_interns:
                if assignment_found:
                    break
                if assigned_intern.request_time >= unassigned_intern.request_time:
                    for potential_buddy_for_assigned_intern, compatibility_score_for_assigned_intern in assigned_intern.potential_buddies:
                        if potential_buddy_for_assigned_intern != assigned_intern.assigned_buddy[0] and potential_buddy_for_assigned_intern.time_available >= assigned_intern.request_time:
                            potential_buddy_for_unassigned_intern.assigned_interns.remove(assigned_intern)
                            potential_buddy_for_unassigned_intern.time_available += assigned_intern.request_time

                            potential_buddy_for_assigned_intern.assigned_interns.append(assigned_intern)
                            potential_buddy_for_assigned_intern.time_available -= assigned_intern.request_time
                            assigned_intern.assigned_buddy = (potential_buddy_for_assigned_intern, compatibility_score_for_assigned_intern)

                            potential_buddy_for_unassigned_intern.assigned_interns.append(unassigned_intern)
                            potential_buddy_for_unassigned_intern.time_available -= unassigned_intern.request_time
                            unassigned_intern.assigned_buddy = (potential_buddy_for_unassigned_intern, compatibility_score_for_unassigned_intern)

                            assignment_found = True
                            break

def build_dict_list(interns):
    dict_list = []
    for intern in interns:
        # print(f"{intern.name} - {intern.assigned_buddy[0].name} - {intern.assigned_buddy[1] / 7 * 100}")
        dict_list.append({ "name": intern.name, "buddy": intern.assigned_buddy[0].name if intern.assigned_buddy else None, "score": intern.assigned_buddy[1] / 7 * 100 if intern.assigned_buddy else None})
    return dict_list

def get_all_interns():
    buddies_csv, interns_csv = read_csv_files()
    interns = create_objects(buddies_csv, interns_csv)
    filter_by_lob_location(interns)
    build_compatibility_score(interns)
    interns = sort_interns(interns)
    sort_potential_buddies(interns)
    assign_buddies(interns)
    unassigned_interns = identify_unassigned_interns(interns)
    reassign_buddies(unassigned_interns)
    assignments_dict_list = build_dict_list(interns)

    print(assignments_dict_list)

    return assignments_dict_list

if __name__ == "__main__":
    get_all_interns()