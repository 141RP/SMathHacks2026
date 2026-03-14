-- Seed data for ReefSync centered on the Florida Keys.
-- Assumes schema.sql has already been applied.

TRUNCATE TABLE survey_divers, surveys, users, reef_zones, orgs RESTART IDENTITY CASCADE;

INSERT INTO orgs (slug, name, contact_email, contact_phone, home_base, metadata) VALUES
    (
        'keys-restoration-alliance',
        'Keys Restoration Alliance',
        'ops@keysrestore.org',
        '+1-305-555-0100',
        ST_GeogFromText('SRID=4326;POINT(-80.1290 25.0840)'),
        '{"focus":"reef restoration","region":"Upper Keys"}'
    ),
    (
        'blue-current-research',
        'Blue Current Research',
        'field@bluecurrent.io',
        '+1-305-555-0110',
        ST_GeogFromText('SRID=4326;POINT(-80.4440 24.7410)'),
        '{"focus":"water quality","region":"Middle Keys"}'
    ),
    (
        'conch-reef-watch',
        'Conch Reef Watch',
        'dispatch@conchreefwatch.org',
        '+1-305-555-0120',
        ST_GeogFromText('SRID=4326;POINT(-81.7800 24.5550)'),
        '{"focus":"bleaching response","region":"Lower Keys"}'
    );

INSERT INTO users (org_id, email, full_name, role, cert_level, phone) VALUES
    (1, 'maya.santos@keysrestore.org', 'Maya Santos', 'coordinator', 'PADI Rescue', '+1-305-555-1101'),
    (1, 'liam.chen@keysrestore.org', 'Liam Chen', 'scientist', 'AAUS', '+1-305-555-1102'),
    (1, 'zoe.martin@keysrestore.org', 'Zoe Martin', 'diver', 'PADI Divemaster', '+1-305-555-1103'),
    (2, 'dani.rivera@bluecurrent.io', 'Dani Rivera', 'coordinator', 'AAUS', '+1-305-555-1201'),
    (2, 'owen.brooks@bluecurrent.io', 'Owen Brooks', 'scientist', 'PADI Rescue', '+1-305-555-1202'),
    (2, 'nina.patel@bluecurrent.io', 'Nina Patel', 'diver', 'PADI Advanced', '+1-305-555-1203'),
    (3, 'aria.lopez@conchreefwatch.org', 'Aria Lopez', 'coordinator', 'PADI Rescue', '+1-305-555-1301'),
    (3, 'samir.khan@conchreefwatch.org', 'Samir Khan', 'scientist', 'AAUS', '+1-305-555-1302'),
    (3, 'elena.torres@conchreefwatch.org', 'Elena Torres', 'diver', 'PADI Divemaster', '+1-305-555-1303');

INSERT INTO reef_zones (org_id, zone_code, name, habitat_type, priority, target_interval_days, notes, geom) VALUES
    (
        1,
        'UK-CARYS',
        'Carysfort Spur and Groove',
        'spur-and-groove',
        5,
        21,
        'High visitation nursery outplant corridor.',
        ST_Multi(ST_GeomFromText('POLYGON((
            -80.2400 25.2220,
            -80.2280 25.2220,
            -80.2280 25.2320,
            -80.2400 25.2320,
            -80.2400 25.2220
        ))', 4326))
    ),
    (
        1,
        'UK-MOLS',
        'Molasses Fore Reef',
        'fore-reef',
        4,
        30,
        'Popular training site with moderate vessel traffic.',
        ST_Multi(ST_GeomFromText('POLYGON((
            -80.3780 25.0110,
            -80.3660 25.0110,
            -80.3660 25.0210,
            -80.3780 25.0210,
            -80.3780 25.0110
        ))', 4326))
    ),
    (
        2,
        'MK-SOMB',
        'Sombrero Patch Matrix',
        'patch-reef',
        5,
        14,
        'Storm-sensitive coral recruitment transects.',
        ST_Multi(ST_GeomFromText('POLYGON((
            -81.1350 24.6130,
            -81.1210 24.6130,
            -81.1210 24.6240,
            -81.1350 24.6240,
            -81.1350 24.6130
        ))', 4326))
    ),
    (
        2,
        'MK-LOOE',
        'Looe Key Sanctuary Grid',
        'barrier-reef',
        5,
        21,
        'Frequent bleaching watch deployments.',
        ST_Multi(ST_GeomFromText('POLYGON((
            -81.4350 24.5390,
            -81.4200 24.5390,
            -81.4200 24.5510,
            -81.4350 24.5510,
            -81.4350 24.5390
        ))', 4326))
    ),
    (
        3,
        'LK-SAND',
        'Sand Key Sentinel Zone',
        'bank-reef',
        3,
        45,
        'Deep relief monitoring site near Key West.',
        ST_Multi(ST_GeomFromText('POLYGON((
            -81.9260 24.4430,
            -81.9120 24.4430,
            -81.9120 24.4550,
            -81.9260 24.4550,
            -81.9260 24.4430
        ))', 4326))
    ),
    (
        3,
        'LK-WSAM',
        'Western Sambo Watch',
        'spur-and-groove',
        4,
        30,
        'Protected outplant and fish abundance surveys.',
        ST_Multi(ST_GeomFromText('POLYGON((
            -81.7720 24.4740,
            -81.7580 24.4740,
            -81.7580 24.4860,
            -81.7720 24.4860,
            -81.7720 24.4740
        ))', 4326))
    );

