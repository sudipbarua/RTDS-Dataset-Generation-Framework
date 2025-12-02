from browsing import Browser
import random

def main():
    # Links for normal browsing and scrolling
    twitter_link = 'https://twitter.com/ScienceMagazine'
    reddit_link = 'https://www.reddit.com/'
    tiktok_link = 'https://www.tiktok.com/en/'
    yahoo_link = 'https://de.yahoo.com/'
    msn_link = 'https://www.msn.com/de-de'

    link_list = [twitter_link, reddit_link, tiktok_link, yahoo_link, msn_link]
    search_txt = "selenium automation google search"
    browser = Browser()
    browse_list = [browser.browse_youtube,
                   browser.browse_amazon,
                   browser.browse_and_scroll,
                   browser.browse_hotels,
                   browser.browse_facebook,
                   browser.browse_google,
                   browser.browse_linkedin,
                   browser.browse_ddgo,
                   browser.auto_messenger]

    # while True:
    #     if random.choices(browse_list)[0] == browser.browse_youtube:
    #         browser.browse_youtube(yt_play_time=60)
    #     elif random.choices(browse_list)[0] == browser.browse_and_scroll:
    #         browser.browse_and_scroll(link=random.choices(link_list)[0]),
    #     else:
    #         random.choices(browse_list)[0]()
    #
    browser.browse_facebook()

if __name__ == "__main__":
    main()
