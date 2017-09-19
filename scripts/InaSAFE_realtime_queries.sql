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
    SELECT min(rw.id) AS id, village.name AS village, rw.name AS rwname  
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
    SELECT min(fe.id)::int4 AS id, village,rwname, count(*) AS flood_days
        FROM flood_events fe
        GROUP BY village,rwname
    )
SELECT fd.*, rb.geometry 
	FROM flood_days fd
	JOIN realtime_boundary rb
	ON fd.id = rb.id;

-- next: 
-- max flood duration in days, per rw



--select * from realtime_impacteventboundary
--select * from realtime_boundary order by name
--select * from realtime_floodreport
--select * from realtime_floodeventboundary 
--select * from realtime_impacteventboundary 