INSERT INTO surveys (
    org_id,
    zone_id,
    lead_user_id,
    survey_code,
    title,
    survey_type,
    status,
    priority,
    scheduled_start,
    scheduled_end,
    observed_at,
    completed_at,
    visibility_m,
    max_depth_m,
    notes,
    location,
    metadata
) VALUES
    (1, 1, 2, 'RS-2025-001', 'Carysfort baseline photogrammetry', 'photogrammetry', 'completed', 5, '2025-11-22T13:00:00Z', '2025-11-22T16:00:00Z', '2025-11-22T14:10:00Z', '2025-11-22T16:05:00Z', 22.5, 11.2, 'Strong current on outer transect.', ST_GeogFromText('SRID=4326;POINT(-80.2338 25.2268)'), '{"bleaching_alert":false}'),
    (1, 1, 1, 'RS-2025-002', 'Carysfort disease spot check', 'health-check', 'completed', 4, '2025-09-28T13:30:00Z', '2025-09-28T15:30:00Z', '2025-09-28T13:50:00Z', '2025-09-28T15:20:00Z', 18.0, 10.5, 'Survey older than 90 days for coverage testing.', ST_GeogFromText('SRID=4326;POINT(-80.2355 25.2291)'), '{"disease_notes":"minor SCTLD scar counts"}'),
    (1, 2, 2, 'RS-2025-003', 'Molasses coral recruitment transect', 'transect', 'completed', 3, '2026-02-10T14:00:00Z', '2026-02-10T17:00:00Z', '2026-02-10T14:12:00Z', '2026-02-10T16:45:00Z', 20.0, 9.1, 'Juvenile colonies above expected count.', ST_GeogFromText('SRID=4326;POINT(-80.3724 25.0160)'), '{"juvenile_count":46}'),
    (1, 2, 3, 'RS-2025-004', 'Molasses mooring impact review', 'impact-assessment', 'planned', 2, '2026-03-16T13:00:00Z', '2026-03-16T15:00:00Z', NULL, NULL, NULL, NULL, 'Planned with harbor team.', ST_GeogFromText('SRID=4326;POINT(-80.3716 25.0154)'), '{"vessel_support":"Skiff 2"}'),
    (1, 2, 1, 'RS-2025-005', 'Molasses algae removal support', 'restoration-support', 'planned', 2, '2026-03-18T13:30:00Z', '2026-03-18T16:00:00Z', NULL, NULL, NULL, NULL, 'Potential overlap candidate with external partner.', ST_GeogFromText('SRID=4326;POINT(-80.3698 25.0147)'), '{"crew_size":4}'),
    (2, 3, 5, 'RS-2025-006', 'Sombrero temperature logger swap', 'maintenance', 'completed', 4, '2026-03-01T14:00:00Z', '2026-03-01T16:00:00Z', '2026-03-01T14:18:00Z', '2026-03-01T15:52:00Z', 24.0, 8.5, 'Logger battery replaced.', ST_GeogFromText('SRID=4326;POINT(-81.1278 24.6185)'), '{"logger_id":"TMP-17"}'),
    (2, 3, 4, 'RS-2025-007', 'Sombrero patch fish census', 'fish-count', 'completed', 3, '2025-10-25T14:00:00Z', '2025-10-25T17:30:00Z', '2025-10-25T14:20:00Z', '2025-10-25T17:10:00Z', 19.3, 8.0, 'Historic benchmark run.', ST_GeogFromText('SRID=4326;POINT(-81.1294 24.6207)'), '{"parrotfish_schools":12}'),
    (2, 3, 5, 'RS-2025-008', 'Sombrero bleaching response dive', 'bleaching-response', 'planned', 5, '2026-03-17T14:30:00Z', '2026-03-17T17:00:00Z', NULL, NULL, NULL, NULL, 'Rapid response if SST remains elevated.', ST_GeogFromText('SRID=4326;POINT(-81.1265 24.6191)'), '{"sst_watch":"orange"}'),
    (2, 3, 4, 'RS-2025-009', 'Sombrero partner transect', 'transect', 'planned', 4, '2026-03-19T14:00:00Z', '2026-03-19T16:00:00Z', NULL, NULL, NULL, NULL, 'May conflict with another boat in sector.', ST_GeogFromText('SRID=4326;POINT(-81.1248 24.6173)'), '{"partner_org":"NOAA volunteer team"}'),
    (2, 4, 5, 'RS-2025-010', 'Looe key bleaching grid', 'bleaching-response', 'completed', 5, '2026-02-26T15:00:00Z', '2026-02-26T18:00:00Z', '2026-02-26T15:09:00Z', '2026-02-26T17:42:00Z', 21.7, 13.4, 'Paling observed on shallow ridges.', ST_GeogFromText('SRID=4326;POINT(-81.4285 24.5458)'), '{"affected_quadrats":7}'),
    (2, 4, 6, 'RS-2025-011', 'Looe anchor scar mapping', 'impact-assessment', 'completed', 3, '2025-11-05T15:00:00Z', '2025-11-05T18:00:00Z', '2025-11-05T15:12:00Z', '2025-11-05T17:48:00Z', 17.5, 14.1, 'Older than 90 days.', ST_GeogFromText('SRID=4326;POINT(-81.4301 24.5469)'), '{"scar_count":3}'),
    (2, 4, 4, 'RS-2025-012', 'Looe sanctuary patrol support', 'patrol-support', 'planned', 2, '2026-03-16T15:30:00Z', '2026-03-16T18:00:00Z', NULL, NULL, NULL, NULL, 'Shared channel coordination required.', ST_GeogFromText('SRID=4326;POINT(-81.4272 24.5448)'), '{"vessel_support":"Blue Current 1"}'),
    (3, 5, 8, 'RS-2025-013', 'Sand Key relief profile', 'photogrammetry', 'completed', 3, '2026-01-08T15:00:00Z', '2026-01-08T18:00:00Z', '2026-01-08T15:16:00Z', '2026-01-08T17:40:00Z', 16.8, 18.6, 'Low viz near channel edge.', ST_GeogFromText('SRID=4326;POINT(-81.9194 24.4498)'), '{"tiles_captured":128}'),
    (3, 5, 7, 'RS-2025-014', 'Sand Key winter fish count', 'fish-count', 'completed', 2, '2025-10-02T15:00:00Z', '2025-10-02T17:00:00Z', '2025-10-02T15:11:00Z', '2025-10-02T16:55:00Z', 14.9, 19.0, 'Reference count from last season.', ST_GeogFromText('SRID=4326;POINT(-81.9178 24.4514)'), '{"grouper_count":9}'),
    (3, 5, 9, 'RS-2025-015', 'Sand Key mooring inspection', 'maintenance', 'planned', 1, '2026-03-20T15:00:00Z', '2026-03-20T16:30:00Z', NULL, NULL, NULL, NULL, 'Short maintenance task.', ST_GeogFromText('SRID=4326;POINT(-81.9185 24.4486)'), '{"mooring_id":"SK-03"}'),
    (3, 6, 8, 'RS-2025-016', 'Western Sambo coral nursery audit', 'restoration-support', 'completed', 4, '2026-02-20T15:00:00Z', '2026-02-20T18:30:00Z', '2026-02-20T15:05:00Z', '2026-02-20T18:00:00Z', 23.1, 12.2, 'Nursery line 4 needs re-tensioning.', ST_GeogFromText('SRID=4326;POINT(-81.7654 24.4798)'), '{"nursery_lines_checked":6}'),
    (3, 6, 7, 'RS-2025-017', 'Western Sambo bleaching transect', 'bleaching-response', 'completed', 5, '2025-11-18T15:00:00Z', '2025-11-18T18:00:00Z', '2025-11-18T15:15:00Z', '2025-11-18T17:50:00Z', 20.4, 11.9, 'Older than 90 days.', ST_GeogFromText('SRID=4326;POINT(-81.7632 24.4809)'), '{"bleached_heads":11}'),
    (3, 6, 8, 'RS-2025-018', 'Western Sambo lionfish sweep', 'removal', 'planned', 3, '2026-03-17T15:00:00Z', '2026-03-17T17:30:00Z', NULL, NULL, NULL, NULL, 'Community volunteer crossover.', ST_GeogFromText('SRID=4326;POINT(-81.7648 24.4816)'), '{"volunteers":5}'),
    (3, 6, 7, 'RS-2025-019', 'Western Sambo partner reef check', 'health-check', 'planned', 4, '2026-03-18T15:15:00Z', '2026-03-18T17:00:00Z', NULL, NULL, NULL, NULL, 'Conflict candidate with nearby team.', ST_GeogFromText('SRID=4326;POINT(-81.7625 24.4794)'), '{"partner_org":"Mote Marine interns"}'),
    (1, 1, 2, 'RS-2025-020', 'Carysfort acoustic beacon service', 'maintenance', 'planned', 2, '2026-03-17T13:15:00Z', '2026-03-17T15:00:00Z', NULL, NULL, NULL, NULL, 'Short turnaround maintenance window.', ST_GeogFromText('SRID=4326;POINT(-80.2324 25.2276)'), '{"beacon_id":"CF-09"}'),
    (1, 1, 3, 'RS-2025-021', 'Carysfort volunteer orientation dive', 'training', 'planned', 1, '2026-03-17T13:45:00Z', '2026-03-17T15:45:00Z', NULL, NULL, NULL, NULL, 'Intentionally near another planned site for overlap testing.', ST_GeogFromText('SRID=4326;POINT(-80.2312 25.2284)'), '{"students":3}'),
    (2, 4, 6, 'RS-2025-022', 'Looe reef sponge census', 'benthic-survey', 'completed', 2, '2025-12-15T15:00:00Z', '2025-12-15T17:30:00Z', '2025-12-15T15:10:00Z', '2025-12-15T17:05:00Z', 18.7, 13.8, 'Stable sponge cover.', ST_GeogFromText('SRID=4326;POINT(-81.4260 24.5460)'), '{"sponge_cover_pct":31}'),
    (3, 5, 9, 'RS-2025-023', 'Sand Key post-front inspection', 'health-check', 'completed', 2, '2025-12-22T15:00:00Z', '2025-12-22T17:15:00Z', '2025-12-22T15:07:00Z', '2025-12-22T16:58:00Z', 15.2, 18.2, 'Sediment plume dissipated by second transect.', ST_GeogFromText('SRID=4326;POINT(-81.9206 24.4508)'), '{"storm_front":"cold front"}'),
    (2, 3, 5, 'RS-2025-024', 'Sombrero reef check duplicate sector', 'health-check', 'planned', 4, '2026-03-18T14:20:00Z', '2026-03-18T16:10:00Z', NULL, NULL, NULL, NULL, 'Designed to overlap spatially and temporally with another planned survey.', ST_GeogFromText('SRID=4326;POINT(-81.1256 24.6180)'), '{"sector":"northwest"}');

