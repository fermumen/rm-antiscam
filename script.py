import json
import threading
import urllib.parse as urlparse
from datetime import datetime, timedelta
from random import randint, randrange
from urllib.parse import urlencode

import names
import pandas as pd
import requests
import shortuuid


def random_date():
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    start = datetime.strptime('1/1/1960 1:30 PM', '%m/%d/%Y %I:%M %p')
    end = datetime.strptime('1/1/1990 1:30 PM', '%m/%d/%Y %I:%M %p')
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)



def generate_card(type):
    """
    Prefill some values based on the card type
    """
    card_types = ["americanexpress","visa13", "visa16","mastercard","discover"]

    def prefill(t):
        # typical number of digits in credit card
        def_length = 16
        """
        Prefill with initial numbers and return it including the total number of digits
        remaining to fill
        """
        if t == card_types[0]:
            # american express starts with 3 and is 15 digits long
            # override the def lengths
            return [3, randint(4,7)], 13

        elif t == card_types[1] or t == card_types[2]:
            # visa starts with 4
            if t.endswith("16"):
                return [4], def_length - 1
            else:
                return [4], 12

        elif t == card_types[3]:
            # master card start with 5 and is 16 digits long
            return [5, randint(1,5)], def_length - 2

        elif t == card_types[4]:
            # discover card starts with 6011 and is 16 digits long
            return [6, 0, 1, 1], def_length - 4

        else:
            # this section probably not even needed here
            return [], def_length

    def finalize(nums):
        """
        Make the current generated list pass the Luhn check by checking and adding
        the last digit appropriately bia calculating the check sum
        """
        check_sum = 0

        #is_even = True if (len(nums) + 1 % 2) == 0 else False

        """
        Reason for this check offset is to figure out whether the final list is going
        to be even or odd which will affect calculating the check_sum.
        This is mainly also to avoid reversing the list back and forth which is specified
        on the Luhn algorithm.
        """
        check_offset = (len(nums) + 1) % 2

        for i, n in enumerate(nums):
            if (i + check_offset) % 2 == 0:
                n_ = n*2
                check_sum += n_ -9 if n_ > 9 else n_
            else:
                check_sum += n
        return nums + [10 - (check_sum % 10) ]

    # main body
    t = type.lower()
    if t not in card_types:
        print("Unknown type: '%s'" % type)
        print("Please pick one of these supported types: %s" % card_types)
        return

    initial, rem = prefill(t)
    so_far = initial + [randint(1,9) for x in range(rem - 1)]
    #print ("Card type: %s, " % t,)
    return "".join(map(str,finalize(so_far)))



def get_session():
    """
    When you connect for the first time you are given a Session string
    We need to extract one for each of our post requests
    """
    base_url = "https://rm-secure-delivery.com/"
    r = requests.get(base_url)
    parsed = urlparse.urlparse(r.url)
    params= urlparse.parse_qs(parsed.query)
    session=str(params['session'])
    ssl = str(params['ssl'])
    session = ''.join(e for e in session if e.isalnum())
    ssl = ''.join(e for e in ssl if e.isalnum())
    params['session'] = session
    params['ssl']=ssl
    return params



def create_url(params, service = "loading.php?"):
    '''
    Creating a url with the correct session parameters
    '''
    base_url = "https://rm-secure-delivery.com/"
    #params = get_session()
    url = base_url + service
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlencode(query)
    return urlparse.urlunparse(url_parts)



post_codes = pd.read_csv("postcodes.csv")
post_codes.pcd[(randint(0,len(post_codes.pcd)))]
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}


def loging_cards():
    while True:
        first_name = names.get_first_name()
        last_name = names.get_last_name()
        full_name = first_name + ' ' + last_name
        email =  first_name.lower() + '0' + str(randint(0,9)) +'@gmail.com'
        phone = "07" + str(randint(10000000,99999999))
        street_name = names.get_last_name() + ' St'
        dob = random_date().strftime("%m/%d/%Y")
        PC = post_codes.pcd[(randint(0,len(post_codes.pcd)))]
        card_number = generate_card('mastercard')
        card_number =  ' '.join([card_number[i:i+4] for i in range(0, len(card_number), 4)])
        # user data
        data_user = {
        "uid": shortuuid.ShortUUID().random(length=10),
        "name": full_name,
        "dob": dob,
        "email": email,
        "phone": phone,
        "address": street_name,
        "city": "London",
        "postcode": PC
        }
        # card data
        data_card = {
        "card_holderName": full_name,
        "card_number": card_number,
        "cardExpiry": (str(randint(1,12)).zfill(2) +'/'+ str(randint(22,24))),
        "cardCVC": randrange(100,999),
        "account_number": (str(randint(500,60000000)).zfill(8)),
        "sort_code": '04-00-' + str(randint(0,80)).zfill(2),
        "paymentBtn": "paymentBtn"
        }
        params = get_session()
        r1 = requests.post(url= create_url(params, service="payment.php?"), headers = headers, data=data_user)
        r = requests.post(url = create_url(params), headers = headers, data=data_card)
        print("logged: "+full_name+ ' ' +card_number+ ' > ' + str(r.status_code))


threads = list()

for i in range(50):
    x = threading.Thread(target=loging_cards)
    threads.append(x)
    x.start()

for thread in threads:
    thread.join()


