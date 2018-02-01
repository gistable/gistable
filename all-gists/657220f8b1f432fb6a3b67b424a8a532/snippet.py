def calculate_tax (name_salary):
    name_tax = {}
    for key, value in name_salary.items():
        name_tax[key] = 0
        if value > 1000 :
            if value > 10000 :
                name_tax[key] = 900;
                if value > 20200 :
                    name_tax[key] = 2430
                    if value > 30750 :
                        name_tax[key] = 4540
                        if value > 50000 :
                            name_tax[key] = 9352.5
                            name_tax[key] = 9352.5 + ((value - 50000) * 0.3)
                        else :
                            name_tax[key] = 4540 + ((value - 30750) * 0.25)
                    else :
                        name_tax[key] = 2430 + ((value - 20200) * 0.2)
                else :
                    name_tax[key] = 900 + ((value - 10001) * 0.15)
            else :
                name_tax[key] = (value - 1000) * 0.1    
    return name_tax
        