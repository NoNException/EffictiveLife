# read the clipboard's content and open xls from it

import xerox

xerox.copy(u'some string')
str1 = str(xerox.paste())
