from django.db import models
import sqlite3
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
import numpy as np
import win32com.client
import pythoncom
from time import sleep
import psycopg2


class XSession:
    """
    classmethod get_instance() 를 사용하여, instance 를 만들어야함.
    """

    def __init__(self):
        self.login_state = 0

    def OnLogin(self, code, msg):  # event handler
        """
        Login 이 성공적으로 이베스트 서버로 전송된후,
        로그인 결과에 대한 Login 이벤트 발생시 실행되는 event handler
        """
        if code == "0000":
            print("로그인 ok\n")
            self.login_state = 1
        else:
            self.login_state = 2
            print("로그인 fail.. \n code={0}, message={1}\n".format(code, msg))

    def api_login(self, id="vlfdus80", pwd="!a571132", cert_pwd="!!a5711327"):  # id, 암호, 공인인증서 암호
        self.ConnectServer("hts.ebestsec.co.kr", 20001)
        is_connected = self.Login(id, pwd, cert_pwd, 0, False)  # 로그인 하기

        if not is_connected:  # 서버에 연결 안되거나, 전송 에러시
            print("로그인 서버 접속 실패... ")
            return
        while self.login_state == 0:
            pythoncom.PumpWaitingMessages()

    def account_info(self):
        """
        계좌 정보 조회
        """
        if self.login_state != 1:  # 로그인 성공 아니면, 종료
            return

        account_no = self.GetAccountListCount()

        print("계좌 갯수 = {0}".format(account_no))

        for i in range(account_no):
            account = self.GetAccountList(i)
            print("계좌번호 = {0}".format(account))

    @classmethod
    def get_instance(cls):
        # DispatchWithEvents로 instance 생성하기
        xsession = win32com.client.DispatchWithEvents("XA_Session.XASession", cls)
        return xsession


class XQuery_t1101:
    """
    classmethod get_instance() 를 사용하여, instance 를 만들어야함.
    """

    def __init__(self):
        self.is_data_received = False

    def OnReceiveData(self, tr_code):  # event handler
        """
        이베스트 서버에서 ReceiveData 이벤트 받으면 실행되는 event handler
        """
        self.is_data_received = True
        name = self.GetFieldData("t1101OutBlock", "hname", 0)
        price = self.GetFieldData("t1101OutBlock", "price", 0)
        volume = self.GetFieldData("t1101OutBlock", "volume", 0)
        code = self.GetFieldData("t1101OutBlock", "shcode", 0)

        con = psycopg2.connect("dbname='webcrolldb' user='postgres' host='localhost' password='1111'")
        cur = con.cursor()
        sql = "insert into price values(%s,%s,current_timestamp);"
        cur.execute(sql, (code, int(remove_letter(price, ','))))

        cur.execute("commit;")
        cur.close()
        con.close()

    def single_request(self, stockcode):
        self.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t1101.res"  # RES 파일 등록
        self.SetFieldData("t1101InBlock", "shcode", 0, stockcode)  # 종목코드 설정
        err_code = self.Request(False)  # data 요청하기 --  연속조회인경우만 True
        if err_code < 0:
            print("error... {0}".format(err_code))

    @classmethod
    def get_instance(cls):
        print("kkk1")
        # DispatchWithEvents로 instance 생성하기
        xq_t1101 = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", cls)
        print("kkk2")
        return xq_t1101




# Create your models here.
def createprice(request):
    con = psycopg2.connect("dbname='webcrolldb' user='postgres' host='localhost' password='1111'")
    cur = con.cursor()
    cur.execute("create table price(code varchar(100), price int, updatedate timestamp)")
    cur.execute("commit;")
    cur.close()
    con.close()
    return HttpResponse('ok')

