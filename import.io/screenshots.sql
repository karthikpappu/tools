select userguid, date_part(YEAR, cast(timestamp as timestamp)) as year, date_part(MONTH, cast(timestamp as timestamp)) as month, sum(screencapturecount) as total
from crawlevent
where timestamp > ‘2019-06-30 23:59:59’
and screencapturecount is not null
--  and userguid in (‘7f083fea-3aa0-4189-b5d8-9b84053c5bdd’)
group by 1, 2, 3
order by 2, 3 desc
select userguid, sum(screencapturecount) as total
from crawlevent
where timestamp > ‘2019-06-30 23:59:59’
and screencapturecount is not null
group by 1
order by 2 desc
select sum(screencapturecount) as total
from crawlevent
where timestamp > ‘2019-06-30 23:59:59’
and screencapturecount is not null
select userguid, domain, sum(screencapturecount) as total
from crawlevent
where timestamp > ‘2018-12-31 23:59:59’
and screencapturecount is not null
and userguid in (‘7f083fea-3aa0-4189-b5d8-9b84053c5bdd’)
group by 1, 2
order by 3 desc
