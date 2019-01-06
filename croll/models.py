from django.db import models
import sqlite3
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
import numpy as np

# Create your models here.
def createprice(request):
    con = sqlite3.connect("C:/Users/72027/PycharmProjects/webcroll/db.sqlite3")
    cur = con.cursor()
    cur.execute("create table price('code' TEXT, 'price' INTEGER, 'updatedate' DATETIME)")
    return HttpResponse('ok')

def updateprice(request):
    # company_code='005930'
    con = sqlite3.connect("C:/Users/72027/PycharmProjects/webcroll/db.sqlite3")
    selectsql = " select code from company where enable = 'Y'; "
    cur = con.cursor()
    cur.execute(selectsql)
    rows = cur.fetchall()
    for row in rows:
        company_code = row[0]
        updatepriceone(company_code)
        print(company_code)
    return HttpResponse('ok')

def updatepriceone(company_code):
    URL = "https://finance.naver.com/item/sise.nhn?code="+company_code
    received = requests.get(URL, verify=False)
    html = received.text
    soup = BeautifulSoup(html, 'html.parser')
    # f = open("c://soup.txt", "wb")
    # f.write(soup.text.encode('utf-8'))
    # f.close()
    # price_html = soup.select('div.section.trade_compare > table > tbody > tr > td')
    price_html = soup.select('#_nowVal')
    # print(price_html)
    price=price_html[0].text

    con = sqlite3.connect("C:/Users/72027/PycharmProjects/webcroll/db.sqlite3")
    cur = con.cursor()
    sql = ''' insert into price values(?,?,strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')); '''
    cur.execute(sql, (company_code, int(remove_letter(price,","))))
    cur.execute("commit;")
    return HttpResponse('ok')

''' sales : 매출액,business_profit : 영업이익,net_profit : 순이익,business_profit_ratio : 영업이익률,
    net_profit_ratio : 순이익률, ROE : ROE(지배주주),debt_ratio : 부채비율,quick_ratio : 당좌비율,
    reserve_ratio :유보율',bedang :주당배당금(원),bedang_ratio :시가배당율(%),bedang_tendency : 배당성향(%)'''
def createfinance(request):
    con = sqlite3.connect("C:/Users/72027/PycharmProjects/webcroll/db.sqlite3")
    sql = ''' CREATE
    TABLE
    `finance`(
    'finance_id' integer primary key autoincrement,
    'code' TEXT,
    `index_date` TEXT,
    'division' TEXT,
    `sales` INTEGER,
    `business_profit` INTEGER,
    `net_profit` INTEGER,
    `business_profit_ratio` REAL,
    `net_profit_ratio` REAL,
    `roe` REAL,
    `debt_ratio` REAL,
    `quick_ratio` REAL,
    `reserve_ratio` REAL,
    `eps` INTEGER,
    `bps` INTEGER,
    `bedang` INTEGER,
    `bedang_ratio` REAL,
    `bedang_tendency` REAL,
    'recent_bungi_check' TEXT,
    `updatedate` DATETIME
    ); '''
    cur = con.cursor()
    cur.execute(sql)
    return HttpResponse('ok')

def createcompany(request):
    con = sqlite3.connect("C:/Users/72027/PycharmProjects/webcroll/db.sqlite3")
    cur = con.cursor()
    cur.execute("create table company('code' TEXT, 'companyname' TEXT)")
    return HttpResponse('ok')

def updatefinance(request):
    # company_code='005930'
    con = sqlite3.connect("C:/Users/72027/PycharmProjects/webcroll/db.sqlite3")
    selectsql = " select code from company where enable = 'Y'; "
    cur = con.cursor()
    cur.execute(selectsql)
    rows = cur.fetchall()
    for row in rows:
        company_code = row[0]
        updatefinanceone(company_code)
        print(company_code)

    return HttpResponse('ok')

