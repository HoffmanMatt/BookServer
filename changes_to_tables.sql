
CREATE TABLE "User" (
	user_id SERIAL PRIMARY KEY,
	login VARCHAR(50) NOT NULL,
	password VARCHAR(100) NOT NULL,
	name VARCHAR(100) NOT NULL,
	email VARCHAR(100) NOT NULL,
	birth_date DATE NOT NULL
);

CREATE TABLE Book (
	book_id SERIAL PRIMARY KEY,
	title VARCHAR(255) NOT NULL,
	isbn VARCHAR(20) NOT NULL,
	description TEXT,
	edition VARCHAR(100)
);

CREATE TABLE Vote (
	vote_id SERIAL PRIMARY KEY,
	number_stars SMALLINT NOT NULL,
	user_id INTEGER NOT NULL REFERENCES "User" ON DELETE CASCADE,
	book_id INTEGER NOT NULL REFERENCES Book ON DELETE CASCADE
);

CREATE TABLE FollowUser (
	follow_user_id SERIAL PRIMARY KEY,
	user_id INTEGER NOT NULL REFERENCES "User" ON DELETE CASCADE,
	friend_id INTEGER NOT NULL
);

CREATE TABLE UserList (
	user_list_id SERIAL PRIMARY KEY,
	user_id INTEGER NOT NULL REFERENCES "User" ON DELETE CASCADE,
	list_name VARCHAR NOT NULL
);

CREATE TABLE ListComment (
	list_comment_id SERIAL PRIMARY KEY,
	user_list_id INTEGER NOT NULL REFERENCES UserList ON DELETE CASCADE,
	user_id INTEGER NOT NULL REFERENCES "User" ON DELETE CASCADE,
	comment_date TIMESTAMP NOT NULL,
	commenter VARCHAR(50) NOT NULL,
	comment TEXT NOT NULL
);

CREATE TABLE BookInList (
	number_in_list SERIAL PRIMARY KEY,
	book_id INTEGER NOT NULL REFERENCES Book ON DELETE CASCADE,
	user_list_id INTEGER NOT NULL REFERENCES UserList ON DELETE CASCADE
);

CREATE TABLE Author (
	author_id SERIAL PRIMARY KEY,
	author_name VARCHAR(150) NOT NULL
);

CREATE TABLE Quote (
	quote_id SERIAL PRIMARY KEY,
	quote_text TEXT NOT NULL,
	book_id INTEGER NOT NULL REFERENCES Book ON DELETE CASCADE,
	user_id INTEGER NOT NULL REFERENCES "User" ON DELETE CASCADE,
	quote_date TIMESTAMP NOT NULL
);

CREATE TABLE QuoteRating (
	quote_rating_id SERIAL PRIMARY KEY,
	quote_id INTEGER NOT NULL REFERENCES Quote ON DELETE CASCADE,
	user_id INTEGER NOT NULL REFERENCES "User" ON DELETE CASCADE,
	quote_rating SMALLINT NOT NULL
);

CREATE TABLE BookDetails (
	book_details_id SERIAL PRIMARY KEY,
	book_id INTEGER NOT NULL REFERENCES Book ON DELETE CASCADE,
	publisher VARCHAR(150) NOT NULL,
	pub_date DATE NOT NULL,
	pages INTEGER,
	cover_type VARCHAR(50),
  details_position INTEGER NOT NULL
);

CREATE TABLE BookAuthor (
	author_id INTEGER REFERENCES Author ON DELETE CASCADE,
	book_details_id INTEGER REFERENCES BookDetails ON DELETE CASCADE,
  author_position INTEGER NOT NULL,
	PRIMARY KEY(author_id, book_details_id)
);

CREATE TABLE Tag (
	tag_id SERIAL PRIMARY KEY,
	tag_text VARCHAR(50) NOT NULL
);

CREATE TABLE BookTag (
	book_id INTEGER REFERENCES Book ON DELETE CASCADE,
	tag_id INTEGER REFERENCES Tag ON DELETE CASCADE,
	PRIMARY KEY(book_id, tag_id)
);

