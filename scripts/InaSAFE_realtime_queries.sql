-- FLOOD

--Number of unique days each RW boundary has been flooded

/* 1st attempt with spatial overlay before I realised we could just parse flood_id 
WITH rw AS (
    SELECT name,st_union(geometry) geom
	FROM realtime_boundary
    WHERE boundary_alias_id = 2
GROUP BY name)
SELECT rw.name,count(flood.*)
FROM realtime_impacteventboundary flood
JOIN rw
ON ST_Intersects(flood.geometry,rw.geom)
GROUP BY rw.name
ORDER BY rw.name
*/

-- DROP VIEW unique_flood_days_per_rw;
CREATE OR REPLACE VIEW unique_flood_days_per_rw AS
WITH flood_events AS (
    SELECT min(rw.id) AS id, village.name AS village, rw.name AS rwname  --this SELECT counts flood *events* per RW
		FROM realtime_flood f
		JOIN realtime_floodeventboundary feb
		ON f.event_id = feb.flood_id
		JOIN realtime_boundary rw
		ON feb.boundary_id = rw.id
		LEFT JOIN realtime_boundary village
		ON rw.parent_id = village.id
		WHERE rw.boundary_alias_id = 2
	GROUP BY village,rwname,substring(f.event_id,1,8)
	ORDER BY village,rwname
	),
    flood_days AS (
    SELECT min(fe.id)::int4 AS id, village,rwname, count(*) AS flood_days --this SELECT counts flood *days* per RW
        FROM flood_events fe
        GROUP BY village,rwname
    )
SELECT fd.*, rb.geometry 
	FROM flood_days fd
	JOIN realtime_boundary rb
	ON fd.id = rb.id;

-- next: 
-- max flood duration in days, per rw


--exploratory queries:
--select * from realtime_boundary order by name
--select * from realtime_floodreport
--select * from realtime_flood
--select * from realtime_floodeventboundary 
--select * from realtime_impacteventboundary 

-- number and time range of shakemaps
select count(*), min(time),max(time) from realtime_earthquake

-- detecting 2010 outlier, when did real shakemap stream start?
select time from realtime_earthquake order by time asc limit 50;

-- number of shakemaps per year and average, total or >= mmi 5
WITH annual AS
(
select date_part('year',time) year_, count(*) shakemaps from realtime_earthquake 
where magnitude >= 5
group by date_part('year',time) 
    having count(*) > 1
    order by date_part('year',time)
    )
select avg(shakemaps)::int from annual;

-- number and time range of flood events
select source, count(*), min(time),max(time) from realtime_flood by 
group by source;

-- detecting early outlier?, when did real flood stream start?
select time from realtime_flood order by time asc limit 50;

-- number of flood events per flood month and average
WITH monthly AS
(
select date_trunc('month',time) month_, count(*) flood_events from realtime_flood 
group by date_trunc('month',time) 
    having count(*) > 0
    order by date_trunc('month',time)
    )
select avg(flood_events)::int from monthly;

-- number of flood events per year and average
WITH annual AS
(
select date_trunc('year',time) month_, count(*) flood_events from realtime_flood 
group by date_trunc('year',time) 
    having count(*) > 0
    order by date_trunc('year',time)
    )
select avg(flood_events)::int from annual;

--what is the distribution of flood hazard classes
select hazard_data, count(*)  from realtime_floodeventboundary group by hazard_data order by hazard_data;

--Rank flood extent (number of RWs flooded per day)
WITH unique_flood_days AS ( -- this fetches one event per flood day
    SELECT DISTINCT ON (substring(event_id,1,8)) * 
    	FROM realtime_flood
    )
SELECT count(*) AS no_rws_flooded, substring(f.event_id,1,8)::date AS date
		FROM unique_flood_days f
		JOIN realtime_floodeventboundary feb
		ON f.event_id = feb.flood_id
		JOIN realtime_boundary rw
		ON feb.boundary_id = rw.id
		LEFT JOIN realtime_boundary village
		ON rw.parent_id = village.id
		WHERE rw.boundary_alias_id = 2
	GROUP BY substring(f.event_id,1,8) 
	ORDER BY count(*) DESC,substring(f.event_id,1,8)::date DESC;
    
--rank flood severity? Some function of depth end extent?

-- a flat table of unique flood days for mapping. 
-- DROP VIEW worst_flood_per_day_per_rw;
CREATE OR REPLACE VIEW worst_flood_per_day_per_rw AS 
    SELECT  DISTINCT ON (substring(f.event_id,1,8),village,rwname) row_number() OVER ()::int4 AS id, substring(f.event_id,1,8)::date as date, 
    hazard_data, village.name AS village, rw.name AS rwname, rw.geometry
		FROM realtime_flood f
		JOIN realtime_floodeventboundary feb
		ON f.event_id = feb.flood_id
		JOIN realtime_boundary rw
		ON feb.boundary_id = rw.id
		LEFT JOIN realtime_boundary village
		ON rw.parent_id = village.id
		WHERE rw.boundary_alias_id = 2
        ORDER BY substring(f.event_id,1,8),village,rwname,hazard_data DESC;
        
 SELECT distinct on (id) * from worst_flood_per_day_per_rw;
	
-- EARTHQUAKE

-- SELECT * from realtime_earthquake

-- create an EQ view for GIS work
-- DROP VIEW eq_animation;
CREATE OR REPLACE VIEW eq_animation AS
SELECT id,magnitude,location,time::date AS date, (time::date + interval '1 month')::date AS fake_end
FROM realtime_earthquake
ORDER BY date
OFFSET 1; -- to remove 2010 outlier
