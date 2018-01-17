# import wikipedia
import MySQLdb as mdb
import string


# import spotipy

def scrape_page(title, con):
    page = wikipedia.page(title)

    print "title = " + page.title
    print "id = " + page.pageid
    # for category in page.categories:
    #     print "category =" + category

    with con:
        cur = con.cursor()
        cur.execute("INSERT INTO entries (title, genre, id) VALUES(%s, %s, %s)",
                    (page.title, 'example', page.pageid))
        print "row count: " + str(cur.rowcount)


def build_prefix_suffix_dict():
    set_of_words = set()
    con = mdb.connect('localhost', 'root', 'password', "wikipedia")
    lst_of_words = ['New York City', 'bolognese sauce', 'synergy', 'nomanclature', 'heap (data structure)',
                    'grease (lubricant)', 'gridiron football', 'obviative', 'atmosphere of earth', 'level measurement']
    i = 0
    for word in lst_of_words:
        scrape_page(word, con)
        i += 1

    con.close()


if __name__ == '__main__':
    build_prefix_suffix_dict()
    # use_spotipy()
