import sys, os, shutil

def generateClass(directory, classNumber, methodsPerClass, mainPackage):
    className = "Foo" + str(classNumber)
    filePath = os.path.join(directory, className + ".java")
    with open(filePath,"w+") as f:
        f.write("package " + mainPackage + "." + directory + ";\n")
        f.write("public class " + className + " {\n")
        for i in xrange(0, methodsPerClass):
            f.write("public void foo" + str(i) + "(){\n")
            if i > 0:
                f.write("foo" + str(i-1) + "();\n")
            elif classNumber > 0:
                f.write("new Foo" + str(classNumber-1) + "().foo" + str(methodsPerClass-1) + "();\n")
            f.write("}\n")
        f.write("}")

def generatePackage(packageNumber, classCounter, methodsPerClass, mainPackage):
    packageName = "package_" + str(packageNumber)
    if not os.path.exists(packageName):
        os.makedirs(packageName)
    else:
        shutil.rmtree(packageName)

    for i in xrange(0, classCounter):
        generateClass(packageName, i, methodsPerClass, mainPackage)

""" 
    4 parameters to specify:
    mainPackage - directory where generator should put all generated packages
    packageCounter - how many packages should be generated
    classCounter - how many classes should be generated in each package
    methodCounter - how many method should be generated all together (!!!)
"""
if len(sys.argv) < 5:
    print "Not enough arguments. Expected 5 arguments. But provided only ", len(sys.argv)
else:
    mainPackage = sys.argv[1]
    packageCounter = int(sys.argv[2])
    classCounter = int(sys.argv[3])
    methodCounter = int(sys.argv[4])
    methodsPerClass = methodCounter / (classCounter * packageCounter)
    print packageCounter, ' packages, ', classCounter, ' classes, ', methodCounter, ' methods, ', methodsPerClass, " methods per class"

    for i in xrange(0, packageCounter):
        generatePackage(i, classCounter, methodsPerClass, mainPackage)
