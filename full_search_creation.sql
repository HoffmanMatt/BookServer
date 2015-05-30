
-- Batch update
TRUNCATE TABLE full_text_search;
INSERT INTO full_text_search (book_id, book_terms)
  SELECT book_id,
        setweight(to_tsvector(title), 'A')
        || setweight(to_tsvector(coalesce(author_name, '')), 'A')
  FROM book
    LEFT OUTER JOIN (SELECT book_id, author_name
                      FROM bookdetails JOIN bookauthor USING (book_details_id)
                      JOIN author USING (author_id)) AS bb
    USING (book_id);

ANALYZE;
