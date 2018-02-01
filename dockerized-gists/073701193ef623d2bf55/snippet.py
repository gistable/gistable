def loadJar(jarFile):
    '''load a jar at runtime using the system Classloader (needed for JDBC)

    adapted from http://forum.java.sun.com/thread.jspa?threadID=300557
    Author: Steve (SG) Langer Jan 2007 translated the above Java to Jython
    Reference: https://wiki.python.org/jython/JythonMonthly/Articles/January2007/3
    Author: seansummers@gmail.com simplified and updated for jython-2.5.3b3+

    >>> loadJar('jtds-1.3.1.jar')
    >>> from java import lang, sql
    >>> lang.Class.forName('net.sourceforge.jtds.jdbc.Driver')
    <type 'net.sourceforge.jtds.jdbc.Driver'>
    >>> sql.DriverManager.getDriver('jdbc:jtds://server')
    jTDS 1.3.1
    '''
    from java import io, net, lang
    u = io.File(jarFile).toURL() if type(jarFile) <> net.URL else jarFile
    m = net.URLClassLoader.getDeclaredMethod('addURL', [net.URL])
    m.accessible = 1
    m.invoke(lang.ClassLoader.getSystemClassLoader(), [u])

if __name__ == '__main__':
    import doctest
    doctest.testmod()
