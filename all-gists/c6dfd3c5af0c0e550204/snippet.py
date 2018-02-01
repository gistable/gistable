def open_file(file_name):
    file_object = open(file_name, 'r', encoding = 'ISO-8859-1')
    return file_object


def water_calculator(weight, activity_leveler, size):
    ounces = ((weight * (2/3))+((activity_leveler/30)*12))
    total_ounces = ounces*size
    return total_ounces
 
 
def calorie_calculator(age, sex, activity_level, size):
    if age > 3:
            if 3 <= age < 8:
                if sex == 'M':
                        print ('M')
                        print ("child")
                        if activity_level == 'sedentary':
                            calories = size*1400
                        elif activity_level == 'moderate':
                             calories = size * 1500
                        elif activity_level == 'active':
                            calories = size * 1800

                elif sex == 'F':
                        print ('F')
                        print ('child')
                        if activity_level == 'sedentary':
                            calories = size * 1400
                        elif activity_level == 'moderate':
                            calories = size * 1500
                        elif activity_level == 'active':
                            calories = size * 1600

            elif 8 <= age < 13:
                if sex == 'M':
                        print ('M')
                        print ("big kid")
                        if activity_level == 'sedentary':
                            calories = size * 1800
                        elif activity_level == 'moderate':
                            calories = size * 2000
                        elif activity_level == 'active':
                            calories = size * 2300

                elif sex == 'F':
                        print ('F')
                        print ('big kid')
                        if activity_level == 'sedentary':
                            calories = size * 1600
                        elif activity_level == 'moderate':
                            calories = size * 1800
                        elif activity_level == 'active':
                            calories = size * 2000

            elif 13 <= age < 18:
                if sex == 'M':
                        print ('M')
                        print('teen')
                        if activity_level == 'sedentary':
                            calories = size * 2200
                        elif activity_level == 'moderate':
                            calories = size * 2600
                        elif activity_level == 'active':
                            calories = size * 3000

                elif sex == ('F'):
                        print ('F')
                        print ('teen')
                        if activity_level == 'sedentary':
                            calories = size * 1800
                        elif activity_level == 'moderate':
                            calories = size * 2000
                        elif activity_level == 'active':
                            calories = size * 2400

            elif 18 <= age < 30:
                if sex == 'M':
                        print ('M')
                        print ('young adult')
                        if activity_level == 'sedentary':
                            calories = size * 2400
                        elif activity_level == 'moderate':
                            calories = size * 2700
                        elif activity_level == 'active':
                            calories = size * 3000

                elif sex == 'F':
                        print ('F')
                        print ('young adult')
                        if activity_level == 'sedentary':
                            calories = size * 2000
                        elif activity_level == 'moderate':
                            calories = size * 2100
                        elif activity_level == 'active':
                            calories = size * 2400

            elif 30 <= age < 50:
                if sex == 'M':
                        print ('M')
                        print ('middle aged')
                        if activity_level == 'sedentary':
                            calories = size * 2200
                        elif activity_level == 'moderate':
                            calories = size * 2500
                        elif activity_level == 'active':
                            calories = size * 2900

                elif sex == 'F':
                        print ('F')
                        print ('middle aged')
                        if activity_level == 'sedentary':
                            calories = size * 1800
                        elif activity_level == 'moderate':
                            calories = size * 2000
                        elif activity_level == 'active':
                            calories = size * 2200

            elif 50 < age < 150:
                if sex == 'M':
                        print ('M')
                        print ('old')
                        if activity_level == 'sedentary':
                            calories = size * 2000
                        elif activity_level == 'moderate':
                            calories = size * 2300
                        elif activity_level == 'active':
                            calories = size * 2600

                        
                elif sex == 'F':
                        print ('F')
                        print ('old')
                        if activity_level == 'sedentary':
                            calories = size * 1600
                        elif activity_level == 'moderate':
                            calories = size * 1800
                        elif activity_level == 'active':
                            calories = size * 2100

    else:
        print ("baby")
        if activity_level == 'sedentary':
            calories = size * 1000
        elif activity_level == 'moderate':
            calories = size * 1200
        elif activity_level == 'active':
            calories = size * 1400

    return calories

def construct_dict(file_object):
    mydict = {}
    country_list = []
    year_list = []
    for line in file_object:
        lister = line.strip().split(',')
        new_list = []
        country_name = lister[0]
        #print (country_name)
        new_list.append(country_name)
        n = 1
        #print (lister)
        while n < 59:
            try:
                population = lister[n]
                #print (population)
                new_list.append(population)
                n += 1
            except IndexError:
                n += 1
        mydict[country_name]=new_list
        country_list.append(country_name)
        if country_name == 'Country Name':
            year_list = lister[3:]
            #print (year_list)
    country_list = country_list[3:]
    #print (country_list)
    return mydict

def total_population (mydict):
    n = 5
    year = 1960
    annual_population = 0
    year_dict = {}
    for key in mydict:
        if key == "World":
            lister = []
            for i in mydict[key]:
                lister.append(i)
            while n < 59:
                try:
                    annual_population = int(lister[n])
                    year_dict[year] = annual_population
                    #print (year, annual_population)
                    year += 1
                    n += 1
                except IndexError:
                    #print ("error")
                    n += 1
                except ValueError:
                    #print ("error")
                    n += 1 
    return year_dict

