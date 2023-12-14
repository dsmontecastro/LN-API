def to_isbn(isbn: str):

    if len(isbn) == 10:
        code = [
            isbn[0],
            isbn[1:3],
            isbn[3:9],
            isbn[9]
        ]
        isbn = '-'.join(code).upper()

    elif len(isbn) == 13:
        code = [
            isbn[0:3],
            isbn[3],
            isbn[4:9],
            isbn[9:12],
            isbn[12]
        ]
        isbn = '-'.join(code)
    
    return isbn