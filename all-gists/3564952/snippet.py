import sqlite3

# ***************************************************
# *
# * Description: Python操作SQLite3数据库辅助类(查询构造器)
# * Author: wangye
# * Website: http://wangye.org
# *
# ***************************************************

def _wrap_value(value):
    return repr(value)
    
def _wrap_values(values):
    return list(map(_wrap_value, values))
        
def _wrap_fields(fields):
    for key,value in fields.items():
        fields[key] = _wrap_value(value)
    return fields

def _concat_keys(keys):
    return "[" + "],[".join(keys) + "]"
    
def _concat_values(values):
    return ",".join(values)

def _concat_fields(fields, operator = (None, ",")):
    if operator:
        unit_operator, group_operator = operator
    # fields = _wrap_fields(fields)
    compiled = []
    for key,value in fields.items():
        compiled.append("[" + key + "]")
        if unit_operator:
            compiled.append(unit_operator)
            compiled.append(value)
        compiled.append(group_operator)
    compiled.pop() # pop last group_operator
    return " ".join(compiled)
    
class DataCondition(object):
    """
        本类用于操作SQL构造器辅助类的条件语句部分
        
        例如:
        DataCondition(("=", "AND"), id = 26)
        DataCondition(("=", "AND"), True, id = 26)
    """
    
    def __init__(self, operator = ("=", "AND"), ingroup = True, **kwargs):
        """
            构造方法
            参数:
                operator 操作符，分为(表达式操作符, 条件运算符)
                ingroup  是否分组，如果分组，将以括号包含
                kwargs   键值元组，包含数据库表的列名以及值
                         注意这里的等于号不等于实际生成SQL语句符号
                         实际符号是由operator[0]控制的
            例如:
            DataCondition(("=", "AND"), id = 26)
            (id=26)
            DataCondition((">", "OR"), id = 26, age = 35)
            (id>26 OR age>35)
            DataCondition(("LIKE", "OR"), False, name = "John", company = "Google")
            name LIKE 'John' OR company LIKE "Google"
        """
        self.ingroup = ingroup
        self.fields = kwargs
        self.operator = operator
    
    def __unicode__(self):
        self.fields = _wrap_fields(self.fields)
        result = _concat_fields(self.fields, self.operator)
        if self.ingroup:
            return "(" + result + ")"
        return result
    
    def __str__(self):
        return self.__unicode__()
    
    def toString(self):
        return self.__unicode__()
        
