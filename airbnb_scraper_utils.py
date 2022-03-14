from bs4 import BeautifulSoup
import requests
import numpy as np 
import pandas as pd
import re


def scrape_page(page_url):
    
    request = requests.get(page_url)
    content = request.content
    soup = BeautifulSoup(content, features='html.parser')
    
    return soup


def extract_listings(page_url):
    
    page_soup = scrape_page(page_url)
    listings = page_soup.findAll("div", {"class": "idt4x4"})

    return listings


def parse_listings(listings_list):

    out_df = pd.DataFrame()
    
    if len(listings_list) >= 1:

        for listing in listings_list:

            # title
            title = listing.find('span', {'class':'ts5gl90'}).text

            # price
            price = int(listing.find('div', {'class':'p1qe1cgb'}).text.split()[0].replace('$','').replace(',',''))
            
            # guests, bedrooms, beds, baths 
            listing_counts = listing.find('div', attrs={'class':'i1wgresd'}).findAll('span',{'class':'mp2hv9t'})
            guests = [int(re.sub('[^\d\.]','', s.string)) for s in listing_counts if 'guests' in s.string]
            bedrooms = [int(re.sub('[^\d\.]','', s.string)) for s in listing_counts if 'bedrooms' in s.string]
            beds = [int(re.sub('[^\d\.]','', s.string)) for s in listing_counts if 'beds' in s.string]
            baths = [float(re.sub('[^\d\.]','', s.string)) for s in listing_counts if 'baths' in s.string]
        

            if len(guests) < 1:
                guests = np.nan
            if len(bedrooms) < 1:
                bedrooms = np.nan
            if len(beds) < 1:
                beds = np.nan
            if len(baths) < 1:
                baths = np.nan


            # rating
            rating_string = listing.find('div', {'class':'sglmc5a'})
            if rating_string:
                rating_ = rating_string.text.split()
                rating = float(rating_[0])
                n_reviews = int(rating_[1].replace('(',''))
            else:
                rating = np.nan
                n_reviews = np.nan
                
            # listing type + location
            type_loc = listing.find('div',{'class': 'mj1p6c8'}).text.split(' in ')    
            listing_type = type_loc[0]
            listing_loc = type_loc[1]
            

            out_dict = {
                'title':[title],
                'price':[price],
                'rating':[rating],
                'guests': guests,
                'bedrooms':bedrooms,
                'beds':beds,
                'baths':baths,
                'n_reviews':[n_reviews],
                'type':[listing_type],
                'location':[listing_loc]
            }
            
            df = pd.DataFrame(out_dict)
            # print(df.head)
            out_df = out_df.append(df)

            # print('#'*20)
            # print(f"Title: {title}")
            # print(f"Price: {price}")
            # print(f"Rating: {rating}")
            # print(f"Number of Reviews: {n_reviews}")
            # print(f"Type: {listing_type}")
            # print(f"Location: {listing_loc}")
            # print('#'*20)
            # print()    
            
    else:
        print('No listings found!')


    return out_df


def scrape_listings(url):
    page_url = url
    listings_final = []
    listings = extract_listings(page_url)
    idx = 0
    listings_final = listings_final + listings

    while len(listings) > 0:
        idx += 1
        per_page_idx = 20*idx
        page_offset_string = f'&pagination_search=true&items_offset={per_page_idx}&section_offset=2'
        new_page_url = f'{page_url}{page_offset_string}'
        # print(new_page_url)
        listings = extract_listings(new_page_url)
        # print(len(listings))
        if len(listings) < 1:
            break
        else:
            listings_final = listings_final + listings
    
    return listings_final
    