def updatefinanceone(company_code):
    URL = "https://finance.naver.com/item/main.nhn?code="+company_code
    samsung_electronic = requests.get(URL, verify=False)
    html = samsung_electronic.text
    soup = BeautifulSoup(html, 'html.parser')

    try :
        finance_html = soup.select('div.section.cop_analysis div.sub_section')[0]
        th_data = [item.get_text().strip() for item in finance_html.select('thead th')]
        annual_date = th_data[3:7]
        quarter_date = th_data[7:13]

        finance_index = [item.get_text().strip() for item in finance_html.select('th.h_th2')][3:]
        finance_data = [item.get_text().strip() for item in finance_html.select('td')]
        finance_data = np.array(finance_data)
        finance_data.resize(len(finance_index), 10)
        finance_data_modify = np.full((10,14), '111111111111.1111111')

        for i in range(len(finance_data)):
            for j in range(len(finance_data[i])):
                finance_data_modify[j][i] = finance_data[i][j]
        finance_date = annual_date + quarter_date

        con = sqlite3.connect("C:/Users/72027/PycharmProjects/webcroll/db.sqlite3")
        finance_date_count = 0
        division = 'annual'
        checkcount=0
        recent_bungi_check = 0
        for i in finance_data_modify:
            selectsql = " select count(*) from finance where code = ? and index_date = ? and division =?; "
            cur = con.cursor()
            cur.execute(selectsql,(company_code,finance_date[finance_date_count],division,))
            rows = cur.fetchall()
            for row in rows:
                checkcount=row[0]

            # 최근 분기 여부 표시
            if finance_date_count == 5:
                recent_bungi_check = 1
            elif finance_date_count == 6:
                recent_bungi_check = 2
            elif finance_date_count == 7:
                recent_bungi_check = 3
            elif finance_date_count == 8:
                recent_bungi_check = 4
            else:
                recent_bungi_check = 0

            if checkcount < 1 :
                # print("i is %s",company_code)
                # print(i)
                sql = ''' insert into finance values(null,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')); '''
                cur = con.cursor()

                i_list=[]
                for k in range(14):
                    i_list.append(k)
                # "," 삭제
                count=0
                for j in  i :
                    i_list[count]=remove_letter(j,",")
                    # print(i_list[count])
                    count=count+1

                # "-" 삭제
                count=0
                for j in i_list :
                    if j=='-':
                        i_list[count]="0"
                    count=count+1
                # count=0
                # for j in i_list :
                #     i_list[count]=remove_letter(j, "-")
                #     count=count+1

                # 숫자로 변경
                count=0
                for j in  i_list :
                    # print(count)
                    # print(j)
                    if len(j)>0:
                        if count in (3,4,5,6,7,8,12,13):
                            i_list[count]=float(j)
                        else:
                            # print(count)
                            # print(j)
                            i_list[count]=int(j)
                    else:
                        i_list[count]=0
                    count = count+1
                cur.execute(sql,(company_code,finance_date[finance_date_count],division,i_list[0],i_list[1],i_list[2],i_list[3],i_list[4],i_list[5],i_list[6],i_list[7],i_list[8],i_list[9],i_list[10],i_list[11],i_list[12],i_list[13],recent_bungi_check))
                cur.execute("commit;")
                # print(i_list)
            # raise Exception('3의 배수가 아닙니다.')
            if finance_date_count >2:
                division = 'quater'
            finance_date_count=finance_date_count+1
    except IndexError :
        con = sqlite3.connect("C:/Users/72027/PycharmProjects/webcroll/db.sqlite3")
        updatesql = " update company set enable = 'N' where code = ? ; "
        cur = con.cursor()
        cur.execute(updatesql,(company_code,))
        cur.execute("commit;")
    return HttpResponse('ok')

def remove_letter(base_string,letter_remove):  # 문자열에서 선택된 특정 문자를 없애버리기
    letter_remove = letter_remove[0]
    string_length = len(base_string)
    location = 0

    while (location < string_length) :
        if base_string[location] == letter_remove:
            base_string = base_string[:location] + base_string[location+1::]  # [:a] -> 처음부터 a위치까지, [a::]a위치부터 끝
            string_length = len(base_string)
        location+= 1
    # print("Result: %s",base_string)
    return base_string