INSERT INTO survey_divers (survey_id, user_id, assignment_role, is_primary) VALUES
    (1, 2, 'lead_scientist', TRUE),
    (1, 3, 'safety_diver', FALSE),
    (2, 1, 'mission_lead', TRUE),
    (2, 3, 'diver', FALSE),
    (3, 2, 'lead_scientist', TRUE),
    (3, 1, 'coordinator', FALSE),
    (4, 3, 'diver', TRUE),
    (4, 1, 'surface_support', FALSE),
    (5, 1, 'mission_lead', TRUE),
    (5, 3, 'diver', FALSE),
    (6, 5, 'lead_scientist', TRUE),
    (6, 6, 'data_recorder', FALSE),
    (7, 4, 'mission_lead', TRUE),
    (7, 5, 'scientist', FALSE),
    (8, 5, 'mission_lead', TRUE),
    (8, 6, 'safety_diver', FALSE),
    (9, 4, 'mission_lead', TRUE),
    (9, 6, 'diver', FALSE),
    (10, 5, 'lead_scientist', TRUE),
    (10, 4, 'coordinator', FALSE),
    (11, 6, 'mapper', TRUE),
    (11, 5, 'safety_diver', FALSE),
    (12, 4, 'mission_lead', TRUE),
    (12, 6, 'diver', FALSE),
    (13, 8, 'lead_scientist', TRUE),
    (13, 9, 'photographer', FALSE),
    (14, 7, 'mission_lead', TRUE),
    (14, 8, 'observer', FALSE),
    (15, 9, 'technician', TRUE),
    (16, 8, 'mission_lead', TRUE),
    (16, 7, 'support_diver', FALSE),
    (17, 7, 'mission_lead', TRUE),
    (17, 9, 'observer', FALSE),
    (18, 8, 'mission_lead', TRUE),
    (18, 9, 'volunteer_lead', FALSE),
    (19, 7, 'mission_lead', TRUE),
    (19, 8, 'scientist', FALSE),
    (20, 2, 'technician', TRUE),
    (20, 1, 'surface_support', FALSE),
    (21, 3, 'lead_diver', TRUE),
    (21, 1, 'surface_support', FALSE),
    (22, 6, 'benthic_recorder', TRUE),
    (22, 5, 'safety_diver', FALSE),
    (23, 9, 'lead_diver', TRUE),
    (23, 7, 'surface_support', FALSE),
    (24, 5, 'mission_lead', TRUE),
    (24, 4, 'coordinator', FALSE);

REFRESH MATERIALIZED VIEW zone_coverage_scores;