class DataHelper(object):
    
    """
        SQLite3 数据查询辅助类
    """
    
    def __init__(self, filename):
        """
            构造方法
            参数: filename 为SQLite3 数据库文件名
        """
        self.file_name = filename
        
    def open(self):
        """
            打开数据库并设置游标
        """
        self.connection = sqlite3.connect(self.file_name)
        self.cursor = self.connection.cursor()
        return self
        
    def close(self):
        """
            关闭数据库，注意若不显式调用此方法，
            在类被回收时也会尝试调用
        """
        if hasattr(self, "connection") and self.connection:
            self.connection.close()
    
    def __del__(self):
        """
            析构方法，做一些清理工作
        """
        self.close()
    
    def commit(self):
        """
            提交事务
            SELECT语句不需要此操作，默认的execute方法的
            commit_at_once设为True会隐式调用此方法，
            否则就需要显示调用本方法。
        """
        self.connection.commit()
        
    def execute(self, sql = None, commit_at_once = True):
        """
            执行SQL语句
            参数:
                sql  要执行的SQL语句，若为None，则调用构造器生成的SQL语句。
                commit_at_once 是否立即提交事务，如果不立即提交，
                对于非查询操作，则需要调用commit显式提交。
        """
        if not sql:
            sql = self.sql
        self.cursor.execute(sql)
        if commit_at_once:
            self.commit()
    
    def fetchone(self, sql = None):
        """
            取一条记录
        """
        self.execute(sql, False)
        return self.cursor.fetchone()
        
    def fetchall(self, sql = None):
        """
            取所有记录
        """
        self.execute(sql, False)
        return self.cursor.fetchall()
        
    def __concat_keys(self, keys):
        return _concat_keys(keys)
    
    def __concat_values(self, values):
        return _concat_values(values)
        
    def table(self, *args):
        """
            设置查询的表，多个表名用逗号分隔
        """
        self.tables = args
        self.tables_snippet = self.__concat_keys(self.tables)
        return self
    
    def __wrap_value(self, value):
        return _wrap_value(value)
    
    def __wrap_values(self, values):
        return _wrap_values(values)
        
    def __wrap_fields(self, fields):
        return _wrap_fields(fields)
    
    def __where(self):
        # self.condition_snippet
        if hasattr(self, "condition_snippet"):
            self.where_snippet = " WHERE " + self.condition_snippet
            
    def __select(self):
        template = "SELECT %(keys)s FROM %(tables)s"
        body_snippet_fields = {
            "tables" : self.tables_snippet,
            "keys" : self.__concat_keys(self.body_keys), 
        }
        self.sql = template % body_snippet_fields
        
    def __insert(self):
        template = "INSERT INTO %(tables)s (%(keys)s) VALUES (%(values)s)"
        body_snippet_fields = {
            "tables" : self.tables_snippet,
            "keys" : self.__concat_keys(list(self.body_fields.keys())),
            "values" : self.__concat_values(list(self.body_fields.values()))
        }
        self.sql = template % body_snippet_fields
        
    def __update(self):
        template = "UPDATE %(tables)s SET %(fields)s"
        body_snippet_fields = {
            "tables" : self.tables_snippet,
            "fields" : _concat_fields(self.body_fields, ("=",","))
        }
        self.sql = template % body_snippet_fields
        
    def __delete(self):
        template = "DELETE FROM %(tables)s"
        body_snippet_fields = {
            "tables" : self.tables_snippet
        }
        self.sql = template % body_snippet_fields
        
    def __build(self):
        {
            "SELECT": self.__select,
            "INSERT": self.__insert,
            "UPDATE": self.__update,
            "DELETE": self.__delete
        }[self.current_token]()
 
    def __unicode__(self):
        return self.sql
        
    def __str__(self):
        return self.__unicode__()
    
    def select(self, *args):
        self.current_token = "SELECT"
        self.body_keys = args
        self.__build()
        return self
        
    def insert(self, **kwargs):
        self.current_token = "INSERT"
        self.body_fields = self.__wrap_fields(kwargs)
        self.__build()
        return self
    
    def update(self, **kwargs):
        self.current_token = "UPDATE"
        self.body_fields = self.__wrap_fields(kwargs)
        self.__build()
        return self
        
    def delete(self, *conditions):
        self.current_token = "DELETE"
        self.__build()
        #if *conditions:
        self.where(*conditions)
        return self
        
    def where(self, *conditions):
        conditions = list(map(str, conditions))
        self.condition_snippet = " AND ".join(conditions)
        self.__where()
        if hasattr(self, "where_snippet"):
            self.sql += self.where_snippet
        return self

# 下面举几个例子供大家参考吧：

db = DataHelper("\home\wangye\sample.db3")
db.open() # 打开数据库
db.execute("""
    CREATE TABLE [staffs] (
      [staff_id] INTEGER PRIMARY KEY AUTOINCREMENT,
      [staff_name] TEXT NOT NULL,
      [staff_cardnum] TEXT NOT NULL,
      [staff_reserved] INTEGER NOT NULL
)
""") # 直接执行SQL语句，注意这里commit_at_once默认为True

db.table("staffs").insert(staff_name="John", staff_cardnum="1001", staff_reserved=0)
# 插入一条记录

rs = db.table("staffs").select("staff_id", "staff_name").fetchall()
# 直接取出所有staff_id和staff_name

rs = db.table("staffs").select("staff_name").where(DataCondition(("=", "AND"), id = 1)).fetchone()
# 取一条staff_id为1的staff_name

rs = db.table("staffs").select("staff_name").where(DataCondition(("<", "AND"), id = 100), DataCondition(("=", "AND"), staff_reserved = 1)).fetchone()
# 取一条id小于100并且staff_reserved为1的staff_name记录

db.close() # 关闭数据库