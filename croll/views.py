from django.shortcuts import render
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
import pandas as pd

#from numpy import xrange
from django.views.decorators.csrf import csrf_exempt
from pandas import Series, DataFrame
import sqlite3
from django.http import HttpResponseRedirect
from croll.pagingHelper import pagingHelper
from django.shortcuts import render_to_response


# 집에 있는 PC임
#print(annual_finance)
#print(quarter_finance)

def index(request):
    print("aaa")
    return render_to_response('croll/index.html')

def enteringwindow(request): # finance초기 화면
    # boardList = DjangoBoard.objects.order_by('-id')[0:2]
    return render_to_response('croll/transaction.html' )

rowsPerPage = 2
def pbrwindow(request): # finance초기 화면
    con = sqlite3.connect("C:/Users/72027/PycharmProjects/webcroll/db.sqlite3")
    selectsql = '''select row_number() over(order by (p.price+0.00)/(b.bps+0.00)) as num,c.companyname,b.code,b.index_date,p.price,b.bps,(p.price+0.00)/(b.bps+0.00) pbr
                 from (select f.code, f.bps,f.eps, f.index_date from finance f
		          where f.index_date not like '%(E)'
		          group by code
		          having index_date=max(index_date)) b,
	             (select code,price,max(updatedate) updatedate from price
		where 1=1
		group by code, price
		having updatedate=max(updatedate)
		order by updatedate desc) p,
		company c
where 1=1
and b.code=p.code
and b.code=c.code
and pbr > 0
order by pbr;'''
    cur = con.cursor()
    cur.execute(selectsql)
    boardList = cur.fetchall()

    # 데이터 포맷 변경
    # boardList_format = []
    boardList_format = [[0 for j in range(len(boardList[i]))] for i in range(len(boardList))]
    # print(boardList_format)
    for i in range(len(boardList)):
        for j in range(len(boardList[i])):
            if j in (4,5):
                boardList_format[i][j] = '{:,}'.format(boardList[i][j])
            elif j==6:
                boardList_format[i][j] = '{:,.2f}'.format(boardList[i][j])
            else:
                boardList_format[i][j] = boardList[i][j]

    boardList=boardList_format
    # print(boardList)
    current_page =1
    totalCnt = len(boardList)
    pagingHelperIns = pagingHelper();
    totalPageList = pagingHelperIns.getTotalPageList( totalCnt, rowsPerPage)
    return render_to_response('croll/pbr.html', {'boardList': boardList, 'totalCnt': totalCnt,
                                                          'current_page':current_page ,'totalPageList':totalPageList} )

rowsPerPage = 2
def financewindow(request): # finance초기 화면
    # boardList = DjangoBoard.objects.order_by('-id')[0:2]
    con = sqlite3.connect("C:/Users/72027/PycharmProjects/webcroll/db.sqlite3")
    selectsql = " select company.companyname,finance.* from finance, company where finance.code=company.code and company.code = ? order by division, index_date ; "
    cur = con.cursor()
    cur.execute(selectsql, ('0',))
    boardList = cur.fetchall()

    print(type(boardList))
    current_page =1
    totalCnt = len(boardList)
    pagingHelperIns = pagingHelper();
    totalPageList = pagingHelperIns.getTotalPageList( totalCnt, rowsPerPage)
    return render_to_response('croll/finance.html', {'boardList': boardList, 'totalCnt': totalCnt,
                                                          'current_page':current_page ,'totalPageList':totalPageList} )
@csrf_exempt
def financeinfo(request): # finance화면에서 검색시 호출
    # boardList = DjangoBoard.objects.order_by('-id')[0:2]

    company_code = request.POST['companycode']
    print(company_code)
    print('finance info called')
    con = sqlite3.connect("C:/Users/72027/PycharmProjects/webcroll/db.sqlite3")
    selectsql = " select company.companyname,finance.* from finance, company where finance.code=company.code and company.code = ? order by division, index_date ; "
    cur = con.cursor()
    cur.execute(selectsql, (company_code,))
    boardList = cur.fetchall()


    current_page =1

       # model 을 사용해서 전체 데이터 갯수를 구한다.
    totalCnt = len(boardList)

       # 이것은 페이징 처리를 위해 생성한 간단한 헬퍼 클래스이다. 별로 중요하지 않으므로 소스를 참조하기 바란다.
    pagingHelperIns = pagingHelper();
    totalPageList = pagingHelperIns.getTotalPageList( totalCnt, rowsPerPage)
    # print 'totalPageList', totalPageList

       # 템플릿으로 필요한 정보들을 넘기는 부분이다. 이를 통해서 정적인 템플릿에 동적인 데이터가 결합되게 되는 것이다.

      # 우리는 게시판 최초 화면 처리를 위해서 listSpecificPage.html 템플릿을 호출했다.

      # 그리고 필요한 정보들을 dictionary 로 전달했다.
    # for i in boardList:
    #     print (i[0],i[1])
    return render_to_response('croll/finance.html', {'boardList': boardList, 'totalCnt': totalCnt,
                                                          'current_page':current_page ,'totalPageList':totalPageList} )

