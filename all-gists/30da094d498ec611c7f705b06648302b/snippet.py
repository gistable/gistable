import subprocess
import re

# Store the output of pacman -Qq in a list, i.e. the name of all packages
pack_command = subprocess.getoutput("pacman -Qq")
packages_list = pack_command.splitlines()

# Store the output of paclog --package=pack_name for all packages in a list
# Even though the format of the list is pretty ugly.
pac_log = []
for pack_name in packages_list:
    pac_log.append(subprocess.getoutput('paclog --package=' + pack_name))

# For each entry of the above paclog list, check how many times there is ' installed' (notice the white space,
# this is to omit reinstallations) and 'upgraded'. Then we add the 2 numbers, these are the ones I decided to plot, but
# you can modify this part as you wish.
result_num = []
for entry in pac_log:
    n_installs = entry.count(' installed')
    n_upgrades = entry.count('upgraded')
    n_total = n_installs + n_upgrades
    result_num.append(n_total)

# Create a 'list' (not sure if a zip is a list or not... looks like not) of tuples. 1st entry in the tuple is the 
# name of the package, 2nd entry is number of installations + upgrades
zipped = zip(packages_list, result_num)

# Now display the result as a histogram or barplot, etc.
import matplotlib.pyplot as plt

# Create the y axis
zipped_f = list(zipped)
y_axis = []
for i in range(len(zipped_f)): 
    y_axis.append(zipped_f[i][1])
    
# Create the x axis
x_axis = []
for i in range(len(zipped_f)):
    x_axis.append(zipped_f[i][0])


# Plotting part
# I'd like to plot on the x_axis the name of the packages and on the y_axis the number of installation + upgrades.


plt.bar(range(len(x_axis)), y_axis)
plt.xlabel('packages')
plt.ylabel('Number of installation + upgrades')


# Here I chose to display the name of the packages which were installed + upgraded more than 7 times, but you can of course modify this 
# according to your like. If I had an older Arch install, I'd probably increase that number.
x_tick = []
pkg_index = []
for i in range(len(y_axis)):
    if y_axis[i] > 7:
        x_tick.append(x_axis[i])
        pkg_index.append(i)
plt.xticks(pkg_index, x_tick, rotation=90)

plt.show()
