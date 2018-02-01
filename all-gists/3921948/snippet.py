import csv
import random

original_list = []
family_number = 0
student_list = []
teacher_list = []
teacher_name_to_index = dict() #Dictionary for looking up teacher names 

LSteacher_sched_a = [] #list for creating a schedule for each teacher on A day.
LSteacher_sched_b = [] #list for creating a schedule for each teacher on B day.
US_conf_a = [] #list for conference sessions for upper school on A day.
US_conf_b = [] #list for conference sessions for upper school on B day.
students = []

LS_CONF_LENGTH = 25
US_CONF_LENGTH = 15

def get_grade(list):
    return list[0]

def get_max_kids(list):  #Determines the greatest number of kids in a family for the entire population
    max_kids = int(len(list[0])/3)
    return max_kids

def get_num_kids(list, max_kids): #Looks at spreadsheet to get the number of kids in a given family
    j = 0
    k = 1
    
    while j<max_kids:
        #print(j)
        if(list[3*j]!=""):
            #print(3*j)
            j = j + 1
            k = j
        else:
            j = j+1
    return k

def get_students_from_file(filename):
    with open(filename, newline='') as f:
        reader = csv.reader(f, delimiter=';', quoting=csv.QUOTE_NONE)
        for row in reader:
            #print(row)
            original_list.append(row) #Add each row of the file to original_list.

    
    sorted_list = sorted(original_list) #Sort the list by grade level.

    max_kids = get_max_kids(sorted_list) #Get the maximum number of kids out of all families
        
    family_number = 0
    
    #for i in range(0,4):
    for i in range(0,len(sorted_list)):
         
         #print(sorted_list[i][0:3])
         num_kids = get_num_kids(sorted_list[i],max_kids)   #Get the number of kids in the current row of the input file.
         
         if (num_kids > 1):                                 #If there are multiple kids, add each one to the list by moving across the row and getting info. 
             j = 0
             family_number = family_number + 1              #Create a new family number by increasing the previous number by 1.

             while (j<num_kids):
                  student_list.append(sorted_list[i][0+3*j:3*j+3]) #Add a row to student_list for the jth child in the family, and add the info for that child to student_list.
                  j = j + 1
                  
             k = 1
             while (num_kids-k>=0):                         
                 student_list[len(student_list)-k].append(family_number) #Append each member of the family's row in student_list with the family number.
                 student_list[len(student_list)-k].append(num_kids)
                 k = k + 1
             
         elif(num_kids ==1):                                #If there is only one child, add the child to the list. 
             student_list.append(sorted_list[i][0:3])       #Give that child a family_number of zero.
             student_list[len(student_list)-1].append(0)
             student_list[len(student_list)-1].append(1)
             
    students_w_fam = student_list  
        
    for i in range(0,len(student_list)):
        tempo = (student_list[i][0],student_list[i][1],student_list[i][2],student_list[i][3],student_list[i][4])
        students.append(tempo) #Create a tuple for each row of the list of students. Makes sorting easier.
        #print(students[i])
        

    
    print("Processed",len(student_list),"total students, with",family_number,"families that have multiple children.")   
    return students



#get_LS_teachers takes the names of homeroom teachers from the spreadsheet, and creates a list of conference spaces for each one.
def get_LS_teachers(student_list):  
    for i in range(0,len(student_list)):
        #print(student_list[i])
        if ((student_list[i][1] in teacher_list)==False and (int(student_list[i][0])<=5)):
            LSteacher_sched_a.append([student_list[i][1],'','','','','','','','','','','','','',''])
            LSteacher_sched_b.append([student_list[i][1],'','','','','','','','','','','','','','',''])
            teacher_name_to_index[student_list[i][1]] = len(LSteacher_sched_a) - 1
            teacher_list.append(student_list[i][1])
            

    
    return 

def create_US_confs():
    names = ['A','B','C','D','E','F']
    for i in range(0,len(names)):
        US_conf_a.append([names[i],'','','','','','','','','','','','','',''])
        US_conf_b.append([names[i],'','','','','','','','','','','','','','',''])

def get_num_of_students(row):
    num = row[4]
    return num

def get_family(student, family_number): #This function stores all members of family (family_number) in family_list for processing in the main function.
    family_list = []
    for i in range(0,len(student)):
        if(student[i][3] == family_number):
            family_list.append(student[i])
    return family_list

