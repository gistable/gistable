def valida_renavam(num_rnv):
    if isinstance(num_rnv, int):
        num_rnv = str(num_rnv)
    if len(num_rnv) < 11:
        num_rnv = "00" + num_rnv[:len(num_rnv)]
        
    reverse_rnv = num_rnv[9::-1]
    soma = 0
    for n in range(8):
        soma += int(reverse_rnv[n])*(n+2)
        
    soma += int(reverse_rnv[8])*2
    soma += int(reverse_rnv[9])*3
    mod11 = (soma * 10) % 11
    
    if mod11 == 10:
        mod11 = 0
    
    if int(num_rnv[10]) == mod11:        
        return True
    return False

renavams = ['25067031574', '45115592660', '58375822196', '14517939339',
            '62733210953', '63798119924', '91103775190', '10774840703',
            '30406942732', '01198179470', '12156672735', '31184681693']
renavams_int = [25067031574, 45115592660, 58375822196, 14517939339,
                62733210953, 63798119924, 91103775190, 10774840703,]

for r in renavams:
    print(valida_renavam(r))

for r in renavams_int:
    print(valida_renavam(r))