def adjust(t, og):
    t2 = 1.34722124e-4 * t
    t3 = 2.04052596e-6 * t ** 2
    t4 = 2.32820948e-9 * t ** 3
    sgcf = 1.00130346 - t2 + t3 - t4
    sg = og * sgcf
    adjusted_og = sg
    OE = -668.962 + 1262.45 * sg - 776.43 * sg * sg + 182.94 * sg * sg * sg
    abv_max = (sg - 1) * 105 * 1.25

    return adjusted_og, OE, abv_max


def profile(t1, t2, og, fg):
    adjusted_og, OE, abv_max1 = adjust(t1, og)
    adjusted_fg, AE, abv_max2 = adjust(t2, fg)
    q = .22 + 0.001 * OE
    RE = (q * OE + AE) / (1 + q)

    RA = (OE - RE) / OE * 100

    abw = (OE - RE) / (2.0665 - 0.010665 * OE)

    abv = abw * adjusted_fg / 0.794

    cal = 3.55 * adjusted_fg * (4.08 * RE + 7.1 * abw)

    return adjusted_fg, RE, RA, abw, abv, cal

if __name__ == "__main__":
    t1 = float(raw_input("Starting temp. (F):   "))
    og = float(raw_input("Original specific gravity (OG):   "))
    adjusted_og, OE, abv_max = adjust(t1, og)
    print
    print "Adjusted OG: ", adjusted_og
    print "Original extract: ", OE, "%"
    print "Maximum potential ABV: ", abv_max, "%"
    print
    t2 = float(raw_input("Final temp. (F):   "))
    fg = float(raw_input("Final specific gravity (FG):   "))
    adjusted_fg, RE, RA, abw, abv, cal = profile(t1, t2, og, fg)
    print
    print "Adjusted FG: ", adjusted_fg
    print "Real extract: ", RE, "%"
    print "Real attenuation: ", RA, "%"
    print "Alcohol (by weight) : ", abw, "%"
    print "Alcohol (by volume) : ", abv, "%"
    print "Calories (12 fl oz.): ", cal
    print
    raw_input("Press return to quit.")