def pick_conf_day():                        #Function chooses a random day for conference for a single family. 
    a = random.randint(0,1)
    if (a == 0):
        US_conf_day = US_conf_a
        LS_conf_day = LSteacher_sched_a
    else:
        US_conf_day = US_conf_b
        LS_conf_day = LSteacher_sched_b
    return US_conf_day,LS_conf_day    

def switch_conf_day(US_conf_day, LS_conf_day): #Switches the conference day from A to B, or B to A.
    if (US_conf_day == US_conf_a):
        US_conf_day = US_conf_b
        LS_conf_day = LSteacher_sched_b
    else:
        US_conf_day = US_conf_a
        LS_conf_day = LSteacher_sched_a
    return US_conf_day, LS_conf_day

def get_US_index(teacher_index): #Uses the teacher_index variable to select an US conference room out of those available in US_conf_a or US_conf_b.
    teacher_index = teacher_index + 1
    if(teacher_index>5):
        teacher_index = 0
    return teacher_index


def choose_LS_conf_balance(teacher_index):                      #This function ensures that the # of students on each conference day is approximately equal.
    count_1 = LSteacher_sched_a[teacher_index].count('')
    count_2 = LSteacher_sched_b[teacher_index].count('')
    if(count_1>=count_2):
        LS_conf_day = LSteacher_sched_a
    else:
        LS_conf_day = LSteacher_sched_b
    return LS_conf_day                           


def place_families_into_conf(sort_by_family_num): 
     print("Placing families into conferences")
     k = 0
     student_count = 0
     #US_conf_day, LS_conf_day = pick_conf_day()
     US_conf_day, LS_conf_day = US_conf_a, LSteacher_sched_a 
     teacher_index = 0
     
     while (k in range(0,len(sort_by_family_num)) and (sort_by_family_num[k][3]!=0)):
        

        current_row = sort_by_family_num[k][3]     #Grabs the family number from the current row of the list.
        current_family = get_family(sort_by_family_num,current_row) #Stores the current family defined by the number in current_family
     
        
        k = k + len(current_family)
        #US_conf_day, LS_conf_day = switch_conf_day(US_conf_day,LS_conf_day) #Switches conference day from the last family.
        
        curr_fam_sched = []
        CONF_TIME = 0
        j = 1
        
        
        for i in range(0,len(current_family)):

            
            set_conf_index=0
            curr_teacher = current_family[i][1] #Gets the teacher for the current member of the family.
            
            if(int(current_family[i][0])<=5):  #If the student is in grade 5 or below, places him/her in a LS conference block corresponding to curr_teacher.
                
                teacher_index = teacher_name_to_index[curr_teacher]
                
                #print(teacher_index,teacher_list[teacher_index])
                


                while(set_conf_index==0):
                    
                    
                    if(LS_conf_day[teacher_index][j]==''):  #Checks to see if current j value is empty.

                        if(j>=11):                                                                  #If there are no open conferences on this day, switch conference day and clear the schedule.
                            US_conf_day, LS_conf_day = switch_conf_day(US_conf_day,LS_conf_day)
                            curr_fam_sched = []
                            j = 1
                            i = 0
                        else:
                            set_conf_index = 1
                    else:
                        j = j + 1
                            
        
                a = (current_family[i][2] + '*')
                #print(a)
                curr_fam_sched.append([current_family[i][0],curr_teacher,a,j])
                #print(curr_fam_sched)
                
                prev_index = j #This index keeps track of the last slot j used to schedule a student in a family. This keeps conferences consecutive.
                j = j+random.randint(1,2) #Randomly advances the next conference day either 1 or 2 spots.
                 
                student_count = student_count + 1
                i = i + 1
                    #print(curr_fam_sched)
                       
            else: #This is for students in grade 6 or above.
                teacher_index = get_US_index(teacher_index)
                times_switched_room = 0
                set_conf_index = 0

                while(set_conf_index ==0):
                                                      
                    if(US_conf_day[teacher_index][j]==''):
                        
                        if((j==5) or (j==6)):   #Always leave slots 5 or 6 open for open conferences with US teachers.
                            
                            j=7
                        
