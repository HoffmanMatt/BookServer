
def full_text_search(cur, query, page):
    
    p = ((page - 1) * 50)
    cur.execute('''
        SELECT book_id, title
        FROM book JOIN book_search USING (book_id)
        WHERE book_terms @@ plainto_tsquery(%s)
        ORDER BY ts_rank(book_terms, plainto_tsquery(%s)) DESC, title
        LIMIT 50 OFFSET %s
    ''', (query, query, p))

    infos = []
    for book_id, title in cur:
        infos.append({'book_id': book_id,
                      'title': title)})

    return infos