def testview(request):
    return render_to_response('croll/test.html')


# def updatefinance(request):
#     URL = "https://finance.naver.com/item/main.nhn?code="+company_code
#     samsung_electronic = requests.get(URL, verify=False)
#     html = samsung_electronic.text
#     soup = BeautifulSoup(html, 'html.parser')
#
#     finance_html = soup.select('div.section.cop_analysis div.sub_section')[0]
#     th_data = [item.get_text().strip() for item in finance_html.select('thead th')]
#     annual_date = th_data[3:7]
#     quarter_date = th_data[7:13]
#
#     finance_index = [item.get_text().strip() for item in finance_html.select('th.h_th2')][3:]
#     finance_data = [item.get_text().strip() for item in finance_html.select('td')]
#     finance_data = np.array(finance_data)
#     finance_data.resize(len(finance_index), 10)
#     finance_data_modify = np.full((10,14), '1.111')
#
#     for i in range(len(finance_data)):
#         for j in range(len(finance_data[i])):
#             finance_data_modify[j][i] = finance_data[i][j]
#
#     finance_date = annual_date + quarter_date
#
#     con = sqlite3.connect("C:/Users/72027/PycharmProjects/webcroll/db.sqlite3")
#     finance_date_count = 0
#     division = 'annual'
#     checkcount=0
#     for i in finance_data_modify:
#         selectsql = " select count(*) from finance where index_date = ? and division =?; "
#         cur = con.cursor()
#         cur.execute(selectsql,(finance_date[finance_date_count],division,))
#         rows = cur.fetchall()
#         for row in rows:
#             checkcount=row[0]
#
#         if checkcount < 1 :
#             sql = ''' insert into finance values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?); '''
#             cur = con.cursor()
#             cur.execute(sql,(company_code,finance_date[finance_date_count],division,i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8],i[9],i[10],i[11],i[12],i[13]))
#             cur.execute("commit;")
#             print(checkcount)
#             print(finance_date[finance_date_count])
#             print(division)
#
#         if finance_date_count >2:
#             division = 'quater'
#         finance_date_count=finance_date_count+1
#     return HttpResponse('ok')





# def makefinance(request): # 현재 사용안함
#     URL = "https://finance.naver.com/item/main.nhn?code=005930"
#     samsung_electronic = requests.get(URL, verify=False)
#     html = samsung_electronic.text
#
#     soup = BeautifulSoup(html, 'html.parser')
#     finance_html = soup.select('div.section.cop_analysis div.sub_section')[0]
#     th_data = [item.get_text().strip() for item in finance_html.select('thead th')]
#     annual_date = th_data[3:7]
#     quarter_date = th_data[7:13]
#
#     finance_index = [item.get_text().strip() for item in finance_html.select('th.h_th2')][3:]
#     # print(finance_html.select('th.h_th2'))
#
#     finance_data = [item.get_text().strip() for item in finance_html.select('td')]
#
#     finance_data = np.array(finance_data)
#
#     finance_data.resize(len(finance_index), 10)
#     finance_data_modify = np.full((10,14), '1.111')
#
#     for i in range(len(finance_data)):
#         for j in range(len(finance_data[i])):
#             finance_data_modify[j][i] = finance_data[i][j]
#     finance_date = annual_date + quarter_date
#
#     finance = pd.DataFrame(data=finance_data_modify[0:, 0:], index=finance_date, columns=finance_index)
#     print(finance)
#     annual_finance = finance.iloc[:, :4]
#     quarter_finance = finance.iloc[:, 4:]
#     con = sqlite3.connect("C:/Users/72027/PycharmProjects/webcroll/db.sqlite3")
#     finance.to_sql('finance', con)
#     return HttpResponse('ok')