#                        elif((j==11) or (j==12)):
#                            j = 13


                        elif((j - prev_index)>5):       #This makes it so that siblings in US are not too far apart from each other.
                            j = prev_index+1
                            teacher_index = get_US_index(teacher_index) 
                            #print("siblings too far apart!")

                        elif (j > 15):
                            #print("Switching conference room...")
                            teacher_index = get_US_index(teacher_index)
                            times_switched_room = times_switched_room + 1
                            j = prev_index+1
                        
                            if(times_switched_room>5): #If the program has switched through all five conference days and can't find a spot, switch conference day and clear the family schedule.
                               print("Switching room")
                               US_conf_day, LS_conf_day = switch_conf_day(US_conf_day, LS_conf_day) 
                               times_switched_room = 0
                               curr_fam_sched=[]
                               j = 1
                               i = 0
                               
                        else:
                            set_conf_index=1
                    else:
                         j = j + 1
                        
                curr_fam_sched.append([current_family[i][0],teacher_index, current_family[i][2]+'*',j])
                prev_index = j
                j = j+random.randint(1,1)
                student_count = student_count + 1
                
                    
            i = i + 1
            
            
        for q in range(0,len(curr_fam_sched)): #The program doesn't write the full schedule to the conference arrays until the entire family is scheduled.

            outFile = open('Family-Conf-times.csv','a')
            outFile.write(current_family[q][2])
            outFile.write(' in slot ')
            outFile.write(str(curr_fam_sched[q][3]))
            outFile.write(' ; ')
            
            if(int(curr_fam_sched[q][0])<=5):
                curr_teacher = current_family[q][1]
                teacher_index = teacher_name_to_index[curr_teacher]
                LS_conf_day[teacher_index][curr_fam_sched[q][3]] = curr_fam_sched[q][2]
            else:
                US_conf_day[curr_fam_sched[q][1]][curr_fam_sched[q][3]] = curr_fam_sched[q][2]
            q = q + 1

        dayName = ''
        if(LS_conf_day==LSteacher_sched_a):
            dayName = 'Morning ;'
        else:
            dayName = 'Afternoon ;'
        
        outFile.write(dayName)
        outFile.write('\n')
        outFile.close()
     students_from_families = student_count
     outFile.close()
     print("Family students all placed.")

     
     return students_from_families
                 
     
   
def place_individual_students(sort_by_family_num):                 
    current_family = get_family(sort_by_family_num,0) #Gets all singleton students with family number of zero and stores list in current_family.
    print(len(current_family))
    
    student_count = 0
    placed_students = []
    flag = 0
    teacher_index = 0
    US_conf_day, LS_conf_day = pick_conf_day()    
    for i in range(0,len(current_family)):
            
            j = 1


            
            if(int(current_family[i][0])<=5):
                curr_teacher = current_family[i][1]
                teacher_index = teacher_name_to_index[curr_teacher]
                #print(teacher_index)

                #LS_conf_day = choose_LS_conf_balance(teacher_index)
                
                while(j<14 and LS_conf_day[teacher_index][j]!=''):
                    j= j + 1
                       
                    
                    if (j >= 14):
                        #print("Switching day...")
                        US_conf_day, LS_conf_day = switch_conf_day(US_conf_day,LS_conf_day)
                        j = 1
                        
                                   
                
                LS_conf_day[teacher_index][j] = current_family[i][2]
                
                placed_students.append(current_family[i][2])
              
                student_count = student_count + 1
                   
                i = i + 1   
                    
                   
                       
            else:
                times_switched_room = 0
                teacher_index = get_US_index(teacher_index)
                set_conf_index = 0
                
                while(set_conf_index ==0):
                                                      
                    if(US_conf_day[teacher_index][j]==''):
                        
                        if((j==5) or (j==6)):
                            #print("prohibited zone")
                            j=7
                        

#                        elif((j==11) or (j==12)):
#                            j = 13

                                       
                        
                        else:
                            set_conf_index=1
                    else:
                        if(j<=14):
                            j = j + 1
                        else:
                            #print("Switching conference room...")
                            teacher_index = get_US_index(teacher_index)
                            times_switched_room = times_switched_room + 1
                            j = 1    
                            if(times_switched_room>5):
                               US_conf_day, LS_conf_day = switch_conf_day(US_conf_day, LS_conf_day) 
                               times_switched_room = 0
   
                if(j!=5 or j!=6):
                    US_conf_day[teacher_index][j] = current_family[i][2]
                    #print(US_conf_day[teacher_index][j])    
                else:
                    print("Problem found.")
                      
                
                placed_students.append(current_family[i][2])
                #print("Currently ",len(placed_students)," students are scheduled.")
                student_count = student_count + 1
                #print("The student count is:",student_count)
                if((len(placed_students)!=i+1) and flag==0):
                        print("Problem started at", current_family[i][2])
                        print(current_family[i])
                        flag= 1
                    
                #input("Press enter to continue.")
                i = i + 1
                       
    students_individual = student_count
    print("Individual students all placed")
    return students_individual

    