def updateprice(request):
    # company_code='005930'

    pythoncom.CoInitialize()
    xsession = XSession.get_instance()
    xsession.api_login()
    xsession.account_info()
    print("request complete")


    con = psycopg2.connect("dbname='webcrolldb' user='postgres' host='localhost' password='1111'")
    selectsql = " select code from company where enable = 'Y'; "
    cur = con.cursor()
    cur.execute(selectsql)
    rows = cur.fetchall()
    for row in rows:
        company_code = row[0]
        updatepriceone_xing(company_code)
        print(company_code)
    cur.close()
    con.close()
    return HttpResponse('ok')

def updatepriceone_xing(company_code):
    pythoncom.CoInitialize()
    # print("kkk")
    # xsession = XSession.get_instance()
    # xsession.api_login()
    # print("kkk2")
    # xsession.account_info()
    # print("------END--")

    def get_single_data():
        xq_t1101 = XQuery_t1101.get_instance()
        xq_t1101.single_request(company_code)  # 삼성전자.

        while xq_t1101.is_data_received == False:
            pythoncom.PumpWaitingMessages()
    sleep(0.1)
    get_single_data()

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

    con = sqlite3.connect("D:/03.Study/01.SD/webcroll_sqlite/db.sqlite3")
    cur = con.cursor()
    sql = ''' insert into price values(?,?,strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')); '''
    cur.execute(sql, (company_code, int(remove_letter(price,","))))
    cur.execute("commit;")
    return HttpResponse('ok')






''' sales : 매출액,business_profit : 영업이익,net_profit : 순이익,business_profit_ratio : 영업이익률,
    net_profit_ratio : 순이익률, ROE : ROE(지배주주),debt_ratio : 부채비율,quick_ratio : 당좌비율,
    reserve_ratio :유보율',bedang :주당배당금(원),bedang_ratio :시가배당율(%),bedang_tendency : 배당성향(%)'''
def createfinance(request):
    con = psycopg2.connect("dbname='webcrolldb' user='postgres' host='localhost' password='1111'")
    sql = ''' CREATE
    TABLE
    finance(
    finance_id serial primary key,
    code varchar(100),
    index_date varchar(100),
    division varchar(100),
    sales int,
    business_profit int,
    net_profit int,
    business_profit_ratio real,
    net_profit_ratio real,
    roe real,
    debt_ratio real,
    quick_ratio real,
    reserve_ratio real,
    eps int,
    bps int,
    bedang int,
    bedang_ratio real,
    bedang_tendency real,
    recent_bungi_check varchar(100),
    updatedate timestamp
    ); '''
    cur = con.cursor()
    cur.execute(sql)
    cur.execute("commit;")
    cur.close()
    con.close()
    return HttpResponse('ok')

def createcompany(request):
    con = psycopg2.connect("dbname='webcrolldb' user='postgres' host='localhost' password='1111'")
    cur = con.cursor()
    cur.execute("create table company(code varchar(100), companyname varchar(100))")
    cur.close()
    con.close()
    return HttpResponse('ok')

def updatefinance(request):
    # company_code='005930'
    con = psycopg2.connect("dbname='webcrolldb' user='postgres' host='localhost' password='1111'")
    selectsql = " select code from company where enable = 'Y'; "
    cur = con.cursor()
    cur.execute(selectsql)
    rows = cur.fetchall()
    for row in rows:
        company_code = row[0]
        updatefinanceone(company_code)
        print(company_code)

    cur.close()
    con.close()
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

        con = psycopg2.connect("dbname='webcrolldb' user='postgres' host='localhost' password='1111'")
        finance_date_count = 0
        division = 'annual'
        checkcount=0
        recent_bungi_check = 0
        for i in finance_data_modify:
            selectsql = " select count(*) from finance where code = %s and index_date = %s and division =%s; "
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
                sql = ''' insert into finance values(nextval('finance_sequence'),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,current_timestamp); '''
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
        cur.close()
        con.close()
    except IndexError :
        con = psycopg2.connect("dbname='webcrolldb' user='postgres' host='localhost' password='1111'")
        updatesql = " update company set enable = 'N' where code = %s ; "
        cur = con.cursor()
        cur.execute(updatesql,(company_code,))
        cur.execute("commit;")
        cur.close()
        con.close()
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




