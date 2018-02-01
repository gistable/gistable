#/usr/bin/python3

print("Press 'Ctrl+C' to exit this tool.")
try:
    while True:
        print("\nPlease input price in BDT: ")
        a = float(input())
        b=a+((a*5)/100)
        c=b+((b*15)/100)
        d=c+((a*1)/100)
        print("Total price with tax:", round(d, 2), "BDT")
except KeyboardInterrupt:
    print("This tool has been exited successfully.")