p :: Parser String
p = do char '['
       d <- digit
       ds <- many (do {char ','; digit})
       char ']'
       return (d:ds)

char '[' >>= \_ ->
digit >>= \d ->
digits >>= \ds ->
char ']' >>= _ ->
f d ds