def year_population (year_dict, year):
    mini_dict = {}
    for key in year_dict:
        if key == year:
            #print (year, year_dict[key])
            mini_dict[year] = year_dict[key]
    return mini_dict
            

def country_population (mydict, year, country):
    n = year - 1955
    population = 0
    for key in mydict:
        if key == country:
            population = mydict[key][n]
    mini_dict = {}
    country_year = ""
    country_year = country + ", " + str(year)
    #print (country_year)
    #print (country, year, population)
    mini_dict[country_year] = population
    return mini_dict

def run_calculator():
        sex = input("Enter sex, M or F:")
        age = int(input("Enter age:"))
        weight = int(input("Please enter your weight:"))
        activity_level = input("Enter activity level (sedentary, moderate, or active:)")
        activity_leveler = int(input("Please enter how many minutes a day you work out:"))
        size = int(input("Enter size of population:"))
        water = water_calculator(weight, activity_leveler, size)
        food = calorie_calculator(age, sex, activity_level, size)
        print ("{} ounces of water and {} calories".format(str(water), food))

def print_entry(dicter):
    for key in dicter:
        print (key, dicter[key])
    

def main():
    print ("Type 'manual' to manually input calculator values.")
    print ("Type 'world' to view population over time.")
    print ("Type 'year' to view population for a specific year")
    print ("Type 'country' to view population for a specific year in a specific country.")
    print ("Type 'world calculator' to calculate food and water needs worldwide over time.")
    print ("Type 'year calculator' to calculate food and water needs for a specific year.")
    print ("Type 'country calculator' to calculate food and water needs for a specific year in a specific country.'")
    print ("Type 'q' to quit.")
    continuity = input ("Please enter text:")
    file = open_file('sp.pop.totl_Indicator_en_csv_v2.csv')
    mydict = construct_dict(file)
    year_dict = total_population (mydict)
    while continuity != "q":
        if continuity == "manual":
            run_calculator()
        elif continuity == "world":
            print_entry(year_dict)
        elif continuity == "year":
            year = int(input("Please enter a year: "))
            mini_year = year_population (year_dict, year)
            print_entry(mini_year)
        elif continuity == "country":
            year = int(input("Please enter a year: "))
            country = input ("Please enter a country: ")
            mini_pop = country_population (mydict, year, country)
            print_entry(mini_pop)
        else:
            print ("This feature is still under development.")
        print ("Type 'manual' to manually input calculator values.")
        print ("Type 'world' to view population over time.")
        print ("Type 'year' to view population for a specific year")
        print ("Type 'country' to view population for a specific year in a specific country.")
        print ("Type 'world calculator' to calculate food and water needs worldwide over time.")
        print ("Type 'year calculator' to calculate food and water needs for a specific year.")
        print ("Type 'country calculator' to calculate food and water needs for a specific year in a specific country.'")
        print ("Type 'q' to quit.")
        continuity = input ("Please enter text:")

        
            
            
    if continuity == "stats":
        
        year_dict = total_population (mydict)
        mini_year = year_population (year_dict, 1965)
        mini_pop = country_population (mydict, 1965, 'Afghanistan')

        continuity = input ("Press enter to continue: ")

main()
                   

##def print_entry(db, state, county):
##    for key in db:
##        if db[key][0]== state:
##            if db[key][1]== county:
##        #print (key)#('{}{}'.format(i[0],i[1]))
##                lister = []
##                for i in db[key]:
##                    lister.append(i)
##            #print (i)
##            #print(lister)
##                print ("County with the smallest population: ")
##                print ("State name = {}".format(lister[0]))
##                print ("County name = {}".format(lister[1]))
##                print ("PopEst = {}".format(lister[2]))
##                print ("Births = {}".format(lister[3]))
##                print ("NetMigr = {}".format(lister[4]))
##
##def print_stats(db):
##    min = 1000000000000000
##    max = 0
##    count = 0
##    total = 0
##    for i in db:
##        try:
##            j = int(db[i][2])
##            if j < min:
##                min = j
##                min_state = db[i][0]
##                min_county = db[i][1]
##                min_pop = db[i][2]
##                min_births = db[i][3]
##                min_mig = db[i][4]
##            if j > max:
##                max = j
##                max_state = db[i][0]
##                max_county = db[i][1]
##                max_pop = db[i][2]
##                max_births = db[i][3]
##                max_mig = db[i][4]
##            count += 1
##            total += j
##        except:
##            continue
##    print ("County with the largest population: ")
##    print ("State name = {}".format(max_state))
##    print ("County name = {}".format(max_county))
##    print ("PopEst = {}".format(max_pop))
##    print ("Births = {}".format(max_births))
##    print ("NetMigr = {}".format(max_mig))
##
##    print ("County with the smallest population: ")
##    print ("State name = {}".format(min_state))
##    print ("County name = {}".format(min_county))
##    print ("PopEst = {}".format(min_pop))
##    print ("Births = {}".format(min_births))
##    print ("NetMigr = {}".format(min_mig))
##   
##def main():
##    db = open_file()
##    #print_dict(db)
##    print_stats(db)
##    state = 'la'
##    county = 'la'
##    while state != 'q' and county != 'q':
##        state = input("Please enter state, enter q to quit: ")
##        if state == 'q':
##            break
##        county = input("Please enter county, enter q to quit: ")
##        print_entry(db, state, county)
##        
##
##
##main()

