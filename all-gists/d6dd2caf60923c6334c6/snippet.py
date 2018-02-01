import re
import sys
from os.path import splitext, basename


class UmlClassFigGenerator(object):
    def __init__(self, file_list):
        self.file_list = file_list
        # notice: parent class was like that: "parenet_class.ClassName2"
        self.re_class_def = re.compile(r"^class\s+([\w\d]+)\(([\w\d\._]+)\):")
        self.re_method_def = re.compile(r"^\s+def (\w+)\(.*\):")
        self.re_member_def = re.compile(r"^\s+self.([_\w]+)\s*=")
        # CamelCase regexp
        self.re_class_name_call = re.compile(r"((:?[A-Z]+[a-z0-9]+)+)\(.*\)")
        self.re_ignore_line = re.compile(r"^\s*(:?$|#|raise|print)")
        self.re_private_name = re.compile(r"^_[\w\d_]+")
        self.re_special_name = re.compile(r"^__[\w_]+__")

        self.parent_dic = {}  # class inheritance relation
        self.relate_dic = {}  # other class relation
        self.class_list = []  # list of class name
        self.ignore_parents = ["object"]

        self.class_name = None
        self.member_dic = {}  # list of member val name

    def _check_name_visibility(self, name):
        if self.re_special_name.match(name):
            return "+" + name
        elif self.re_private_name.match(name):
            return "-" + name
        else:
            return "+" + name

    def _check_line_class_def(self, class_name, parent_class_name):
        if "." in parent_class_name:
            # if written by "package.classname" format
            pcn_list = parent_class_name.split(".")
            pkg = pcn_list[0:-1]
            cls = pcn_list[-1]
            # print "## pkg=%s, cls=%s" % (pkg, cls) 
            parent_class_name = cls
        if class_name in self.class_list:
            return  # is there multiple definition??
        self.class_name = class_name
        self.member_dic[class_name] = []
        self.relate_dic[class_name] = []
        self.class_list.append(class_name)
        print "  class %s" % class_name
        if parent_class_name not in self.ignore_parents:
            self.parent_dic[class_name] = parent_class_name
            # print "  %s <|-- %s" % (parent_class_name, class_name)

    def _check_line_method_def(self, method_name):
        method_name = self._check_name_visibility(method_name)
        print "  %s : %s()" % (self.class_name, method_name)

    def _check_line_member_def(self, member_name):
        member_name = self._check_name_visibility(member_name)
        if member_name not in self.member_dic[self.class_name]:
            self.member_dic[self.class_name].append(member_name)

    def _check_line_class_relation(self, called_class_name):
        # print "#call: %s in %s" % (called_class_name, class_name)
        if called_class_name not in self.relate_dic[self.class_name]:
            self.relate_dic[self.class_name].append(called_class_name)

    def _read_file(self, file_name):
        for line in open(file_name, "r"):
            if self.re_ignore_line.match(line):
                # print "# ignored: %s" % line
                continue

            # def class
            m_cdef = self.re_class_def.match(line)
            if m_cdef:
                self._check_line_class_def(m_cdef.group(1), m_cdef.group(2))
                continue

            # def method
            m_mtd = self.re_method_def.match(line)
            if m_mtd and self.class_name:
                self._check_line_method_def(m_mtd.group(1))
                continue

            # member val
            m_mval = self.re_member_def.match(line)
            if m_mval and self.class_name:
                self._check_line_member_def(m_mval.group(1))

            # instance generate
            m_call = self.re_class_name_call.search(line)
            if m_call and self.class_name:
                self._check_line_class_relation(m_call.group(1))

    def _pre_read_file(self, file_name):
        # print "## file_name=%s" % file_name
        root, ext = splitext(basename(file_name))
        self.class_name = None
        self.member_dic = {}
        print "package %s {" % root

    def _post_read_file(self):
        # print member list
        for cname, mlist in self.member_dic.items():
            for member_name in mlist:
                print "  %s : %s" % (cname, member_name)
        print "}\n"  # end package

    def _post_read_files(self):
        # parent class
        for ccls, pcls in self.parent_dic.items():
            print "%s <|-- %s" % (pcls, ccls)
        # relation of class
        for cls1, clist in self.relate_dic.items():
            for called_class_name in clist:
                if called_class_name in self.class_list and cls1 != called_class_name:
                    # print class which aws defined in files
                    print "%s -- %s" % (cls1, called_class_name)

    def _read_files(self):
        print "@startuml"
        for file_name in self.file_list:
            self._pre_read_file(file_name)
            self._read_file(file_name)
            self._post_read_file()
        self._post_read_files()
        print "@enduml"

    def gen_fig(self):
        self._read_files()

if __name__ == "__main__":
    argvs = sys.argv
    if len(argvs) < 2:
        print "usage: %s /foo/bar/*.py" % argvs[0]
        exit(1)
    argvs.pop(0) # shift
    class_fig_gen = UmlClassFigGenerator(argvs)
    class_fig_gen.gen_fig()
