#!/usr/bin/env python

import lief

shellx = lief.parse("libshellx-2.10.3.1.so")


# .dynsym
dt_symtab = shellx[lief.ELF.DYNAMIC_TAGS.SYMTAB]
dynsym_section = shellx.get_section(".dynsym")

dynsym_section.virtual_address = dt_symtab.value
dynsym_section.offset          = shellx.virtual_address_to_offset(dt_symtab.value)
dynsym_section.size            = len(shellx.dynamic_symbols) * 0x10

# .dynstr
dt_strtab = shellx[lief.ELF.DYNAMIC_TAGS.STRTAB]
dynstr_section = shellx.get_section(".dynstr")

dynstr_section.virtual_address = dt_strtab.value
dynstr_section.offset          = shellx.virtual_address_to_offset(dt_strtab.value)
dynstr_section.size            = shellx[lief.ELF.DYNAMIC_TAGS.STRSZ].value

# .init_array
dt_init_array = shellx[lief.ELF.DYNAMIC_TAGS.INIT_ARRAY]
init_array_section = shellx.get_section(".init_array")

init_array_section.virtual_address = dt_init_array.value
init_array_section.offset          = shellx.virtual_address_to_offset(dt_init_array.value)
init_array_section.size            = len(dt_init_array.array) * 4

# .fini_array
dt_fini_array = shellx[lief.ELF.DYNAMIC_TAGS.FINI_ARRAY]
fini_array_section = shellx.get_section(".fini_array")

fini_array_section.virtual_address = dt_fini_array.value
fini_array_section.offset          = shellx.virtual_address_to_offset(dt_fini_array.value)
fini_array_section.size            = len(dt_fini_array.array) * 4

# .rel.dyn
dt_rel = shellx[lief.ELF.DYNAMIC_TAGS.REL]
rel_dyn_section = shellx.get_section(".rel.dyn")

rel_dyn_section.virtual_address = dt_rel.value
rel_dyn_section.offset          = shellx.virtual_address_to_offset(dt_rel.value)
rel_dyn_section.size            = shellx[lief.ELF.DYNAMIC_TAGS.RELSZ].value

# .rel.plt
dt_pltrel = shellx[lief.ELF.DYNAMIC_TAGS.JMPREL]
rel_plt_section = shellx.get_section(".rel.plt")

rel_plt_section.virtual_address = dt_pltrel.value
rel_plt_section.offset          = shellx.virtual_address_to_offset(dt_pltrel.value)
rel_plt_section.size            = shellx[lief.ELF.DYNAMIC_TAGS.PLTRELSZ].value

# .hash
dt_hash = shellx[lief.ELF.DYNAMIC_TAGS.HASH]
hash_section = shellx.get_section(".hash")

hash_section.virtual_address = dt_hash.value
hash_section.offset          = shellx.virtual_address_to_offset(dt_hash.value)
hash_section.size            = 0x200

# .plt section: Guessing
plt_section = shellx.get_section(".plt")

plt_section.virtual_address = 0x8d0
plt_section.offset          = plt_section.virtual_address
plt_section.size            = 0xb80 - 0x8d0

# .text
text_section = shellx.get_section(".text")

code_start = min(*[e.value for e in shellx.exported_symbols if e.value > 0])
code_start = min(code_start, *[c for c in dt_init_array.array if c > 0])
code_start = min(code_start, *[c for c in dt_fini_array.array if c > 0])

code_end = max(*[e.value for e in shellx.exported_symbols if e.value > 0])
code_end = max(code_start, *[c for c in dt_init_array.array if c > 0])
code_end = max(code_start, *[c for c in dt_fini_array.array if c > 0])

code_end = max(*[e.value for e in shellx.exported_symbols], *[c for c in dt_fini_array.array])
code_size = code_end - code_start
print("Assembly code: 0x{:06x} - 0x{:06x}".format(code_start, code_end))

text_section.virtual_address = code_start
text_section.offset = code_start

# First PT_LOAD
shellx.write("libshellx-2.10.3.1_FIXED.so")
