__author__ = 'KarlTothIII'


#!/usr/bin/env python

import json
import re
import easypg


with open('authors.json') as af:
    with easypg.cursor() as cur:
        count = 0
        ak_list = []
        for line in af:
            au = json.loads(line.strip())
            key = au['key']
            rx = re.compile('\/authors\/OL(\d+)A')
            k = rx.findall(key)
            author_key = int(k[0])
            if au['name']:
                auth = au['name']
                regex = re.compile("([A-z]+[\.]*[^\s]*)")
                a = regex.findall(auth)
                cnt = 0
                for b in a:
                    cnt += 1
                if cnt == 3:
                    auth_name = a[0] + ' ' + a[1] + ' ' + a[2]
                    cur.execute('''
                        INSERT INTO author (author_id, author_name)
                        VALUES (%s, %s)
                    ''', (author_key, auth_name))
                    ak_list.append(author_key)
                    count += 1
                elif cnt == 2:
                    auth_name = a[0] + ' ' + a[1]
                    cur.execute('''
                        INSERT INTO author  (author_id, author_name)
                        VALUES (%s, %s)
                    ''', (author_key, auth_name))
                    ak_list.append(author_key)
                    count += 1
                elif cnt == 1:
                    auth_name = a[0]
                    cur.execute('''
                        INSERT INTO author (author_id, author_name)
                        VALUES (%s, %s)
                    ''', (author_key, auth_name))
                    ak_list.append(author_key)
                    count += 1
                else:
                    count = count
        print 'number of authors added to Author table:', count