CREATE TABLE Review (
	review_id SERIAL PRIMARY KEY,
	review_text TEXT NOT NULL,
	book_id INTEGER NOT NULL REFERENCES Book ON DELETE CASCADE,
	review_date TIMESTAMP NOT NULL,
	user_id INTEGER NOT NULL REFERENCES "User" ON DELETE CASCADE,
	poster VARCHAR(50) NOT NULL
);

CREATE TABLE ReviewRating (
	review_rating_id SERIAL PRIMARY KEY,
	vote_choice SMALLINT NOT NULL,
	user_id INTEGER NOT	NUll REFERENCES "User" ON DELETE CASCADE,
	review_id INTEGER NOT NULL REFERENCES Review ON DELETE CASCADE
);

CREATE TABLE BooksRead (
	books_read_id SERIAL PRIMARY KEY,
	user_id INTEGER NOT NULL REFERENCES "User" ON DELETE CASCADE,
	book_id INTEGER NOT NULL REFERENCES Book ON DELETE CASCADE,
	date_read DATE NOT NULL
);

CREATE TABLE ListCommentRating (
	list_comment_rating_id SERIAL PRIMARY KEY,
	user_id INTEGER	NOT NULL REFERENCES "User" ON DELETE CASCADE,
	list_comment_id INTEGER NOT NULL REFERENCES ListComment ON DELETE CASCADE,
  comment_rating SMALLINT NOT NULL
);

CREATE INDEX user_name_idx ON "User"(name);
CREATE INDEX book_title_idx ON Book(title);
CREATE INDEX vote_user_idx ON Vote(user_id);
CREATE INDEX vote_book_idx ON Vote(book_id);
CREATE INDEX followuser_user_idx ON FollowUser(user_id);
CREATE INDEX userlist_user_idx ON UserList(user_id);
CREATE INDEX listcomment_user_idx ON ListComment(user_id);
CREATE INDEX listcomment_user_list_idx ON ListComment(user_list_id);
CREATE INDEX bookinlist_book_idx ON Book(book_id);
CREATE INDEX bookinlist_user_list_idx ON BookInList(user_list_id);
CREATE INDEX author_name_idx ON Author(author_name);
CREATE INDEX quote_book_idx ON Quote(book_id);
CREATE INDEX quote_author_idx ON Quote(author_id);
CREATE INDEX quote_user_idx ON Quote(user_id);
CREATE INDEX quoterating_quote_idx ON QuoteRating(quote_id);
CREATE INDEX quoterating_user_idx ON QuoteRating(user_id);
CREATE INDEX quoterating_rating_idx ON QuoteRating(quote_rating);
CREATE INDEX bookdetails_book_idx ON BookDetails(book_id);
CREATE INDEX bookdetails_publisher_idx ON BookDetails(publisher);
CREATE INDEX bookdetails_pub_date_idx ON BookDetails(pub_date);
CREATE INDEX bookauthor_author_idx ON BookAuthor(author_id);
CREATE INDEX bookauthor_book_details_idx ON BookAuthor(book_details_id);
CREATE INDEX review_book_idx ON Review(book_id);
CREATE INDEX review_user_idx ON Review(user_id);
CREATE INDEX review_date_idx ON Review(review_date);
CREATE INDEX reviewrating_user_idx ON ReviewRating(user_id);
CREATE INDEX reviewrating_review_idx ON ReviewRating(review_id);
CREATE INDEX reviewrating_vote_choice_idx ON ReviewRating(vote_choice);
CREATE INDEX booksread_user_idx ON BooksRead(user_id);
CREATE INDEX booksread_book_idx ON BooksRead(book_id);
CREATE INDEX booksread_date_read_idx ON BooksRead(date_read);

DROP TABLE IF EXISTS full_text_search CASCADE;
CREATE TABLE full_text_search (
  book_id INTEGER PRIMARY KEY REFERENCES book ON DELETE CASCADE,
  book_terms TSVECTOR NOT NULL
);
CREATE INDEX full_text_search_idx ON full_text_search USING gin(book_terms);

ANALYZE;



