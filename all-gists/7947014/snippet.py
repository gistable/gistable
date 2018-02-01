import cx_Oracle
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)


if __name__ == "__main__":

  conn = cx_Oracle.connect(user,password,server)
  cursor = conn.cursor()
  cursor.arraysize = 10000


  for city in range("New York", "San Francisco", "Chicago", "Boston"):
    logging.info("Getting data for city:" + str(city))
  
    #sql to be executed
    sql = "select city, employee_age, employee_gender, employment_age, salary from employee_salary where city = " + str(city)
    cursor.execute( sql )

    #create dataframe from the data returned
    df = DataFrame(cursor.fetchall())
    #map the salary value to a lambda function to create the bucket
  
    # the lambda function will create bucket in a step of 50000. For e.g. 0<x<50000, 50000<x<100000 and store in the new column 'bucket'
    df['bucket'] = df[4].map(lambda x:str(int(math.floor(x/50000.0)*50000)) + "< x <" + str(int(math.ceil(x/50000.0)*50000)))

    #group by
    df2 = df.groupby([0,1,2,3,'bucket'])
    #aggregate and calculate sum, mean and count
    final = DataFrame({'sum(salary)':df2[4].sum(),'mean(salary)':df2[4].mean(), 'count(salary)':df2[4].size()}).reset_index()
    logging.info("Writing data to excel for a city:" + str(city))

    #write to excel
    final.to_excel(writer,'Sheet' + str(city))

  writer.save() 