CREATE SCHEMA `DbMysql09` ;

CREATE  TABLE `DbMysql09`.`artists` (
  `artist_id` INT NOT NULL ,
  `artist_name` VARCHAR(100) NOT NULL ,
  `country_name` VARCHAR(50) NULL ,
  PRIMARY KEY (`artist_id`));


CREATE  TABLE `DbMysql09`.`albums` (
  `album_id` INT NOT NULL ,
  `album_name` VARCHAR(100) NOT NULL ,
  `artist_id` INT NULL ,
  `albums_cover` VARCHAR(1024) NULL ,
  `release_year` YEAR NULL ,
  `release_month` TINYINT NULL ,
  `type` ENUM('album','single','remix','EP','compilation','live','soundtrack') NULL ,
  PRIMARY KEY (`album_id`) ,
  INDEX `artist_fk_idx` (`artist_id` ASC) ,
  CONSTRAINT `artist_fk`
  FOREIGN KEY (`artist_id` )
  REFERENCES `DbMysql09`.`artists` (`artist_id` )
  ON DELETE RESTRICT
  ON UPDATE RESTRICT
);

DELIMITER $$

DROP TRIGGER IF EXISTS DbMysql09.albums_BINS$$
USE `DbMysql09`$$
CREATE TRIGGER `albums_BINS` BEFORE INSERT ON albums FOR EACH ROW
-- Edit trigger body code below this line. Do not edit lines above this one
BEGIN
    IF (NEW.release_month < 1 OR NEW.release_month > 12)
			THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'invalid release_month';
    END IF;
END
$$
DELIMITER ;


DELIMITER $$

DROP TRIGGER IF EXISTS DbMysql09.albums_BUPD$$
USE `DbMysql09`$$
CREATE TRIGGER `albums_BUPD` BEFORE UPDATE ON albums FOR EACH ROW
-- Edit trigger body code below this line. Do not edit lines above this one
BEGIN
    IF (NEW.release_month < 1 OR NEW.release_month > 12)
			THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'invalid release_month';
    END IF;
END
$$
DELIMITER ;


CREATE  TABLE `DbMysql09`.`songs` (
  `song_id` INT NOT NULL ,
  `title` VARCHAR(50) NOT NULL ,
  `album_id` INT NULL ,
  `rank` TINYINT NULL ,
  PRIMARY KEY (`song_id`),
  INDEX `albums_fk_idx` (`album_id` ASC) ,
  CONSTRAINT `album_fk`
    FOREIGN KEY (`album_id` )
    REFERENCES `DbMysql09`.`albums` (`album_id` )
    ON DELETE RESTRICT
    ON UPDATE RESTRICT );

DELIMITER $$

DROP TRIGGER IF EXISTS DbMysql09.songs_BINS$$
USE `DbMysql09`$$
CREATE TRIGGER `songs_BINS` BEFORE INSERT ON songs FOR EACH ROW
-- Edit trigger body code below this line. Do not edit lines above this one
BEGIN
    IF (NEW.rank < 1 OR NEW.rank > 100)
			THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'invalid rank';
    END IF;
END
$$
DELIMITER ;


DELIMITER $$

DROP TRIGGER IF EXISTS DbMysql09.songs_BUPD$$
USE `DbMysql09`$$
CREATE TRIGGER `songs_BUPD` BEFORE UPDATE ON songs FOR EACH ROW
-- Edit trigger body code below this line. Do not edit lines above this one
BEGIN
    IF (NEW.rank < 1 OR NEW.rank > 100)
			THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'invalid rank';
    END IF;
END
$$
DELIMITER ;


CREATE  TABLE `DbMysql09`.`performed_by` (
  `song_id` INT NOT NULL ,
  `artist_id` INT NULL ,
  PRIMARY KEY (`song_id`) ,
  INDEX `artists_fk_idx` (`artist_id` ASC) ,
  CONSTRAINT `songs_fk`
    FOREIGN KEY (`song_id`, `artist_id` )
    REFERENCES `DbMysql09`.`songs` (`song_id` )
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT `artists_fk`
    FOREIGN KEY (`artist_id` )
    REFERENCES `DbMysql09`.`artists` (`artist_id` )
    ON DELETE RESTRICT
    ON UPDATE RESTRICT);

# CREATE  TABLE `DbMysql09`.`lyrics` (
#   `song_id` INT NOT NULL ,
#   `lyrics` VARCHAR(2048) NOT NULL ,
#   `lyrics_language` VARCHAR(10) NULL ,
#   `hebrew_translation` VARCHAR(2048) NULL ,
#   PRIMARY KEY (`song_id`) ,
#   FULLTEXT INDEX `fulltext` (`lyrics` ASC) ,
#   CONSTRAINT `songs_lyrics_fk`
#     FOREIGN KEY (`song_id` )
#     REFERENCES `DbMysql09`.`songs` (`song_id` )
#     ON DELETE RESTRICT
#     ON UPDATE RESTRICT);

CREATE TABLE `DbMysql09`.`lyrics` (
  `song_id` INT NOT NULL,
  `lyrics` VARCHAR(2048) NOT NULL,
  `lyrics_language` VARCHAR(10) NULL,
  `hebrew_translation` VARCHAR(2048) NULL,
  PRIMARY KEY (`song_id`),
  FULLTEXT INDEX `lyrics_fulltext` (`lyrics` ASC))
ENGINE = MyISAM;



CREATE  TABLE `DbMysql09`.`popular_songs_by_country` (
  `country_name` VARCHAR(20) NOT NULL ,
  `song_id` INT NOT NULL ,
  `rank` INT NOT NULL ,
  PRIMARY KEY (`country_name`, `rank`) ,
  INDEX `popular_songs_countries_idx` (`song_id` ASC) ,
  CONSTRAINT `popular_songs_countries_fk`
    FOREIGN KEY (`song_id` )
    REFERENCES `DbMysql09`.`songs` (`song_id` )
    ON DELETE RESTRICT
    ON UPDATE RESTRICT);


CREATE  TABLE `DbMysql09`.`users` (
  `nickname` VARCHAR(20) NOT NULL ,
  `email` VARCHAR(50) NOT NULL ,
  `hash_password` VARCHAR(100) NOT NULL ,
  PRIMARY KEY (`nickname`) );

CREATE  TABLE `DbMysql09`.`scores` (
  `nickname` VARCHAR(20) NOT NULL ,
  `date` DATETIME NOT NULL ,
  `game_id` TINYINT NOT NULL ,
  `score` INT NOT NULL ,
  PRIMARY KEY (`nickname`, `date`, `game_id`) ,
  INDEX `scores_users_fk_idx` (`nickname` ASC) ,
  CONSTRAINT `scores_users_fk`
    FOREIGN KEY (`nickname` )
    REFERENCES `DbMysql09`.`users` (`nickname` )
    ON DELETE RESTRICT
    ON UPDATE RESTRICT);

