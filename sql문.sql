/* 최신의 bps 뽑기 */
select f.code, f.bps,f.index_date from finance f
where f.index_date not like '%(E)'
group by code
having index_date=max(index_date);

/* 최신 주가 뽑기 */
select code,price,max(updatedate) updatedate from price
where 1=1
group by code, price
having updatedate=max(updatedate)
order by updatedate desc;

/* 최근 분기 pbr 계산 */
select b.code,c.companyname,p.price,b.bps,b.eps,(p.price+0.00)/(b.bps+0.00) pbr,b.index_date
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
order by pbr;



select * from finance
where code = '005930';

/* pbr per 동시 추출 */
select b.code,c.companyname,p.price,b.bps,e.eps,(p.price+0.00)/(b.bps+0.00) pbr,(p.price+0.00)/(e.eps+0.00) per,b.index_date
from (select f.code, f.bps, f.index_date from finance f
		where f.index_date not like '%(E)'
		group by code
		having index_date=max(index_date)) b,
	 (select f.code, sum(f.eps) eps, max(f.index_date) index_date from finance f
		where 1=1
		and f.index_date not like '%(E)'
		and f.recent_bungi_check > 0
		group by code) e,
	 (select code,price,max(updatedate) updatedate from price
		where 1=1
		group by code, price
		having updatedate=max(updatedate)
		order by updatedate desc) p,
		company c
where 1=1
and b.code=p.code
and b.code=c.code
and b.code=e.code
and pbr > 0
order by pbr;

/* 최근 분기 per 계산 */
select e.code,c.companyname,p.price,e.eps,(p.price+0.00)/(e.eps+0.00) per,e.index_date, eps > 0 plus
from (select f.code, sum(f.eps) eps, max(f.index_date) index_date from finance f
		where 1=1
		and f.index_date not like '%(E)'
		and f.recent_bungi_check > 0
		group by code) e,
	 (select code,price,max(updatedate) updatedate from price
		where 1=1
		group by code, price
		having updatedate=max(updatedate)
		order by updatedate desc) p,
		company c
where 1=1
and e.code=p.code
and e.code=c.code
--and per > 0
order by plus desc,per;

/* transaction record 테이블 생성 */
CREATE TABLE `transactionrecord`( 'id' integer primary key autoincrement,
														     'code' TEXT,
									                     'division' TEXT,
													  `quantity` INTEGER,
											             `price` INTEGER,
											 `transactionamount` INTEGER,
														   `fee` INTEGER,
														   `tax` INTEGER,
												  `adjustamount` INTEGER,
										  `transfer_yn` TEXT default 'N',
											  `transactiondate` DATETIME,
												   `updatedate` DATETIME
																		)
		