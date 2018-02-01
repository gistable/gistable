                for iconstr in constr.constraints:
                    constline = "R %i %i 0\n" % get_fix_bond_indices(iconstr)
                else:
                    constline = constline[-1]