def main():
    student_list = get_students_from_file('output.csv')
  
    get_LS_teachers(student_list) #Create a list of the LS teachers and their grades.
                  
    create_US_confs() #Create the list containing the schedules for the upper school conference rooms
        
    #This next line takes the list of students and their family numbers, and sorts them according to the number of children in each family.
    sort_by_family_num = sorted(student_list, reverse=True, key = get_num_of_students) 

    total_students = len(sort_by_family_num)

    total_upper_school_students = 0 #Counts the number of upper school students.
    for q in range(0,len(sort_by_family_num)):
        if(int(sort_by_family_num[q][0])>5):
            total_upper_school_students = total_upper_school_students + 1
            

    

    students_from_families = place_families_into_conf(sort_by_family_num) #Schedules families into conferences.

    students_individual = place_individual_students(sort_by_family_num) #...then schedules all individual students.

    outFile = open('Conferences.csv','w')
    outFile.write('Teacher Name ; Period 1 ; Period 2 ;  Period 3 ; Period 4 ;  Period 5 ; Period 6 ;  Period 7 ; Period 8 ; Period 9 ; Period 10 ;  Period 11; Period 12 ; Period 13 ; Period 14; Period 15')
    outFile.write('\n')

    for i in range(0,len(LSteacher_sched_a)):
        z = LSteacher_sched_a[i]
        s = z[0]
        for j in range(1,len(z)):
            s = s + ' ; ' + z[j]
        outFile.write(s)
        outFile.write('\n')

    outFile.write('\n')
    outFile.write('Upper School Conferences - Morning:\n')
    outFile.write('Conference Room: ; Period 1 ; Period 2 ;  Period 3 ; Period 4 ;  Period 5 ; Period 6 ;  Period 7 ; Period 8 ; Period 9 ; Period 10 ;  Period 11; Period 12 ; Period 13 ; Period 14; Period 15')
    outFile.write('\n')
    outFile.write('\n')       
    for i in range(0,len(US_conf_a)):
        z = US_conf_a[i]
        s = z[0]
        for j in range(1,len(z)):
            s = s + ' ; ' + z[j]
        outFile.write(s)
        outFile.write('\n')

    outFile.write('\n')
    outFile.write('Teacher Name ; Period 1 ; Period 2 ;  Period 3 ; Period 4 ;  Period 5 ; Period 6 ;  Period 7 ; Period 8 ; Period 9 ; Period 10 ;  Period 11; Period 12 ; Period 13 ; Period 14; Period 15; Period 16')
    outFile.write('\n')
    
    for i in range(0,len(LSteacher_sched_b)):
        z = LSteacher_sched_b[i]
        s = z[0]
        for j in range(1,len(z)):
            s = s + ' ; ' + z[j]
        outFile.write(s)
        outFile.write('\n')

    outFile.write('\n')
    outFile.write('Upper School Conferences - Afternoon:\n')
    outFile.write('Conference Room: ;Period 1 ; Period 2 ;  Period 3 ; Period 4 ;  Period 5 ; Period 6 ;  Period 7 ; Period 8 ; Period 9 ; Period 10 ;  Period 11; Period 12 ; Period 13 ; Period 14; Period 15; Period 16')
    outFile.write('\n')

    for i in range(0,len(US_conf_b)):
        z = US_conf_b[i]
        s = z[0]
        for j in range(1,len(z)):
            s = s + ' ; ' + z[j]
        outFile.write(s)
        outFile.write('\n')

    outFile.close()

    print(students_from_families, " students placed from families.")   
    
    print(students_individual,"students placed as individuals")

    print(total_students, "students in total.")
    print(total_upper_school_students,"of those are in the upper school.") 

    if(students_individual + students_from_families == total_students): #This serves as a check to make sure all students are appropriately scheduled.
        print("Success in placing all students!")
    else:
        print("Error in placing all students - rerun program.")

        
      
if __name__ == '__main__':
  main()

                     
