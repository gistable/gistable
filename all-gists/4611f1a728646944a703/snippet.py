
# First, we went over doing some basic math
# and using variables
year = 2016
year_born = 1983
age = year - year_born
dog_years = age/7

print(dog_years)

# Then we went over strings and string concatenation
dog_name = 'Biscuit'
breed = "Pug"

sentence = dog_name + ' is a ' + breed
print(sentence)

# Then we looked at string manipulation
word = 'Python'
#       0123456 <-- indexes of each character

first = word[0]
print('The first letter is', first)

# And string slices
end = word[1:6]
print('The end of the word is', end)

# Python --> ython-Pay, Pig Latin
pig_latin = end + '-' + first + 'ay'
print(pig_latin)

# Getting user input from the console is like printing
time_of_day = input('What time of day is it?  ')
print(time_of_day)

# Some basic conditionals
if time_of_day == 'morning':
    print('Top o the morning to you!')
elif time_of_day == 'afternoon':
    print("Awesome let's get coffee")
else:
    print('This day is dragging')

print('OUtside of the conditional')

# Our final example imported the request module to talk to
# the Open Weather API to get today's temperature
import requests

r = requests.get('http://api.openweathermap.org/data/2.5/weather?q=Orlando,fl&units=imperial&appid=f641b59e03463c808393605f493b1f93')
weather_json = r.json()
temp = weather_json['main']['temp']
print('The temperature today is', temp)
