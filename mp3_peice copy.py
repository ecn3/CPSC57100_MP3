""" 
Christian Nelson
10/10/2020
CPSC-57100-002, Fall 2020
Machine Problem 3: Course Planning using a Constraint Satisfaction Problem Formulation
"""

'''
Electives chosen randomly instead of being assigned -values
finish term not properly constrained
'''

# Imports
import pandas as pd
import numpy as np
from constraint import *

# Formats
fm1 = "Number of Possible Degree Plans is {}"
fm2 = "Not Taken          {}"

def create_term_list(terms, years=4):
    '''Create a list of term indexes for years in the future'''
    all_terms = []
    for year in range(years):
        for term in terms:    
            all_terms.append(year*6+term)
    return all_terms
    
def map_to_term_label(term_num):
    '''Returns the label of a term, given its number'''
    term_num_to_label_map = {
            0: 'Fall 1',
            1: 'Fall 2',
            2: 'Spring 1',
            3: 'Spring 2',
            4: 'Summer 1',
            5: 'Summer 2',
    }
    if (term_num < 1):
        return 'Not Taken'
    else:
        return 'Year ' + str((term_num - 1) // 6 + 1) + ' ' + term_num_to_label_map[(term_num - 1) % 6]

def prereq(a, b):
    '''Used for encoding prerequisite constraints, a is a prerequisite for b'''
    if a > 0 and b > 0: # Taking both prereq a and course b
        return a < b
    elif a > 0 and b < 0: # Taking prereq a, but not course b
        return True
    elif a < 0 and b > 0: #  Taking course b, but not prereq a
        return False
    else:
        return True # Not taking prereq a or course b

def get_possible_course_list(start, finish):
    '''Returns a possible course schedule, assuming student starts in start term
       finishes in finish term'''
    problem = Problem()
    
    # Read course_offerings file
    course_offerings = pd.read_excel('csp_course_rotations.xlsx', sheet_name='course_rotations')
    course_prereqs = pd.read_excel('csp_course_rotations.xlsx', sheet_name='prereqs')

    # Foundation course terms
    foundation_courses = course_offerings[course_offerings.Type=='foundation']
    for r,row in foundation_courses.iterrows():
        term = create_term_list(list(row[row==1].index))
        # Control start and finish terms
        term = [t for t in term if t>start] 
        term = [t for t in term if t<finish] 
        problem.addVariable(row.Course, term)

    """ TODO FROM HERE... """    
    # Core course terms
    
    core_courses = course_offerings[course_offerings.Type=='core']
    for r,row in core_courses.iterrows():
        term = create_term_list(list(row[row==1].index))
        # Control start and finish terms
        term = [t for t in term if t>start] 
        term = [t for t in term if t<finish] 
        problem.addVariable(row.Course, term)

    # CS Electives course terms (-x = elective not taken)
    all_elective_courses = course_offerings[course_offerings.Type=='elective']
    elective_courses = all_elective_courses.sample(3) # Control electives - exactly 3 courses must be chosen
    all_elective_courses = all_elective_courses.drop(elective_courses.index)
    elective_not_taken = all_elective_courses.Course
    
    for r,row in elective_courses.iterrows():
        term = create_term_list(list(row[row==1].index))
        term = [t for t in term if t>start] 
        #term = [t for t in term if t<finish] 
        problem.addVariable(row.Course, term)

    # Capstone
    capstone_courses = course_offerings[course_offerings.Type=='capstone']
    for r,row in capstone_courses.iterrows():
        term = create_term_list(list(row[row==1].index))
        # Control start and finish terms
        term = [t for t in term if t>start] 
        #term = [t for t in term if t<finish] 
        problem.addVariable(row.Course, term)
    
    # Guarantee no repeats of courses
    problem.addConstraint(AllDifferentConstraint()) # Makes sure no classes are duplicated

    # Prereqs
    course_prereqs = course_prereqs[~course_prereqs.course.isin(elective_not_taken)] # remove classes not taken from preqs

    i = 0
    for preq in course_prereqs.prereq:
        problem.addConstraint(prereq, (course_prereqs.prereq.iloc[i], course_prereqs.course.iloc[i]))
        i+=1
    """ ...TO HERE """
    
    # Generate a possible solution
    sol = problem.getSolutions()
    print(fm1.format(len(sol))) # format printing to match sample output
    print("")
    s = pd.Series(sol[0])
    return elective_not_taken, s.sort_values().map(map_to_term_label)

# Print heading
print("CLASS: Artificial Intelligence, Lewis University")
print("NAME: Christian Nelson")
print("")


# Check for possible schedules for all start terms
for start in [1]:
    print('START TERM = ' + map_to_term_label(start))
    elective_not_taken, s = get_possible_course_list(start,start+13)
    if s.empty:
        print('NO POSSIBLE SCHEDULE!')
    else:
        s2 = pd.Series(s.index.values, index=s)
        print("Sample Degree Plan")
        for x in elective_not_taken:
            print(fm2.format(x))
        print(s2.to_string())
    print()
