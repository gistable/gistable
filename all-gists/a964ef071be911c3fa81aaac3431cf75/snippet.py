# PyMean ?2008, Kenneth Reitz


def main():
    mean(GetNumbers())

def GetNumbers():
    number_list = []
    input_number = False
    while input_number != "":
          input_number = raw_input("Plase enter numbers to average:")
          number_list.append(input_number)
          input_number = raw_input("Plase enter numbers to average:")
    return number_list

def mean(number_list):
    sum = 0
    for i in range(len(number_list)):
        sum = (sum+number_list[i])


main()