with open('books.json')as af:
    with easypg.cursor() as cur:
        flagged_authors = []
        ba_cnt = 0
        bk_cnt = 0
        for line in af:
            book = json.loads(line.strip())
            flag = False
            the_author = None
            if book['authors']:
                key = book['authors']
                akey = str(key)
                rx = re.compile('\/authors\/OL(\d+)A')
                k = rx.findall(akey)
                thor = int(k[0])
                for ak in ak_list:
                    if ak == thor:
                        the_author = thor
                        flag = True
                        ba_cnt += 1
                        if ba_cnt % 1000 == 0:
                            print 'book/author count so far: ', ba_cnt
                        break
            if (flag and 'publishers' in book and 'isbn_13' in book and 'publish_date' in book and 'title' in book):
                flagged_authors.append(thor)
                bk_cnt += 1
                if bk_cnt % 1000 == 0:
                    print 'books so far: ', bk_cnt
                rx = re.compile('\/books\/OL(\d+)M')
                k = rx.findall(book['key'])
                book_key = int(k[0])
                if (book_key == 25188432):
                    print 'skip this one!'
                else:
                    publish = book['publishers']
                    publisher = publish[0]
                    title = book['title']
                    isbn_13 = book['isbn_13']
                    isbn = isbn_13[0]
                    pub = book['publish_date']
                    rx = re.compile('[\w]+')
                    parts = rx.findall(pub)
                    cnt = 0
                    for p in parts:
                        cnt += 1
                    if cnt == 3:
                        if parts[0] == 'January':
                            month = 1
                        elif parts[0] == 'February':
                            month = 2
                        elif parts[0] == 'March':
                            month = 3
                        elif parts[0] == 'April':
                            month = 4
                        elif parts[0] == 'May':
                            month = 5
                        elif parts[0] == 'June':
                            month = 6
                        elif parts[0] == 'July':
                            month = 7
                        elif parts[0] == 'August':
                            month = 8
                        elif parts[0] == 'September':
                            month = 9
                        elif parts[0] == 'October':
                            month = 10
                        elif parts[0] == 'November':
                            month = 11
                        elif parts[0] == 'December':
                            month = 12
                        else:
                            print 'date failure!!! parts[0] = ', parts[0]
                            print 'book_id = ', book_key
                        day = int(parts[1])
                        year = parts[2]
                        if day <= 9 and month <= 9:
                            publish_date = str(year) + '-0' + str(month) + '-0' + str(day)
                        elif month > 9 and day <= 9:
                            publish_date = str(year) + '-' + str(month) + '-0' + str(day)
                        elif day > 9 and month <= 9:
                            publish_date = str(year) + '-0' + str(month) + '-' + str(day)
                        elif day > 9 and month > 9:
                            publish_date = str(year) + '-' + str(month) + '-' + str(day)
                    elif cnt == 2:
                        if parts[0] == 'January':
                            month = 1
                        elif parts[0] == 'February':
                            month = 2
                        elif parts[0] == 'March':
                            month = 3
                        elif parts[0] == 'April':
                            month = 4
                        elif parts[0] == 'May':
                            month = 5
                        elif parts[0] == 'June':
                            month = 6
                        elif parts[0] == 'July':
                            month = 7
                        elif parts[0] == 'August':
                            month = 8
                        elif parts[0] == 'September':
                            month = 9
                        elif parts[0] == 'October':
                            month = 10
                        elif parts[0] == 'November':
                            month = 11
                        elif parts[0] == 'December':
                            month = 12
                        else:
                            print 'date failure!!! parts[0] = ', parts[0]
                            print 'book_id = ', book_key
                        year = parts[1]
                        if month < 10:
                            publish_date = str(year) + '-0' + str(month) + '-01'
                        else:
                            publish_date = str(year) + '-' + str(month) + '-01'
                    elif cnt == 1:
                        year = parts[0]
                        publish_date = str(year) + '-01-01'
                    if 'number_of_pages' in book:
                        num_pgs = book['number_of_pages']
                    else:
                        num_pgs = None
                    if 'edition_name' in book:
                        ed_name = book['edition_name']
                    else:
                        ed_name = None
                    if 'physical_format' in book:
                        ph_form = book['physical_format']
                    else:
                        ph_form = None
                    if ed_name:
                        cur.execute('''
                            INSERT INTO Book (book_id, title, isbn, edition)
                            VALUES (%s, %s, %s, %s)
                        ''', (book_key, title, isbn, ed_name))
                    else:
                        cur.execute('''
                            INSERT INTO Book (book_id, title, isbn)
                            VALUES (%s, %s, %s)
                        ''', (book_key, title, isbn))
                    if num_pgs and ph_form:
                        cur.execute('''
                            INSERT INTO BookDetails (book_id, publisher, pub_date, pages, cover_type, details_position)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            RETURNING book_details_id
                        ''', (book_key, publisher, publish_date, num_pgs, ph_form, 1))
                        bk_details_id, = cur.fetchone()
                    elif num_pgs:
                        cur.execute('''
                            INSERT INTO BookDetails (book_id, publisher, pub_date, pages, details_position)
                            VALUES (%s, %s, %s, %s, %s)
                            RETURNING book_details_id
                        ''', (book_key, publisher, publish_date, num_pgs, 1))
                        bk_details_id, = cur.fetchone()
                    elif ph_form:
                        cur.execute('''
                            INSERT INTO BookDetails (book_id, publisher, pub_date, cover_type, details_position)
                            VALUES (%s, %s, %s, %s, %s)
                            RETURNING book_details_id
                        ''', (book_key, publisher, publish_date, ph_form, 1))
                        bk_details_id, = cur.fetchone()
                    else:
                        cur.execute('''
                            INSERT INTO BookDetails (book_id, publisher, pub_date, details_position)
                            VALUES (%s, %s, %s, %s)
                            RETURNING book_details_id
                        ''', (book_key, publisher, publish_date, 1))
                        bk_details_id, = cur.fetchone()
                    cur.execute('''
                        INSERT INTO BookAuthor (author_id, book_details_id, author_position)
                        VALUES (%s, %s, %s)
                    ''', (the_author, bk_details_id, 1))
                    if 'subjects' in book:
                        for sub in book['subjects']:
                            if len(sub) < 50:
                                cur.execute('''
                                    INSERT INTO tag (tag_text)
                                    VALUES (%s)
                                    RETURNING tag_id
                                ''', (sub,))
                                tag_id, = cur.fetchone()
                                cur.execute('''
                                    INSERT INTO booktag (book_id, tag_id)
                                    VALUES (%s, %s)
                                ''', (book_key, tag_id))
            if bk_cnt == 3738:
                break
        print 'number of books = ', bk_cnt

        dlt_authors = 0
        for ak in ak_list:
            flag = 1
            for ba in flagged_authors:
                if ak == ba:
                    flag = 0
            if flag:
                cur.execute('''
                    DELETE FROM author WHERE author_id = %s
                ''', (ak,))
                dlt_authors += 1
                if dlt_authors % 1000 == 0:
                    print 'authors removed so far: ', dlt_authors
        new_authors = count - dlt_authors
        print 'new number of authors = ', new_authors
