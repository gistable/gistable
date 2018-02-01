import idaapi
import idc

class MemoryPattern(object):
    def __init__(self, pattern, wildcards, patch):
        self._pattern = pattern
        self._wildcards = wildcards
        self._patch = patch

    def compareTo(self, buffer, offset):
        if offset + len(self._pattern) > len(buffer):
            return False

        for i in range(0, len(self._pattern)):
            if i in self._wildcards:
                continue

            if buffer[offset + i] == chr(self._pattern[i]):
                continue

            return False

        return True

    def getPatch(self):
        return self._patch

class Program(object):
    def __init__(self):
        self._pattern_list = []

        # .text:000000000045210C C6 45 EB 44            mov     [rbp+var_15], 44h
        # .text:0000000000452110 80 7D EB 44            cmp     [rbp+var_15], 44h
        # .text:0000000000452114 0F 85 B3 89 00 00      jnz     loc_45AACD      
        self._pattern_list.append(MemoryPattern([0xC6, 0x45, 0xEB, 0x44, 0x80, 0x7D, 0xEB, 0x44, 0x0F, 0x85, 0xB3, 0x89, 0x00, 0x00], [2, 3, 6, 7, 10, 11], [0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90]))

    def Main(self):
        for segment_start_address in Segments():
            segment_end_address = SegEnd(segment_start_address)
            segment_name = SegName(segment_start_address)
            segment_attributes = GetSegmentAttr(segment_start_address, SEGATTR_PERM)

            if segment_attributes & idaapi.SEGPERM_EXEC == 0:
                print("Skipping segment " + segment_name + " because it is not marked as executable")
                continue

            print "Scanning segment " + segment_name + " (start address: " + str(segment_start_address) + ", end address: " + str(segment_end_address) + ")"
            buffer = self._readProcessMemory(segment_start_address, segment_end_address)
            if len(buffer) == 0:
                print("Could not access the segment data")
                return 1

            self._scanSegment(buffer, segment_start_address)

        return 0

    def _readProcessMemory(self, start_address, end_address):
        buffer = []

        for address in range(start_address, end_address):
            buffer.append(chr(Byte(address)))

        return buffer

    def _scanSegment(self, buffer, segment_start_address):
        offset = 0
        reanalyze_segment = False

        while offset < len(buffer):
            for pattern in self._pattern_list:
                if pattern.compareTo(buffer, offset) == False:
                    continue

                patch_address = segment_start_address + offset
                print "Patching following address: 0x%x" % patch_address
                self._patchDatabase(pattern.getPatch(), patch_address)

                offset += len(pattern.getPatch()) - 1
                reanalyze_segment = True

                break

            offset += 1

        if reanalyze_segment:
            print("Reanalyzing segment...")
            idaapi.analyze_area(segment_start_address, segment_start_address + len(buffer))

        return

    def _patchDatabase(self, patch_buffer, address):
        for i in range(0, len(patch_buffer)):
            idc.PatchByte(address + i, patch_buffer[i])

program = Program()
exit_code = program.Main()
print("Terminating with exit code " + str(exit_code))
