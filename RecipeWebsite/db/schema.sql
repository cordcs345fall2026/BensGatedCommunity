-- Recipe Box schema: one table.
--
--   mysql --default-character-set=utf8mb4 recipes < db/schema.sql
--
-- is_starter marks the recipes loaded from seed.sql. The site refuses to
-- remove those, so the public Remove button cannot empty the site.

CREATE TABLE IF NOT EXISTS recipes (
  id            INT UNSIGNED      NOT NULL AUTO_INCREMENT,
  title         VARCHAR(200)      NOT NULL,
  description   VARCHAR(500)      NOT NULL,
  category      VARCHAR(50)       NOT NULL,
  prep_minutes  SMALLINT UNSIGNED NOT NULL DEFAULT 0,
  cook_minutes  SMALLINT UNSIGNED NOT NULL DEFAULT 0,
  servings      SMALLINT UNSIGNED NOT NULL DEFAULT 1,
  ingredients   TEXT              NOT NULL,  -- one ingredient per line
  instructions  TEXT              NOT NULL,  -- one step per line
  is_starter    TINYINT(1)        NOT NULL DEFAULT 0,
  created_at    TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
